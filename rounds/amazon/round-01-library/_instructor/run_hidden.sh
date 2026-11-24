#!/usr/bin/env bash
set -uo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: bash run_hidden.sh <attempt-folder>" >&2
  exit 1
fi

attempt="$(cd "$1" && pwd)" || { echo "No such folder: $1" >&2; exit 1; }
repo="$attempt/repo"
hidden_src="$(cd "$(dirname "$0")" && pwd)/hidden_tests"
[ -d "$repo/tests" ] || { echo "No repo/tests in $attempt" >&2; exit 1; }

if [ -x "$attempt/.venv/bin/python" ]; then
  py="$attempt/.venv/bin/python"
elif [ -x "$repo/.venv/bin/python" ]; then
  py="$repo/.venv/bin/python"
else
  py="python3"
fi

dest="$repo/tests/_hidden_round01"
rm -rf "$dest"
cleanup() { rm -rf "$dest"; }
trap cleanup EXIT INT TERM

cp -R "$hidden_src" "$dest"

echo "Running hidden tests with $py"
cd "$repo"
PYTHONDONTWRITEBYTECODE=1 "$py" -m pytest -p no:cacheprovider -v -rA "tests/_hidden_round01"
status=$?
exit $status
