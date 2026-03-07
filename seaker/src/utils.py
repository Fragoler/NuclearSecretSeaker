def get_snippet_with_context(line: str, match: str, context_chars: int=40) -> str:
    match_start = line.find(match)
    if match_start == -1:
        return match

    start = max(0, match_start - context_chars)
    end = min(len(line), match_start + len(match) + context_chars)

    snippet = line[start:end].rstrip('\n\r').strip()

    if start > 0:
        snippet = "..." + snippet
    if end < len(line):
        snippet = snippet + "..."

    return snippet


def deduplicate_results(results: list[dict[str, str]]) -> list[dict[str, str]]:
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

