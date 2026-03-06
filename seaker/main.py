import sys
import re
import os
from pathlib import Path
import json

PATTERNS_FILE = Path(__file__).parent / "patterns.json"


def load_patterns_from_json(json_path):
    """
    Load secret patterns from JSON file.
    
    JSON format:
    {
        "patterns": [
            {"name": "Pattern Name", "regex": "regex_here", "priority": 200},
            ...
        ]
    }
    
    Returns:
        dict: {regex_pattern: (description, priority)}
    """
    dict_pattern = {}
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for entry in data.get('patterns', []):
        name = entry.get('name', 'Unknown')
        regex = entry.get('regex', '')
        priority = entry.get('priority', 100)
        
        if regex:
            dict_pattern[regex] = (name, priority)
    
    return dict_pattern


dict_pattern = load_patterns_from_json(PATTERNS_FILE)

patterns = list(dict_pattern.keys())

def print_help():
    help_text = """
        Usage: program [options]

        Options:
          -h, --help        See this message
          -i DIR, --input DIR  Pick root directory (default: .)
    """
    print(help_text)


def get_snippet_with_context(line, match, context_chars=40):
    """
    Extract snippet with context around the match.
    Includes characters before and after the match for better context.
    """
    match_start = line.find(match)
    if match_start == -1:
        return match
    
    start = max(0, match_start - context_chars)
    end = min(len(line), match_start + len(match) + context_chars)
    
    snippet = line[start:end].rstrip('\n\r')
    
    if start > 0:
        snippet = "..." + snippet
    if end < len(line):
        snippet = snippet + "..."
    
    return snippet.strip()


def deduplicate_results(results):
    """
    Deduplicate results by keeping highest-priority matches per line.
    For each file+line combination, keeps only the highest-priority secret.
    """
    grouped = {}
    for r in results:
        key = (r["file"], r["line"])
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(r)

    deduplicated = []
    for key, matches in grouped.items():
        matches.sort(key=lambda x: x["level"], reverse=True)
        
        if matches:
            deduplicated.append(matches[0])

    return deduplicated


def main():
    argc = len(sys.argv)
    root_dir = "."
    if argc == 1:
        pass
    else:
        i = 1
        while i < argc:
            if sys.argv[i] in ['-h', '--help']:
                print_help()
                return
            elif sys.argv[i] in ['-i', '--input']:
                if i + 1 < argc:
                    root_dir = sys.argv[i + 1]
                    i += 2
                else:
                    print("DIR expected after -i (--input) option")
                    print_help()
                    return
            else:
                print(f"Unknown option: {sys.argv[i]}")
                print_help()
                return

    compiled_patterns = [
        (re.compile(p, re.IGNORECASE), dict_pattern[p][0], dict_pattern[p][1])
        for p in patterns
    ]
    compiled_patterns.sort(key=lambda x: x[2], reverse=True)
    
    results = []

    for root, dirs, files in os.walk(root_dir):
        for file in files:
            file_path = Path(root) / file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for pattern, description, level in compiled_patterns:
                            matches = pattern.findall(line)
                            if matches:
                                for match in set(matches):
                                    snippet = get_snippet_with_context(line, match)
                                    result = {
                                        "file": str(file_path),
                                        "line": str(line_num),
                                        "description": description,
                                        "snippet": snippet,
                                        "secret": match,
                                        "level": level
                                    }
                                    results.append(result)

            except Exception as e:
                pass

    results = deduplicate_results(results)
    
    results.sort(key=lambda x: (-x["level"], x["file"], int(x["line"])))

    print(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    main()
