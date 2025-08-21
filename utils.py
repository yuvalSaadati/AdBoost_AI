from typing import List, Dict, Any, Optional
import joblib
from typing import Dict, Any
import re
import os
from typing import List, Dict, Any, Set
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any
from sklearn.tree import DecisionTreeRegressor
import os
import re
import google.generativeai as genai
import time

# Configure Gemini once
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Helper: pick your CTR column robustly


def generate_and_rank_ad(
    title: str,
    description: str,
    rule_path,
    generate_ad_func,
    model_path: str = "saved_models/CTR_ranker.joblib",
    vectorizer_path: str = "saved_models/CTR_ranker_vectorizer.joblib",
    max_attempts: int = 2,
) -> dict:
    """
    Try up to `max_attempts` to generate a new ad and predict its CTR.
    Stops early if y_pred == 1.

    Returns a dict with the best ad, prediction, probability, and attempts.
    """

    CTR_ranker_model = joblib.load(model_path)
    CTR_ranker_vectorizer = joblib.load(vectorizer_path)

    origin_text = f"{title}. {description}".strip()

    best_ad = None
    best_prob = -1.0
    final_pred = None

    for attempt in range(max_attempts):
        # Generate ad
        new_ad = generate_ad_func(title, description, rule_path)

        # Vectorize
        gen_text = f"{new_ad['new_title']}. {new_ad['new_description']}".strip()
        X_origin = CTR_ranker_vectorizer.transform([origin_text])
        X_gen = CTR_ranker_vectorizer.transform([gen_text])
        X_diff = X_gen - X_origin

        # Predict
        y_pred = CTR_ranker_model.predict(X_diff)[0]
        y_prob = float(CTR_ranker_model.predict_proba(X_diff)[:, 1][0])

        # Track best
        if y_prob > best_prob:
            best_ad = new_ad
            best_prob = y_prob
            final_pred = y_pred

        if y_pred == 1:
            break
        print(f'attempt: {attempt}')
        time.sleep(5)
    return {
        "new_title": best_ad["new_title"] if best_ad else None,
        "new_description": best_ad["new_description"] if best_ad else None,
        "prediction": int(final_pred) if final_pred is not None else None,
        "probability_higher_ctr": best_prob if best_prob >= 0 else None,
        "attempts": attempt + 1,
    }


def _pick_ctr_col(df: pd.DataFrame) -> str:
    for c in ["ctr", "CTR", "current_ctr", "click_through_rate"]:
        if c in df.columns:
            return c
    raise ValueError(
        "CTR column not found. Expected one of: ctr, CTR, current_ctr, click_through_rate")

# Helper: convert your string tag columns into numeric features


def _make_feature_matrix(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    X = pd.DataFrame(index=df.index)
    for col in feature_cols:
        if col not in df.columns:
            # missing column → fill with zeros
            X[col] = 0
            continue

        s = df[col]

        # If column is numeric already (e.g., Arousal score), keep as-is
        if pd.api.types.is_numeric_dtype(s):
            X[col] = s.fillna(0).astype(float)
            continue

        # If it’s textual tags like "fast, quick" or "None"
        # Option A: presence (binary)
        presence = s.fillna("").astype(str).str.strip().str.lower().ne(
            "none") & s.fillna("").astype(str).str.strip().ne("")
        X[col] = presence.astype(int)

        # If you prefer counts instead of presence, use this instead:
        # X[col] = s.fillna("").astype(str).str.count(",") + (s.fillna("").astype(str).str.strip().ne("").astype(int))
    return X

# Extract a readable rule string for a given node path


def _rule_string_from_path(tree: DecisionTreeRegressor, feature_names: List[str], node_index: int) -> str:
    t = tree.tree_
    # Backtrack from leaf to root
    path = []
    # Build parents map once
    parents = {0: (-1, None)}  # node_id -> (parent_id, is_left_child)
    stack = [0]
    while stack:
        nid = stack.pop()
        left, right = t.children_left[nid], t.children_right[nid]
        if left != -1:
            parents[left] = (nid, True)
            parents[right] = (nid, False)
            stack.append(left)
            stack.append(right)

    # Walk up
    current = node_index
    while current != 0 and current in parents:
        parent, is_left = parents[current]
        feat_id = t.feature[parent]
        thr = t.threshold[parent]
        feat_name = feature_names[feat_id]
        cond = f"{feat_name} <= {thr:.3f}" if is_left else f"{feat_name} > {thr:.3f}"
        path.append(cond)
        current = parent

    if not path:
        return "(root: no splits)"
    return " AND ".join(reversed(path))


feature_cols = [
    "FeelingBase", "FreeOffers", "Quality", "ProductLineup",
    "Speed", "UserFriendliness", "SocialIdentity",
    "ProductDescription", "Motive", "Curiosity",
    "Personalization",
    "Arousal", "Valence"
]


def train_tree_and_best_path(
    df: pd.DataFrame,
    ctr_col: str = None,
    max_depth: int = 4,
    min_samples_leaf: int = 20,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Train a DecisionTreeRegressor on the provided features to predict CTR.
    Returns the model, feature importances, and the best-leaf rule path.
    """
    if ctr_col is None:
        ctr_col = _pick_ctr_col(df)

    # Build X, y
    X = _make_feature_matrix(df, feature_cols)
    y = df[ctr_col].astype(float)

    # Drop rows with missing y
    mask = y.notna()
    X = X.loc[mask]
    y = y.loc[mask]

    # # Safety: if too small, bail early
    # if len(X) < max(2 * min_samples_leaf, 40):
    #     raise ValueError(
    #         f"Not enough rows to train a stable tree. Have {len(X)}, need at least {max(2 * min_samples_leaf, 40)}.")

    # Fit the tree
    model = DecisionTreeRegressor(
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state
    )
    model.fit(X, y)

    # Find leaf for each sample
    leaf_ids = model.apply(X.values)

    # Compute mean CTR per leaf
    leaf_to_mean: Dict[int, float] = {}
    leaf_to_count: Dict[int, int] = {}
    for leaf, ctr in zip(leaf_ids, y):
        leaf_to_mean.setdefault(leaf, []).append(float(ctr))
        leaf_to_count[leaf] = leaf_to_count.get(leaf, 0) + 1
    leaf_to_mean = {leaf: float(np.mean(vals))
                    for leaf, vals in leaf_to_mean.items()}

    # Best leaf = highest mean CTR
    best_leaf = max(leaf_to_mean.items(), key=lambda kv: kv[1])[0]
    best_mean = leaf_to_mean[best_leaf]
    best_support = leaf_to_count[best_leaf]

    # Rules/path to the best leaf
    rule_path = _rule_string_from_path(model, list(X.columns), best_leaf)

    # Optionally: a human-readable text tree (short)
    # from sklearn.tree import export_text
    # tree_text = export_text(model, feature_names=list(X.columns), max_depth=max_depth)

    result = {
        "model": model,
        "feature_names": list(X.columns),
        "feature_importances": sorted(
            zip(list(X.columns), model.feature_importances_), key=lambda x: x[1], reverse=True
        ),
        "best_leaf_id": int(best_leaf),
        "best_leaf_mean_ctr": float(best_mean),
        "best_leaf_support_n": int(best_support),
        "best_leaf_rule_path": rule_path,
        # "tree_text": tree_text,
    }
    return result

# helpers_tree_gen.py (or put under your existing utils)


# Which feature names are binary presence features in your X matrix
BINARY_FEATURES: Set[str] = {
    "FeelingBase", "FreeOffers", "Quality", "ProductLineup", "Speed",
    "UserFriendliness", "SocialIdentity", "ProductDescription", "Motive",
    "Curiosity", "Personalization"
}
# Numeric features where threshold matters (map for display if you like)
NUMERIC_FEATURES: Set[str] = {"Arousal", "Valence"}


def features_from_rule_path(rule_path: str) -> Dict[str, Any]:
    """
    Parse a path like 'Speed > 0.500 AND FreeOffers > 0.500 AND Valence > -0.500'
    -> {'Speed': True, 'FreeOffers': True, 'Valence': {'op': '>', 'thr': -0.5}}
    We treat <= 0.5 as 'absent' for binary features, and > 0.5 as 'present'.
    """
    out: Dict[str, Any] = {}
    if not rule_path or "no splits" in rule_path:
        return out

    parts = [p.strip() for p in rule_path.split("AND")]
    for p in parts:
        m = re.match(r"^([A-Za-z0-9_]+)\s*(<=|>)\s*([\-]?\d+\.?\d*)$", p)
        if not m:
            continue
        feat, op, thr_s = m.group(1), m.group(2), m.group(3)
        thr = float(thr_s)

        if feat in BINARY_FEATURES:
            if op == ">" and thr >= 0.5:
                out[feat] = True           # require presence
            elif op == "<=" and thr < 0.5:
                out[feat] = False          # require absence (rarely useful)
            else:
                # for odd splits, just record the rule
                out[feat] = {"op": op, "thr": thr}
        elif feat in NUMERIC_FEATURES:
            out[feat] = {"op": op, "thr": thr}
        else:
            out[feat] = {"op": op, "thr": thr}
    return out


def _brief_from_features(req: Dict[str, Any]) -> str:
    """Human-readable constraints for the prompt."""
    bullets = []
    for k, v in req.items():
        if k in BINARY_FEATURES:
            if v is True:
                bullets.append(f"- Include the feature: {k}")
            elif v is False:
                bullets.append(f"- Avoid the feature: {k}")
            else:
                bullets.append(f"- Respect rule: {k} {v['op']} {v['thr']:.2f}")
        elif k in NUMERIC_FEATURES:
            bullets.append(f"- Aim for {k} {v['op']} {v['thr']:.2f}")
        else:
            bullets.append(f"- Rule: {k} {v['op']} {v['thr']:.2f}")
    return "\n".join(bullets)

# dspy_data_loader.py


# Features you use as binary presence (for interpreting the rule path)
BINARY_FEATURES = {
    "FeelingBase", "FreeOffers", "Quality", "ProductLineup", "Speed",
    "UserFriendliness", "SocialIdentity", "ProductDescription", "Motive",
    "Curiosity", "Personalization"
}
NUMERIC_FEATURES = {"Arousal", "Valence"}


def _features_from_rule_path(rule_path: str) -> Dict[str, Any]:
    """
    Parse a path like 'Speed > 0.500 AND FreeOffers > 0.500 AND Valence > -0.500'
    -> {'Speed': True, 'FreeOffers': True, 'Valence': {'op': '>', 'thr': -0.5}}
    """
    out: Dict[str, Any] = {}
    if not rule_path or "no splits" in rule_path:
        return out

    parts = [p.strip() for p in rule_path.split("AND")]
    for p in parts:
        m = re.match(r"^([A-Za-z0-9_]+)\s*(<=|>)\s*([\-]?\d+\.?\d*)$", p)
        if not m:
            continue
        feat, op, thr_s = m.group(1), m.group(2), m.group(3)
        thr = float(thr_s)

        if feat in BINARY_FEATURES:
            # Treat > 0.5 as "present", <= 0.5 as "absent"
            if op == ">" and thr >= 0.5:
                out[feat] = True
            elif op == "<=" and thr < 0.5:
                out[feat] = False
            else:
                out[feat] = {"op": op, "thr": thr}
        elif feat in NUMERIC_FEATURES:
            out[feat] = {"op": op, "thr": thr}
        else:
            out[feat] = {"op": op, "thr": thr}
    return out


def _pick(df: pd.DataFrame, name: str) -> Optional[str]:
    """Case-insensitive column finder."""
    name_l = name.lower()
    for c in df.columns:
        if c.lower() == name_l:
            return c
    return None


def load_train_examples_from_excel(
    path: str,
    use_rule_path_to_constraints: bool = True,
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Reads 'regenerate ads.xlsx' and returns a list of training examples for DSPy.
    Expected columns:
      - Headline 1, Headline 2, Headline 3
      - Description 1, Description 2, Description 3
      - New Decision Path  (rule path or constraints)
    """
    df = pd.read_excel(path)

    h1 = _pick(df, "Headline 1")
    h2 = _pick(df, "Headline 2")
    h3 = _pick(df, "Headline 3")
    d1 = _pick(df, "Description 1")
    d2 = _pick(df, "Description 2")
    d3 = _pick(df, "Description 3")
    cp = _pick(df, "New Decision Path") or _pick(
        df, "Constraints") or _pick(df, "Decision Path")

    examples: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        headlines = []
        for col in [h1, h2, h3]:
            if col and pd.notna(row[col]):
                val = str(row[col]).strip()
                if val:
                    headlines.append(val)

        descs = []
        for col in [d1, d2, d3]:
            if col and pd.notna(row[col]):
                val = str(row[col]).strip()
                if val:
                    descs.append(val)

        # Title: combine non-empty headlines into one line
        title = " | ".join(headlines) if headlines else ""
        # Description: combine descriptions into one sentence-ish block
        description = " ".join(descs) if descs else ""

        # Constraints
        raw_path = ""
        if cp and pd.notna(row[cp]):
            raw_path = str(row[cp]).strip()

        if use_rule_path_to_constraints and raw_path:
            feats = _features_from_rule_path(raw_path)
            constraints = _brief_from_features(feats) if feats else raw_path
        else:
            constraints = raw_path  # assume already a human-written constraints block

        # Skip empty rows
        if not title and not description:
            continue

        examples.append({
            "title": title,
            "description": description,
            "constraints": constraints,
            "rewritten": None  # no gold; DSPy will optimize via your metric
        })

        if limit and len(examples) >= limit:
            break

    return examples


def generate_ad_with_gemini(title: str, description: str, rule_path: Dict[str, Any]) -> dict:
    """
    Generate ad copy using Google Gemini
    Returns {'new_title': ..., 'new_description': ...}
    """

    model = genai.GenerativeModel(
        "gemini-1.5-flash")  # or gemini-1.5-pro for better quality
    feature_requirements = features_from_rule_path(rule_path)
    brief = _brief_from_features(feature_requirements)
    prompt = (
        "You are an expert ad copywriter. "
        "Rewrite the product title and description into a short ad with high CTR. "
        "Strictly follow the constraints.\n\n"
        f"Original Title: {title}\n"
        f"Original Description: {description}\n\n"
        f"Constraints:\n{brief}\n\n"
        "Return exactly this format:\n"
        "Title: <new one line>\n"
        "Description: <new one sentence>\n"
        "No emojis. No hashtags."
    )

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Parse the output
    m = re.search(r"Title:\s*(.+?)\s*Description:\s*(.+)", text, re.I | re.S)
    if m:
        return {
            "new_title": m.group(1).strip(),
            "new_description": m.group(2).strip()
        }
    else:
        # fallback
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        if len(lines) >= 2:
            return {"new_title": lines[0], "new_description": " ".join(lines[1:])}
        return {"new_title": title + " (Improved)", "new_description": description}
