import sys
import re
import os
from pathlib import Path
import json

mail_regex = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
phone_regex = r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?\d{3}[\- ]?\d{2}[\- ]?\d{2}$'
ipv4_regex = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
ipv6_regex = r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'
mac_regex = r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b'
cidr_regex = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:3[0-2]|[12]?[0-9])\b'
patterns = [mail_regex, phone_regex, ipv4_regex, ipv6_regex, mac_regex, cidr_regex]

dict_pattern = {
    mail_regex: ('mail', 135),
    phone_regex: ('phone', 170),
    ipv4_regex: ('ipv4', 200),
    ipv6_regex: ('ipv6', 70),
    mac_regex: ('mac', 90),
    cidr_regex: ('cidr', 120)
}

def print_help():
    help_text = """
        Usage: program [options]

        Options:
          -h, --help               See this message
          -i DIR, --input DIR      Pick root directory (default: .)
          -x DIR, --ignore DIR     Ignore directory
          -x FILE, --ignore FILE   Ignore file
          -x FILE1 -x FILE2 -x DIR The way to ignore multiple dirs/files
    """
    print(help_text)

def find_regex(root_dir: str, ignore_list: list):
    compiled_patterns = [(re.compile(p, re.IGNORECASE), dict_pattern[p][0], dict_pattern[p][1]) for p in patterns]
    results = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_list and d not in ignore_list]
        for file in files:
            file_path = Path(root) / file
            file_path_str = str(file_path)
            if file_path_str in ignore_list or file in ignore_list:
                continue
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                    for line_num, line in enumerate(lines, 1):
                        for pattern, description, level in compiled_patterns:
                            matches = pattern.findall(line)
                            if matches:
                                for match in set(matches):
                                    result = {
                                        "file": str(file_path_str),
                                        "line": str(line_num),
                                        "description": description,
                                        "snippet": match,
                                        "level": level
                                    }
                                    results.append(result)
                                    
            except Exception as e:
                pass
    
    print(json.dumps(results, indent=4, ensure_ascii=False))

def main():
    argc = len(sys.argv)
    root_dir = "."
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
            else:
                print(f"Unknown option: {sys.argv[i]}")
                return
    find_regex(root_dir, ignore_list)
    

if __name__ == '__main__':
    main()
