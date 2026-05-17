# ЛР2 — access/refresh аутентификация и авторизация

## Что сделано

### 1. Схема access + refresh
- `access_token` — короткоживущий JWT для доступа к защищённым endpoint'ам.
- `refresh_token` — длинноживущий случайный токен для продления сессии.

### 2. Серверная часть
- `POST /api/v1/auth/login` — вход и выдача пары токенов.
- `POST /api/v1/auth/refresh` — обновление access token и ротация refresh token.
- `POST /api/v1/auth/logout` — отзыв refresh token и завершение сессии.
- `GET /api/v1/auth/me` — получение текущего пользователя.

### 3. Безопасность
- в БД хранится не сам refresh token, а его SHA-256 хэш;
- refresh token ротируется при каждом обновлении сессии;
- после logout дальнейшее обновление по старому refresh token блокируется;
- RBAC из ЛР1 сохранён и продолжает работать на бизнес-операциях.

### 4. Архитектура
Для auth-механизма используется разделение:
- `app/api/v1/endpoints/auth.py` — API слой;
- `app/services/auth_service.py` — бизнес-логика;
- `app/repositories/users.py`, `app/repositories/refresh_sessions.py` — доступ к данным.

### 5. Frontend
- централизованное состояние аутентификации в `AuthContext`;
- хранение access/refresh токенов в `tokenStorage.ts`;
- автоматическое обновление access token через `axios` interceptor;
- при невалидной сессии клиент очищает состояние и отправляет пользователя на вход.
