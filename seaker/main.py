import sys
import re
import os
from pathlib import Path
import json


PATTERNS_FILE = Path(__file__).parent / "patterns.json"

DEFAULT_CONFIG_PATH = ".nuclearss"
DEFAULT_ROOT_DIR = "."

def load_patterns_from_json(json_path):
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


def get_snippet_with_context(line, match, context_chars=40):
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


def print_help():
    help_text = f"""
        Usage: program [options]

        Options:
          -h, --help               See this message
          -i DIR, --input DIR      Pick root directory (default: {DEFAULT_ROOT_DIR})
          -c FILE, --config FILE   Specify config file (default: {DEFAULT_CONFIG_PATH})
          -x DIR, --ignore DIR     Ignore directory
          -x FILE, --ignore FILE   Ignore file
          -x FILE1 -x FILE2 -x DIR The way to ignore multiple dirs/files
    """
    print(help_text)

def parse_config(config_path):
    ignore_dir_list = []
    ignore_file_list = []
    ignore_matches = []
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('dir:'):
                    dir_path = line[4:].strip()
                    if dir_path:
                        ignore_dir_list.append(dir_path)
                        
                elif line.startswith('file:'):
                    file_path = line[5:].strip()
                    if file_path:
                        ignore_file_list.append(file_path)
                        
                elif line.startswith('text:'):
                    text = line[5:].strip()
                    if text:
                        ignore_matches.append(text)
                        
                else:
                    print(f"Warning, unknown format in config on line {line_num}: {line}")
                    
    except FileNotFoundError:
        if config_path == DEFAULT_CONFIG_PATH:
            open(config_path, 'w').close()
            print(f"Config file not found, default one was created at {DEFAULT_CONFIG_PATH}")
        else:
            print(f"Config file {config_path} not found. Try creating config on default path .nuclearss or specify it with -c (--config) option")
    except Exception as e:
        print(f"Unknown error {e}")
    
    return ignore_dir_list, ignore_file_list, ignore_matches

def find_regex(root_dir: str = DEFAULT_ROOT_DIR, ignore_dir_list: list = [], ignore_file_list: list = [], ignore_matches: list = []):
    compiled_patterns = [
        (re.compile(p, re.IGNORECASE), dict_pattern[p][0], dict_pattern[p][1])
        for p in patterns
    ]
    compiled_patterns.sort(key=lambda x: x[2], reverse=True)
    
    results = []

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_dir_list and d not in ignore_dir_list]
        for file in files:
            file_path = Path(root) / file
            file_path_str = str(file_path)
            if file_path_str in ignore_file_list or file in ignore_file_list:
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        for pattern, description, level in compiled_patterns:
                            matches = pattern.findall(line)
                            if matches:
                                for match in set(matches):
                                    if match in ignore_matches: continue
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
                print(f"Could not read \"{file_path_str}\"")
                pass

    results = deduplicate_results(results)
    
    results.sort(key=lambda x: (-x["level"], x["file"], int(x["line"])))

    print(json.dumps(results, indent=4, ensure_ascii=False))
    
def main():
    argc = len(sys.argv)
    root_dir = "."
    config_path = DEFAULT_CONFIG_PATH
    ignore_list = []
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
                    print("DIR expected after -i (--input) option)")
                    return
            elif sys.argv[i] in ['-x', '--ignore']:
                if i + 1 < argc:
                    ignore_list.append(sys.argv[i + 1])
                    i += 2
                else:
                    print("DIR or FILE expected after -x (--ignore) option")
                    return
            elif sys.argv[i] in ['-c', '--config']:
                if i + 1 < argc:
                    config_path = sys.argv[i + 1]
                    i += 2
                else:
                    print("FILE expected after -c (--config) option")
            else:
                print(f"Unknown option: {sys.argv[i]}")
                return
    dirs, files, matches = parse_config(config_path)
    find_regex(root_dir, dirs, files, matches)
    

if __name__ == '__main__':
    main()
