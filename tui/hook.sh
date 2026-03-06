#!/usr/bin/env sh

output=$(./dummy-seaker 2>/dev/null)

if [ -z "$output" ]; then
    exit 0
fi


tmpfile=$(mktemp)
echo "$output" > "$tmpfile"
./dist/main --file "$tmpfile"

exit 0