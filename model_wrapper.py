import re
from transformers import pipeline
import os
import os
import re
from typing import List, Dict


tagger = pipeline("text-generation", model="distilgpt2")

# ---------- Fallback keyword lists / patterns per feature ----------
FEATURE_KEYWORDS: Dict[str, List[str]] = {
    "Feeling base": [
        r"\btrust(ed|worthy)?\b", r"\bofficial\b", r"\bapproved\b",
        r"\bclinically (?:proven|tested)\b", r"\bscientifically (?:backed|proven|validated)\b",
        r"\bdoctor-?recommended\b", r"\bauthorized\b", r"\bverified\b"
    ],
    "Free Offers": [
        r"\bfree\b", r"\bno\s*charge\b", r"\bcomplimentary\b", r"\bgratis\b",
        r"\bdiscount(s)?\b", r"\bsale\b", r"\b% ?off\b", r"\bpromo( code)?\b",
        r"\bfree shipping\b", r"\bzero fees?\b"
    ],
    "Quality": [
        r"\bpremium\b", r"\btop[- ]?quality\b", r"\bhigh[- ]grade\b", r"\bsuperior\b",
        r"\bbest[- ]in[- ]class\b", r"\bstate[- ]of[- ]the[- ]art\b",
        r"\bscientifically (?:validated|proven)\b", r"\bdurable\b", r"\breliable\b"
    ],
    "Product Lineup": [
        r"\bwide (?:range|selection)\b", r"\blarge selection\b", r"\bextensive range\b",
        r"\bvariety of\b", r"\bone of (?:the )?largest\b", r"\bfull catalog(?:ue)?\b",
        r"\bmultiple options\b", r"\bcomplete lineup\b"
    ],
    "Speed": [
        r"\bfast\b", r"\bquick\b", r"\bimmediate\b", r"\bspeedy\b", r"\binstant\b",
        r"\brapid\b", r"\bshort (?:time|wait|setup)\b", r"\bminutes?\b"
    ],
    "User Friendliness": [
        r"\beasy to use\b", r"\buser[- ]?friendly\b", r"\bsimple\b", r"\bintuitive\b",
        r"\bno hassle\b", r"\bconvenient\b", r"\bquick setup\b", r"\bplug[- ]and[- ]play\b"
    ],
    "Social Identity": [
        r"\bjoin (?:us|our community)\b", r"\bcommunity\b", r"\btogether\b",
        r"\bfor (?:parents|students|gamers|creators|developers)\b",
        r"\bmembers?\b", r"\bshare(d)? experience(s)?\b", r"\bbelong(?:ing)?\b"
    ],
    "Product Description": [
        # nouns + verbs about what it is/does; keep broad
        r"\b(app|tool|platform|service|course|guide|software|device|supplement|program)\b",
        r"\b(builds?|creates?|tracks?|manages?|analyzes?|optimizes?|protects?)\b"
    ],
    "Motive": [
        r"\block(?:ing)? for help\b", r"\bproblem\b", r"\bfix\b", r"\bsolve\b",
        r"\bstruggl\w*\b", r"\bpain point\b", r"\blimited time\b", r"\burgent\b",
        r"\bdeadline\b", r"\bseason(al)?\b", r"\bweather\b", r"\bsale\b", r"\bdiscount\b"
    ],
    "Curiosity": [
        r"\bsecret\b", r"\bhidden\b", r"\bunknown\b", r"\bdiscover\b", r"\bfind out\b",
        r"\bwhat happens if\b", r"\byou won't believe\b", r"\bguess\b", r"\bteaser\b",
        r"\bcoming soon\b", r"\bstay tuned\b"
    ],
}


def _extract_keywords_fallback(text: str, feature_type: str) -> str:
    """Regex scan for the given feature_type; return comma-separated matches or 'None'."""
    text_l = text.lower()
    patterns = FEATURE_KEYWORDS.get(feature_type, [])
    found: List[str] = []
    for pat in patterns:
        for m in re.findall(pat, text_l, flags=re.IGNORECASE):
            # handle regex groups returning tuples
            match_str = m if isinstance(
                m, str) else next((g for g in m if g), "")
            if match_str:
                found.append(match_str if isinstance(
                    match_str, str) else str(match_str))
        # also try to capture the literal pattern if group returns empty
        if not found:
            if re.search(pat, text_l, flags=re.IGNORECASE):
                # take a readable version of the pattern (rough)
                literal = re.sub(
                    r"\\b|\\s\*|\?:|\(|\)|\?|\\w\*|\[\^?\w+\]", "", pat)
                if literal:
                    found.append(literal.strip())
    # normalize & unique
    cleaned = [w.strip().lower() for w in found if w and isinstance(w, str)]
    cleaned = sorted(set(cleaned))
    return ", ".join(cleaned) if cleaned else "None"


# ---------- OpenAI path (optional) ----------
_openai_client = None
try:
    from openai import OpenAI
    if os.getenv("OPENAI_API_KEY"):
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    _openai_client = None


def run_model(system_prompt: str, user_prompt: str, ad: str, feature_type: str) -> str:
    """
    Try OpenAI first (if OPENAI_API_KEY is set), else fall back to keyword/regex for the given feature_type.
    Returns a comma-separated string or 'None'.
    """
    # # --- OpenAI path ---
    # if _openai_client.api_key != 'None':
    #     try:
    #         # Keep output strict: keywords/short phrases only
    #         response = _openai_client.chat.completions.create(
    #             model="gpt-4o-mini",
    #             temperature=0,
    #             max_tokens=120,
    #             messages=[
    #                 {"role": "system", "content": system_prompt},
    #                 {"role": "user", "content": f"{user_prompt}{ad}\n\nOnly return keywords/short phrases separated by comma. If none, return 'None'."}
    #             ],
    #         )
    #         out = response.choices[0].message.content.strip()
    #         # normalize tiny mistakes (ensure comma-separated)
    #         if not out:
    #             return "None"
    #         # Some models add leading bullets/newlines—clean them:
    #         out = re.sub(r"^[\-\•\s]+", "", out, flags=re.MULTILINE)
    #         return out
    #     except Exception as e:
    #         # fall back silently
    #         print(
    #             f"[run_model] OpenAI failed; falling back to keywords. Reason: {e}")

    # --- Fallback path: keyword/regex by feature_type ---
    return _extract_keywords_fallback(ad, feature_type)
