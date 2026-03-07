#!/usr/bin/env sh

output=$(nuclearss-seaker 2>/dev/null)

if [ -z "$output" ]; then
    exit 0
fi

if ! exec < /dev/tty 2>/dev/null; then
    echo "Error: there is no access to the terminal (/dev/tty is unavailable). The commit is blocked."
    exit 1
fi

tmpfile=$(mktemp)
echo "$output" > "$tmpfile"
nuclearss tui "$tmpfile"

exit $?
