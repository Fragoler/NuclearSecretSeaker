def parse_config(config_path) -> tuple[list[str], list[str], list[str]]:
    ignore_dir_list = []
    ignore_file_list = [config_path]
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

    except FileNotFoundError:
        ignore_file_list = [] # config file doesn't exist, nothing to ignore
    except Exception as e:
        raise

    return ignore_dir_list, ignore_file_list, ignore_matches

