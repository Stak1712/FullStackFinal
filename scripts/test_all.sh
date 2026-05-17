#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Running backend tests..."
cd "$ROOT_DIR/ai-interview-platform"

if [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON="python3"
else
  PYTHON="python"
fi

"$PYTHON" -m pytest --cov=app --cov-report=term-missing

echo "Running frontend checks..."
cd "$ROOT_DIR/ai-interview-frontend"

npm run typecheck
npm run test:coverage
