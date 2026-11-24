#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ] || [ -z "$1" ]; then
  echo "Usage: bash start_attempt.sh <name>" >&2
  exit 1
fi

name="$1"
round_dir="$(cd "$(dirname "$0")" && pwd)"
attempts_dir="$round_dir/attempts"
mkdir -p "$attempts_dir"

base="$name-$(date +%Y-%m-%d)"
attempt="$attempts_dir/$base"
n=2
while [ -e "$attempt" ]; do
  attempt="$attempts_dir/$base-$n"
  n=$((n + 1))
done

mkdir -p "$attempt"
tar -xzf "$round_dir/pristine.tar.gz" -C "$attempt"
cp "$round_dir/assistant_rules.txt" "$attempt/assistant_rules.txt"
: > "$attempt/test_runs.log"
: > "$attempt/process_log.md"

cat <<MSG
Attempt folder: $attempt

Setup (copy and paste):

  cd "$attempt/repo"
  python3 -m venv ../.venv
  source ../.venv/bin/activate
  pip install -r requirements.txt
  ./t

Then open a NEW terminal in $attempt/repo, start a fresh Claude Code session,
and paste prompts/2-assistant.md. Read TASK.md, then README.md (the issue is described there). Run tests only with ./t.
MSG
