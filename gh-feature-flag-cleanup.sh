#!/usr/bin/env bash

set -e

# Usage info
usage() {
  echo "Usage: gh feature-flag-cleanup <repository> <feature-flag>"
  echo "Example: gh feature-flag-cleanup octocat/hello-world OLD_FEATURE_FLAG"
  exit 1
}

# Input validation
if [ $# -ne 2 ]; then
  usage
fi

REPO="$1"
FLAG="$2"

# Clone the repository to a temp directory
TMP_DIR=$(mktemp -d)
echo "Cloning repository $REPO into $TMP_DIR..."
gh repo clone "$REPO" "$TMP_DIR"
cd "$TMP_DIR"

# Open the repo in a new VS Code window
if command -v code >/dev/null 2>&1; then
  code -n .
else
  echo "VS Code (code) not found in PATH. Please install VS Code CLI."
fi

# Create a new branch for the cleanup
BRANCH="feature-flag-cleanup/$FLAG"
git checkout -b "$BRANCH"

# Find all files containing the feature flag
echo "Searching for occurrences of '$FLAG'..."
MATCHES=$(git grep -l "$FLAG" || true)

if [ -z "$MATCHES" ]; then
  echo "No occurrences of '$FLAG' found."
  exit 0
fi

echo "Found occurrences in:"
i=1
declare -a FILES
for FILE in $MATCHES; do
  echo "$i. $FILE"
  FILES+=("$FILE")
  ((i++))
done

echo ""
echo "For each file, enter its number to clean up, or 'q' to finish."

MODIFIED=()

while true; do
  read -p "File number to clean up (or 'q' to quit): " CHOICE
  if [ "$CHOICE" == "q" ]; then
    break
  fi
  IDX=$((CHOICE-1))
  if [ "$IDX" -ge 0 ] && [ "$IDX" -lt "${#FILES[@]}" ]; then
    FILE="${FILES[$IDX]}"
    echo "Cleaning $FILE using AI agent..."
    python3 "$(dirname "$0")/cleanup_agent.py" "$FILE" "$FLAG"
    git add "$FILE"
    MODIFIED+=("$FILE")
    echo "$FILE cleaned and staged."
  else
    echo "Invalid choice."
  fi
done

if [ "${#MODIFIED[@]}" -eq 0 ]; then
  echo "No files modified."
  exit 0
fi

# Commit and push changes, then create a PR
git commit -m "chore: remove feature flag $FLAG"
git push -u origin "$BRANCH"
gh pr create --title "Remove feature flag $FLAG" --body "Automated cleanup of feature flag: $FLAG"

echo "Pull request created. You can continue working in VS Code."
