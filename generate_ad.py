import re
import dspy
from transformers import pipeline
from utils import *
from utils import _brief_from_features
import joblib
from dspy.teleprompt import BootstrapFewShotWithRandomSearch

# Use a local instruction model to optimize the prompt cheaply
lm = dspy.LM("gemini/gemini-1.5-flash", api_key=os.getenv("GOOGLE_API_KEY"))
dspy.configure(lm=lm)


# 2) Define the task signature with InputField / OutputField
class AdRewrite(dspy.Signature):
    """Rewrite an ad with constraints and return Title/Description in a strict format."""
    title = dspy.InputField(desc="Original product title (short)")
    description = dspy.InputField(
        desc="Original product description (one sentence)")
    constraints = dspy.InputField(desc="Bullet list of constraints to follow")
    rewritten = dspy.OutputField(
        desc="Format: 'Title: ...\\nDescription: ...'")

# 3) Make a Module that uses the signature


class AdRewriter(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predict = dspy.Predict(AdRewrite)

    def forward(self, title: str, description: str, constraints: str):
        # You can add guardrails here if needed, but DSPy handles prompting.
        return self.predict(title=title, description=description, constraints=constraints)


train_examples = load_train_examples_from_excel(
    path="data/regenerate ads.xlsx",
    # set False if the sheet already has human-written constraints
    use_rule_path_to_constraints=True,
    limit=None                          # or an int, e.g. 50
)


def parse_title_description(text: str):
    m = re.search(r"Title:\s*(.+?)\s*Description:\s*(.+)\s*$",
                  text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # fallback
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) >= 2:
        return lines[0], " ".join(lines[1:])
    if len(lines) == 1:
        return lines[0], lines[0]
    return None, None


constraints = "- Include Speed\n- Include FreeOffers\n- Avoid jargon"
rewriter = AdRewriter()
pred = rewriter(
    title="Budget Running Shoes",
    description="Comfortable shoes for daily jogs.",
    constraints=constraints
)

out = pred.rewritten or ""
new_title, new_desc = parse_title_description(out)
print("RAW OUTPUT:\n", out, "\n")
print("PARSED:\n", new_title, "\n", new_desc)
