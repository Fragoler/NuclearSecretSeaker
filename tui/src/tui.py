from ignore import ignore_text, ignore_file

# ── ANSI helpers ────────────────────────────────────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

RED    = "\033[38;2;220;50;50m"
YELLOW = "\033[38;2;230;180;0m"
GREEN  = "\033[38;2;60;200;80m"
CYAN   = "\033[38;2;80;200;220m"
GRAY   = "\033[38;2;140;140;140m"
WHITE  = "\033[38;2;220;220;220m"


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def _level_color(level: int) -> str:
    t = level / 255.0
    if t < 0.5:
        r, g = int(255 * t * 2), 200
    else:
        r, g = 255, int(200 * (1 - (t - 0.5) * 2))
    return _rgb(r, g, 0)


def _level_label(level: int) -> str:
    if level < 85:
        return f"{GREEN}LOW{RESET}"
    elif level < 170:
        return f"{YELLOW}MEDIUM{RESET}"
    else:
        return f"{RED}HIGH{RESET}"


def _bar(level: int, lc: str, width: int = 18) -> str:
    filled = level * width // 255
    empty  = width - filled
    return f"{lc}{'█' * filled}{GRAY}{'░' * empty}{RESET}"


def _div(char="─", color=GRAY):
    return f"{color}{char * 60}{RESET}"


# ── Main TUI ────────────────────────────────────────────────────────────────

def tui(data: list[dict], ignored: dict, config_file: str) -> int:
    total   = len(data)
    skipped = 0

    for idx, item in enumerate(data, 1):
        file_path   = item.get("file", "")
        description = item.get("description", "")
        snippet     = item.get("snippet", "")
        secret      = item.get("secret", "")
        level       = item.get("level", 0)

        if not file_path or not description or level is None:
            continue

        lc    = _level_color(level)
        label = _level_label(level)

        # ── Header ──────────────────────────────────────────────────────────
        print()
        print(_div("─"))
        print(f"  {BOLD}{WHITE}Secret detected{RESET}  {GRAY}[{idx}/{total}]{RESET}")
        print(_div("─"))
        print(f"  {CYAN}File :{RESET} {file_path}")
        print(f"  {CYAN}Type :{RESET} {description}")
        print(f"  {CYAN}Risk :{RESET} {label}  {_bar(level, lc)}")
        print(_div("·"))

        # ── Snippet ─────────────────────────────────────────────────────────
        for line in snippet.splitlines():
            highlighted = line.replace(secret, f"{lc}{BOLD}{secret}{RESET}")
            print(f"  {DIM}{highlighted}{RESET}")

        print(_div("·"))

        # ── Prompt ──────────────────────────────────────────────────────────
        colored_secret = f"{lc}\"{secret}\"{RESET}"
        print(f"  Ignore {colored_secret}?")
        print(f"  {GREEN}[y]{RESET} this secret  "
              f"{YELLOW}[f]{RESET} whole file  "
              f"{RED}[N]{RESET} block commit  "
              f"{GRAY}[?]{RESET} help")
        print()

        while True:
            print(f"  {GRAY}›{RESET} ", end="", flush=True)
            action = input("").strip().lower()

            if action == "y":
                ignore_text(secret, config_file)
                print(f"  {GREEN}✔{RESET}  Secret added to ignore list.\n")
                break

            elif action == "f":
                ignore_file(file_path, config_file, force=True)
                print(f"  {YELLOW}✔{RESET}  File added to ignore list.\n")
                break

            elif action == "?":
                print(f"\n  {BOLD}Options:{RESET}")
                print(f"    {GREEN}y{RESET}         — ignore this specific secret value")
                print(f"    {YELLOW}f{RESET}         — ignore the entire file")
                print(f"    {RED}N{RESET} / Enter — block the commit and exit")
                print(f"    {GRAY}?{RESET}         — show this help\n")

            else:
                skipped += 1
                return 1

    # ── Summary ─────────────────────────────────────────────────────────────
    ignored_dirs  = ignored.get('directories', [])
    ignored_files = ignored.get('files', [])
    ignored_texts = ignored.get('texts', [])

    print()
    print(_div("═"))
    print(f"  {BOLD}{WHITE}Scan complete{RESET}")
    print(_div("─"))
    print(f"  {CYAN}Findings   :{RESET}  {total}")
    print(f"  {GREEN}Ignored    :{RESET}  {total - skipped}")
    if skipped:
        print(f"  {RED}Unresolved :{RESET}  {skipped}")

    def _list_section(title, items):
        print()
        print(f"  {BOLD}{title}{RESET}")
        if items:
            for entry in items:
                print(f"    {GRAY}·{RESET} {entry}")
        else:
            print(f"    {DIM}(none){RESET}")

    _list_section("Ignored directories:", ignored_dirs)
    _list_section("Ignored files:",       ignored_files)
    _list_section("Ignored secrets:",     ignored_texts)
    print()
    print(_div("═"))
    print()

    return 0


def add_to_ignore(file_path):
    pass  # Placeholder
