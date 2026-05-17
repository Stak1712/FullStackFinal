# ЛР4 — SEO-оптимизация и интеграция стороннего API

## Что реализовано

### 1. SEO на frontend

В React-приложении добавлен компонент `Seo`, который на каждой странице обновляет:

- `document.title`;
- `meta name="description"`;
- `meta name="robots"`;
- canonical URL;
- Open Graph теги;
- JSON-LD для главной страницы и страницы материалов.

Публичные индексируемые страницы:

- `/` — главная;
- `/ai` — описание виртуального интервьюера;
- `/directions` — направления интервью;
- `/resources` — материалы для подготовки;
- `/about` — информация о платформе.

Закрытые/служебные страницы помечены как `noindex`:

- `/login`;
- `/register`;
- `/profile`;
- `/resume`;
- `/interview/:id`;
- `/admin/users`;
- `/forbidden`.

### 2. Техническая SEO-поддержка

На backend добавлены публичные маршруты:

- `GET /robots.txt`;
- `GET /sitemap.xml`.

Также во frontend-папке `public` добавлены статические варианты:

- `public/robots.txt`;
- `public/sitemap.xml`.

Это позволяет показать SEO и при отдельной раздаче frontend через Vite/Nginx, и при обращении к FastAPI.

### 3. Производительность

В `App.tsx` добавлен `React.lazy` и `Suspense` для тяжёлых/закрытых страниц:

- профиль;
- резюме;
- интервью;
- админ-панель;
- страница внешних материалов.

Это уменьшает стартовую загрузку публичной части приложения.

### 4. Интеграция стороннего API

Добавлен внешний сценарий: пользователь выбирает навык, а система показывает материалы для подготовки к техническому интервью.

Backend обращается к GitHub Search API через отдельный service/adapter:

- `app/services/external_resources.py`;
- `app/api/v1/endpoints/resources.py`;
- `app/schemas/external_resource.py`.

Endpoint:

```http
GET /api/v1/resources/interview-prep?skill=FastAPI&limit=6
```

Ответ нормализуется к внутреннему формату:

```json
{
  "query": "FastAPI",
  "source": "GitHub Search API",
  "external_status": "live",
  "items": [
    {
      "title": "owner/repository",
      "description": "...",
      "url": "https://github.com/...",
      "source": "GitHub",
      "stars": 1000,
      "language": "Python",
      "updated_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### 5. Надёжность внешней интеграции

В сервисе внешнего API реализованы:

- timeout;
- retry;
- in-memory cache;
- простой rate limit;
- fallback-ответ, если внешний API недоступен.

Переменные окружения добавлены в `.env.example`:

```env
PUBLIC_SITE_URL=http://localhost:5173
GITHUB_API_URL=https://api.github.com
GITHUB_API_TOKEN=
EXTERNAL_API_TIMEOUT_SECONDS=5
EXTERNAL_API_RETRIES=2
EXTERNAL_API_RATE_LIMIT_PER_MINUTE=30
EXTERNAL_API_CACHE_TTL_SECONDS=300
```

### 6. Клиентская часть внешнего API

Добавлена страница:

- `/resources`.

Ключевые файлы:

- `src/pages/ResourcesPage.tsx`;
- `src/api/resources.ts`.

На странице есть:

- форма выбора навыка;
- быстрые кнопки по популярным навыкам;
- состояние загрузки;
- состояние ошибки;
- предупреждение при fallback-режиме;
- список внешних материалов.

## Как проверить

### Backend

```bash
cd ai-interview-platform
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install -e .
uvicorn app.main:app --reload
```

Проверить в браузере:

```text
http://127.0.0.1:8000/robots.txt
http://127.0.0.1:8000/sitemap.xml
http://127.0.0.1:8000/api/v1/resources/interview-prep?skill=FastAPI&limit=6
```

### Frontend

```bash
cd ai-interview-frontend
npm install
npm run dev
```

Проверить страницу:

```text
http://localhost:5173/resources
```

## Что можно сказать на защите

В четвёртой лабораторной я не менял основную бизнес-логику MVP, а расширил приложение SEO и внешней интеграцией. Публичные страницы получили title, description, canonical, Open Graph и JSON-LD. Закрытые страницы профиля, резюме, интервью и админки помечены как noindex, чтобы поисковые системы не индексировали приватные разделы.

Для технического SEO на FastAPI реализованы `/robots.txt` и `/sitemap.xml`. В sitemap попадают только публичные маршруты, а robots запрещает индексацию закрытых разделов.

Сторонний API реализован через отдельный сервисный слой. Frontend не обращается к GitHub напрямую. Он вызывает наш backend endpoint `/api/v1/resources/interview-prep`, а backend уже обращается к GitHub Search API, нормализует ответ и отдаёт клиенту единый формат данных. Это соответствует архитектуре API → service → external adapter и позволяет централизованно контролировать таймауты, повторные попытки, кэширование, rate limit и fallback при ошибках внешнего API.
