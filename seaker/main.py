import sys
import re
import os
from pathlib import Path

mail_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
phone_regex = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
ipv4_regex = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
ipv6_regex = r'\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b|\b(?:[A-Fa-f0-9]{1,4}:){1,7}:|\b::(?:[A-Fa-f0-9]{1,4}:){0,6}[A-Fa-f0-9]{1,4}\b'
mac_regex = r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b'
cidr_regex = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(?:3[0-2]|[12]?[0-9])\b'
patterns = [mail_regex, phone_regex, ipv4_regex, ipv6_regex, mac_regex, cidr_regex]

def main():
    argc = len(sys.argv)
    root_dir = ".."
    compiled_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            try:
                file_path = Path(root) / file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                    for i, pattern in enumerate(compiled_patterns):
                        matches = pattern.findall(content)
                        if matches:
                            print(f"\n {file_path}")
                            print(f"  Паттерн {i}: {patterns[i][:50]}...")
                            print(f"  Найдено: {len(set(matches))} уникальных")
                            print(f"  Примеры: {list(set(matches))}")
                            
            except Exception as e:
                print(f"Ошибка чтения {file_path}: {e}")

if __name__ == '__main__':
    main()
