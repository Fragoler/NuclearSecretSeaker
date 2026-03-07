from patterns import load_patterns_from_json, PATTERNS_FILE
from utils import get_snippet_with_context, deduplicate_results
from logger import log, LogLevel

from pathlib import Path

import os
import re

IGNORED_DIRS = ['.git', 'node_modules', 'vendor', '__pycache__', '.venv']

def find_all_matches_with_positions(line, pattern):
    matches_with_pos = []
    for match in pattern.finditer(line):
        matches_with_pos.append({
            'text': match.group(0),
            'start': match.start(),
            'end': match.end()
        })
    return matches_with_pos


def find_regex(root_dir: str, dict_pattern=None, suppressed_dirs: list = None,
               suppressed_files: list = None, suppressed_matches: list = None, ignored_files: list = None) -> list:
    if dict_pattern is None:
        dict_pattern = load_patterns_from_json(PATTERNS_FILE)

    suppressed_dirs    = [] if suppressed_dirs    is None else suppressed_dirs
    suppressed_files   = [] if suppressed_files   is None else suppressed_files
    suppressed_matches = [] if suppressed_matches is None else suppressed_matches
    ignored_files      = [] if ignored_files      is None else ignored_files
    
    suppressed_dirs = [os.path.join(root_dir, d) for d in suppressed_dirs]
    suppressed_files = [os.path.join(root_dir, f) for f in suppressed_files]
    ignored_files = [os.path.join(root_dir, f) for f in ignored_files]

    log('\n' + "=" * 20, LogLevel.VERBOSE)
    log(f"root dir: {root_dir}", LogLevel.VERBOSE)
    log(f"suppressed dirs:    {suppressed_dirs}",    LogLevel.VERBOSE)
    log(f"suppressed files:   {suppressed_files}",   LogLevel.VERBOSE)
    log(f"suppressed_matches: {suppressed_matches}", LogLevel.VERBOSE)
    log(f"ignored files:      {ignored_files}",      LogLevel.VERBOSE)


    patterns = list(dict_pattern.keys())

    compiled_patterns = [
        (re.compile(p, re.IGNORECASE), dict_pattern[p][0], dict_pattern[p][1])
        for p in patterns
    ]
    compiled_patterns.sort(key=lambda x: x[2], reverse=True)

    results = []

    for root, dirs, files in os.walk(root_dir):
        log("-" * 20, LogLevel.VERBOSE)
        log(f"root:  {root}",  LogLevel.VERBOSE)
        log(f"dirs:  {dirs}",  LogLevel.VERBOSE)
        log(f"files: {files}", LogLevel.VERBOSE)
        
        dirs[:] = [d for d in dirs 
                   if os.path.join(root, d) not in suppressed_dirs 
                   and d not in suppressed_dirs
                   and d not in IGNORED_DIRS]
        files = [f for f in files if str(Path(root) / f) not in ignored_files and f not in ignored_files]
        
        for file in files:
            file_path = Path(root) / file
            file_path_str = str(file_path)
            if file_path_str in suppressed_files or file in suppressed_files:
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
                            m['is_ignored'] = m['text'] in suppressed_matches

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
                log(f'Could not read "{file_path_str}"', LogLevel.ERROR)
                pass

    log("=" * 20 + '\n', LogLevel.VERBOSE)

    results = deduplicate_results(results)

    results.sort(key=lambda x: (-x['level'], x['file'], int(x['line'])))
    return results

