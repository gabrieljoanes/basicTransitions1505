# utils/io.py

import json

def load_transitions(file_path="transitions.json"):
    """
    Loads only the 'transition' strings from the JSON list of objects.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["transition"] for item in data if "transition" in item]
