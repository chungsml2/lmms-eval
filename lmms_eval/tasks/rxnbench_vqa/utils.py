import os
import re
from pathlib import Path
import yaml
from PIL import Image

hf_home = os.getenv("HF_HOME", "~/.cache/huggingface/")
base_cache_dir = os.path.expanduser(hf_home)

def _load_cache_name(yaml_filename):
    yaml_path = Path(__file__).parent / yaml_filename
    if not yaml_path.exists():
        return ""
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            lines = [line for line in f if "!function" not in line]
            config = yaml.safe_load("".join(lines))
            return config.get("dataset_kwargs", {}).get("cache_dir", "")
    except Exception:
        return ""

cache_name = _load_cache_name("rxnbench_vqa_en.yaml") or ""

def rxnbench_doc_to_visual(doc):
    image = doc["image"]
    
    if cache_name:
        full_path = os.path.join(base_cache_dir, cache_name, image)
        if os.path.exists(full_path):
            return [full_path]
    return [image]

def rxnbench_doc_to_text(doc, lmms_eval_specific_kwargs=None):
    if lmms_eval_specific_kwargs is None:
        lmms_eval_specific_kwargs = {}

    choices = doc["choices"]
    while len(choices) < 4:
        choices.append("")
    choices = choices[:4]
    options = ["A", "B", "C", "D"]
    choices_str = "\n".join(f"{opt}. {choice}" for opt, choice in zip(options, choices))
    
    default_post = "\nBased on the image and the question, choose the most appropriate answer.\n**Only output a single letter (A, B, C, or D)**. Do NOT output any other text or explanation."
    
    pre = lmms_eval_specific_kwargs.get("pre_prompt", "")
    post = lmms_eval_specific_kwargs.get("post_prompt", default_post)
    
    return f"{pre}Question: {doc['question']}\nChoices:\n{choices_str}{post}"

def _get_target(doc):
    return ["A", "B", "C", "D"][int(doc["answer"])]


# [ADDED]
# Processing \boxed format output
_BOXED_RE = re.compile(r"\\boxed\{\s*\(?([A-Da-d])\)?")
_LETTER_RE = re.compile(r"\b([A-D])\b")

# [ADDED]
def _extract_choice(pred):
    boxed = _BOXED_RE.findall(pred)
    if boxed:
        return boxed[-1].lower()
    match = _LETTER_RE.search(pred)
    return match.group(1).lower() if match else ""

def rxnbench_process_results(doc, results):
    raw_pred = results[0] if results else ""

    pred = raw_pred.strip()
    target = _get_target(doc).strip().lower()
    
    score = 0.0

    if pred.lower() == target:
        score = 1.0
    else:
        # [ADDED]
        if _extract_choice(pred) == target:
            score = 1.0
        
    prompt_text = rxnbench_doc_to_text(doc)
    
    return {
        "exact_match": score,
        "raw_output": raw_pred,
        "question": prompt_text
    }

