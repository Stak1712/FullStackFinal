#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
docker compose up --build -d
echo "Frontend/reverse proxy: http://localhost:8080"
echo "Backend docs:          http://localhost:8080/docs"
echo "MinIO console:          http://localhost:9001"
