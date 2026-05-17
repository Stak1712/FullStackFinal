#!/usr/bin/env bash
set -euo pipefail

echo "Backend:"
echo "  cd ai-interview-platform"
echo "  cp .env.example .env"
echo "  python3 -m venv .venv && source .venv/bin/activate"
echo "  python -m pip install -r requirements-dev.txt"
echo "  python -m uvicorn app.main:app --reload"
echo
echo "Frontend:"
echo "  cd ai-interview-frontend"
echo "  cp .env.example .env"
echo "  npm install"
echo "  npm run dev"
