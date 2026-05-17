# Лабораторная работа №6 — Контейнеризация и автоматизация развертывания

## Тема проекта

**ИИ-платформа для прохождения технических собеседований с виртуальным интервьюером.**

Цель доработки: подготовить проект к воспроизводимому запуску через Docker, добавить reverse proxy, healthcheck, переменные окружения, изоляцию секретов и CI/CD-пайплайн.

---

## 1. Архитектура контейнеризации

Выделены сервисы:

```text
reverse-proxy  → единая точка входа на порт 8080
frontend       → React/Vite build, отдаётся через Nginx
backend        → FastAPI + Uvicorn
minio          → S3-совместимое объектное хранилище для резюме
volumes        → постоянные данные backend и MinIO
network        → внутренняя Docker-сеть app-network
```

Пользователь открывает приложение через:

```text
http://localhost:8080
```

Reverse proxy маршрутизирует запросы:

```text
/              → frontend
/api/*         → backend
/docs          → backend Swagger
/robots.txt    → backend SEO endpoint
/sitemap.xml   → backend SEO endpoint
```

---

## 2. Dockerfile для backend

Файл:

```text
ai-interview-platform/Dockerfile
```

Что делает:

1. Берёт базовый образ `python:3.11-slim`.
2. Устанавливает зависимости из `requirements.txt`.
3. Копирует код `app/`.
4. Создаёт директорию `/app/data`.
5. Запускает приложение через Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Также добавлен `HEALTHCHECK`, который проверяет endpoint:

```text
/api/v1/health/live
```

Секреты в Dockerfile не копируются. `.env` не попадает в образ.

---

## 3. Dockerfile для frontend

Файл:

```text
ai-interview-frontend/Dockerfile
```

Используется multi-stage build:

1. Stage `build`:
   - образ `node:22-alpine`;
   - установка зависимостей;
   - сборка React-приложения командой `npm run build`.
2. Stage `runtime`:
   - образ `nginx:1.27-alpine`;
   - копирование `dist/` в `/usr/share/nginx/html`;
   - отдача собранного frontend через Nginx.

Frontend получает переменные сборки через build args:

```text
VITE_API_URL=/api/v1
VITE_PUBLIC_SITE_URL=http://localhost:8080
```

Это нужно, чтобы в Docker frontend обращался не напрямую к `127.0.0.1:8000`, а через reverse proxy.

---

## 4. Reverse proxy

Файл:

```text
deploy/nginx/default.conf
```

Reverse proxy нужен, чтобы у пользователя была одна точка входа:

```text
http://localhost:8080
```

Он проксирует:

```text
/api/        → backend:8000
/docs        → backend:8000/docs
/openapi.json→ backend:8000/openapi.json
/robots.txt  → backend:8000/robots.txt
/sitemap.xml → backend:8000/sitemap.xml
/            → frontend:80
```

Так frontend и backend работают как единое приложение.

---

## 5. docker-compose

Главный файл:

```text
docker-compose.yml
```

Он запускает все сервисы одной командой:

```bash
docker compose up --build
```

В compose описаны:

- `backend`;
- `frontend`;
- `reverse-proxy`;
- `minio`;
- `backend-data` volume;
- `minio-data` volume;
- `app-network` сеть;
- healthcheck для сервисов;
- порядок запуска через `depends_on` и `condition: service_healthy`.

---

## 6. Object Storage через MinIO

В Docker-режиме backend работает с MinIO как с S3-совместимым хранилищем:

```text
STORAGE_PROVIDER=s3
STORAGE_S3_ENDPOINT_URL=http://minio:9000
STORAGE_S3_BUCKET=ai-interview-assets
```

MinIO Console доступна по адресу:

```text
http://localhost:9001
```

По умолчанию:

```text
login: minioadmin
password: minioadmin
```

В реальном окружении эти значения должны быть изменены через `.env`.

---

## 7. Безопасная конфигурация

Добавлены `.dockerignore`:

```text
ai-interview-platform/.dockerignore
ai-interview-frontend/.dockerignore
```

Они исключают:

```text
.env
.venv
node_modules
data
coverage
__pycache__
dist
```

Также добавлен корневой `.gitignore`, который не даёт случайно закоммитить секреты, локальные БД, виртуальное окружение и зависимости.

Файл `.env.example` содержит только примерные значения. Реальный `.env` не должен попадать в Git.

---

## 8. CI/CD

Добавлен GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

Pipeline состоит из этапов:

1. `backend-tests`:
   - установка Python 3.11;
   - установка `requirements-dev.txt`;
   - запуск `pytest` с coverage;
   - минимальный backend coverage threshold: `70%`.

2. `frontend-tests`:
   - установка Node.js 22;
   - `npm install`;
   - `npm run typecheck`;
   - `npm run test:coverage`;
   - `npm run build`.

3. `docker-build`:
   - проверка `docker compose config`;
   - сборка Docker-образов.

4. `deploy-placeholder`:
   - заготовка под будущий deploy после успешных проверок на ветке `main`.

Такой pipeline соответствует базовому CI/CD: сначала тесты, потом сборка, потом подготовка к развёртыванию.

---

## 9. Команды запуска

### Локальный Docker-запуск всего проекта

```bash
cp .env.example .env
docker compose up --build
```

После запуска:

```text
Frontend:      http://localhost:8080
Backend docs:  http://localhost:8080/docs
MinIO console: http://localhost:9001
```

### Запуск в фоне

```bash
docker compose up --build -d
```

### Остановка

```bash
docker compose down
```

### Остановка с удалением volumes

```bash
docker compose down -v
```

---

## 10. Скрипты

Добавлены вспомогательные скрипты:

```text
scripts/run_local.sh
scripts/test_all.sh
scripts/deploy_local.sh
```

`deploy_local.sh` запускает весь проект через Docker Compose и выводит адреса сервисов.

---

## 11. Итог по ЛР6

В результате лабораторной работы добавлены:

- Dockerfile для FastAPI backend;
- Dockerfile для React frontend;
- Nginx-конфиг для frontend;
- reverse proxy Nginx;
- общий `docker-compose.yml`;
- MinIO как S3-совместимое объектное хранилище;
- volumes для постоянных данных;
- Docker network;
- healthcheck для backend, frontend, reverse proxy и MinIO;
- `.dockerignore` и безопасная работа с `.env`;
- GitHub Actions CI/CD;
- скрипты локального запуска и проверки.

Проект теперь можно поднять одной командой и проверить через единый адрес `http://localhost:8080`.

