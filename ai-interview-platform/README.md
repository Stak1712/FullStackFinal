# AI Interview Platform Backend

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e .
cp .env.example .env  # Windows: copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Что реализовано для ЛР2

- access token с коротким временем жизни;
- refresh token с длительным временем жизни;
- endpoint'ы `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`;
- хранение хэша refresh token в таблице `refresh_sessions`;
- ротация refresh token при обновлении сессии;
- отзыв refresh token при logout;
- разделение backend-логики на API → service → repository для механизма аутентификации.


## Lab 3
- Resume object storage with signed upload/download URLs
- Search, filter, sort and paginate resume library
- Interview catalog endpoint with search/filter/sort/pagination
