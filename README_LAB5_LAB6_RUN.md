# Запуск и проверка после ЛР5–ЛР6

## Быстрый Docker-запуск

```bash
cp .env.example .env
docker compose up --build
```

Открыть:

```text
http://localhost:8080
http://localhost:8080/docs
http://localhost:9001
```

## Backend без Docker

```bash
cd ai-interview-platform
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

## Frontend без Docker

```bash
cd ai-interview-frontend
cp .env.example .env
npm install
npm run dev
```

## Тесты

Backend:

```bash
cd ai-interview-platform
python -m pytest
python -m pytest --cov=app --cov-report=term-missing
```

Frontend:

```bash
cd ai-interview-frontend
npm run typecheck
npm run test
npm run test:coverage
```

E2E:

```bash
cd ai-interview-frontend
npx playwright install
npm run e2e
```

## Важное замечание

Для frontend после распаковки архива нужно выполнить `npm install`, потому что `node_modules` специально не включается в сдаваемый архив. Для backend `.venv` также не включается, его нужно создать заново.
