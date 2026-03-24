#!/usr/bin/env bash
# Pre-commit hook: ensures commits touching src/ also include docs/ or README changes.
# Exits 0 (pass) if:
#   - No src/ files are staged, OR
#   - At least one docs/ file or README.md is also staged
# Exits 1 (fail) if:
#   - src/ files are staged but no docs/ or README.md files are included

staged_files=$(git diff --cached --name-only)

has_src=false
has_docs=false

for file in $staged_files; do
    case "$file" in
        src/*) has_src=true ;;
        docs/*) has_docs=true ;;
        README.md) has_docs=true ;;
    esac
done

if [ "$has_src" = true ] && [ "$has_docs" = false ]; then
    echo "ERROR: Source files changed without documentation update."
    echo ""
    echo "Commits that modify files under src/ must also update at least"
    echo "one file under docs/ or README.md."
    echo ""
    echo "If this change truly needs no docs update, use --no-verify to skip."
    exit 1
fi

exit 0
