import sys
import re
import os
from pathlib import Path
import json


PATTERNS_FILE = Path(__file__).parent / "patterns.json"

DEFAULT_CONFIG_PATH = ".nuclearss"
DEFAULT_ROOT_DIR = "."

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_patterns_from_json(json_path):
    dict_pattern = {}
    
    with open(resource_path(json_path), 'r', encoding='utf-8') as f:
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


def find_all_matches_with_positions(line, pattern):
    """Find all matches with their start/end positions in the line."""
    matches_with_pos = []
    for match in pattern.finditer(line):
        matches_with_pos.append({
            'text': match.group(0),
            'start': match.start(),
            'end': match.end()
        })
    return matches_with_pos


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
                        # Step 1: Collect ALL matches from ALL patterns with positions
                        all_matches = []
                        for idx, (pattern, description, level) in enumerate(compiled_patterns):
                            matches = find_all_matches_with_positions(line, pattern)
                            for m in matches:
                                all_matches.append({
                                    'priority_idx': idx,
                                    'level': level,
                                    'description': description,
                                    'text': m['text'],
                                    'start': m['start'],
                                    'end': m['end']
                                })

                        # Step 2: Mark matches that are directly ignored
                        for m in all_matches:
                            m['is_ignored'] = m['text'] in ignore_matches

                        # Step 3: For each match, determine if it should be shown
                        for current in all_matches:
                            if current['is_ignored']:
                                current['show'] = False
                                continue

                            should_show = True

                            # Check against all other matches
                            for other in all_matches:
                                if other is current:
                                    continue

                                # If other is higher priority (lower idx)
                                if other['priority_idx'] < current['priority_idx']:
                                    # If other is NOT ignored and contains current, hide current
                                    if not other['is_ignored'] and \
                                       other['start'] <= current['start'] and \
                                       other['end'] >= current['end']:
                                        should_show = False
                                        break

                                    # If other IS ignored and current contains other, hide current
                                    # (e.g., Bearer contains ignored JWT)
                                    if other['is_ignored'] and \
                                       current['start'] <= other['start'] and \
                                       current['end'] >= other['end']:
                                        should_show = False
                                        break

                            current['show'] = should_show

                        # Step 4: Collect results for matches that should be shown
                        for m in all_matches:
                            if m['show']:
                                results.append({
                                    'file': str(file_path),
                                    'line': str(line_num),
                                    'description': m['description'],
                                    'snippet': get_snippet_with_context(line, m['text']),
                                    'secret': m['text'],
                                    'level': m['level']
                                })

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
