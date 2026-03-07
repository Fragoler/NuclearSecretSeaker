from resources import resource_path
from pathlib import Path

import json


PATTERNS_FILE = "patterns.json"


def load_patterns_from_json(json_path=None) -> dict:
    dict_pattern = {}
    if json_path is None:
        json_path = PATTERNS_FILE

    with open(resource_path(json_path), 'r', encoding='utf-8') as f:
        data = json.load(f)

    for entry in data.get('patterns', []):
        name = entry.get('name', 'Unknown')
        regex = entry.get('regex', '')
        priority = entry.get('priority', 100)
        recommendation = entry.get('recommendation', '')

        if regex:
            dict_pattern[regex] = (name, priority, recommendation)

    return dict_pattern

