# Лабораторная работа №5 — Комплексное тестирование клиентской и серверной частей

## Тема проекта

**ИИ-платформа для прохождения технических собеседований с виртуальным интервьюером.**

Цель доработки: добавить воспроизводимую тестовую инфраструктуру для backend, frontend и E2E-сценариев, чтобы проверить авторизацию, RBAC, работу с резюме/файлами, фильтрацию, внешнюю интеграцию и устойчивую обработку ошибок.

---

## 1. Тестовая модель приложения

Для тестирования выделены критические пользовательские сценарии:

1. Регистрация, вход, получение текущего пользователя, выход.
2. Ротация refresh token и запрет повторного использования старого refresh token.
3. Защита закрытых endpoint'ов от анонимных пользователей.
4. Проверка RBAC: обычный пользователь не может работать с админкой, администратор может менять роли, manager может создавать интервью.
5. CRUD/каталог интервью: создание, поиск, сортировка и пагинация.
6. Работа с резюме: создание upload target, фильтрация списка, ограничение доступа к чужим данным, проверка ограничения размера файла.
7. Интеграция внешнего API материалов подготовки: нормальный ответ, fallback при ошибке внешнего сервиса.
8. Frontend-поведение: хранение токенов, декодирование JWT, защита маршрутов, отображение элементов по ролям, страница материалов.
9. E2E: регистрация пользователя через UI и поиск материалов на странице `/resources`.

Области повышенного риска:

- access/refresh токены;
- права ролей;
- загрузка пользовательских файлов;
- запросы к внешнему API;
- ошибки сети и истечение сессии;
- маршруты, которые должны быть закрыты.

---

## 2. Backend-тестирование FastAPI

Добавлена тестовая инфраструктура:

```text
ai-interview-platform/tests/conftest.py
```

В `conftest.py` задаётся отдельное тестовое окружение:

```text
ENV=test
DATABASE_URL=sqlite:///./data/test.db
STORAGE_PROVIDER=local
STORAGE_LOCAL_ROOT=./data/test_object_storage
```

Перед тестами база очищается и пересоздаётся через SQLAlchemy `Base.metadata.drop_all/create_all`. Это даёт изолированное состояние между тестами.

### Добавленные backend-тесты

```text
ai-interview-platform/tests/test_health.py
ai-interview-platform/tests/test_auth_api.py
ai-interview-platform/tests/test_rbac_api.py
ai-interview-platform/tests/test_interviews.py
ai-interview-platform/tests/test_resumes_api.py
ai-interview-platform/tests/test_resources_api.py
ai-interview-platform/tests/test_auth_service_unit.py
ai-interview-platform/tests/test_external_resource_service_unit.py
ai-interview-platform/tests/test_storage_service_unit.py
```

### Что проверяется

**Health endpoints:**

- `GET /api/v1/health/live`;
- `GET /api/v1/health/ready`.

**Auth API:**

- успешная регистрация;
- успешный вход;
- получение `/auth/me`;
- запрет дублирующего email;
- неправильный пароль возвращает `401`;
- refresh token ротируется;
- старый refresh token после ротации больше не работает;
- после logout refresh token отзывается.

**RBAC:**

- анонимный пользователь получает `401`;
- обычный пользователь не может открыть `/admin/users`;
- админ может повысить пользователя до `manager`;
- `manager` может создать интервью;
- обычный пользователь не может создать интервью без permission.

**Интервью:**

- создание записей интервью;
- каталог с поиском;
- сортировка;
- пагинация;
- `404` для несуществующего интервью.

**Резюме и файлы:**

- создание signed upload URL;
- сохранение метаданных резюме;
- фильтрация списка резюме по search/grade;
- запрет просмотра чужих резюме обычным пользователем;
- запрет анонимного доступа;
- ошибка `413`, если размер файла выше лимита.

**Внешний API:**

- endpoint `/api/v1/resources/interview-prep` возвращает нормализованный live-ответ;
- при ошибке внешнего API возвращается fallback, а приложение не падает.

**Unit-тесты сервисного слоя:**

- `AuthService` назначает роль `admin` первому пользователю и `user` следующим;
- `AuthService` запрещает дублирующий email;
- `AuthService` возвращает `401` при неправильном пароле;
- `ExternalResourceService` использует cache;
- `ExternalResourceService` возвращает fallback при локальном rate limit;
- `StorageService` очищает имя файла, создаёт scoped upload URL и сохраняет файл в local storage.

---

## 3. Frontend-тестирование React + TypeScript

Добавлены зависимости и команды в `ai-interview-frontend/package.json`:

```json
{
  "test": "vitest run --config vitest.config.ts",
  "test:watch": "vitest --config vitest.config.ts",
  "test:coverage": "vitest run --coverage --config vitest.config.ts",
  "e2e": "playwright test",
  "typecheck": "tsc -b"
}
```

Добавлена конфигурация Vitest:

```text
ai-interview-frontend/vitest.config.ts
```

Тестовая среда — `jsdom`. Настроены coverage thresholds:

```text
lines: 70
functions: 65
branches: 60
statements: 70
```

### Добавленные frontend-тесты

```text
src/auth/tokenStorage.test.ts
src/auth/jwt.test.ts
src/auth/ProtectedRoute.test.tsx
src/components/Navbar.test.tsx
src/pages/ResourcesPage.test.tsx
```

### Что проверяется

**tokenStorage:**

- сохранение access/refresh token;
- очистка access/refresh token.

**JWT helpers:**

- декодирование payload;
- проверка истёкшего токена.

**ProtectedRoute:**

- анонимный пользователь перенаправляется на `/login`;
- пользователь без роли/прав перенаправляется на `/forbidden`;
- пользователь с нужной ролью и permission видит защищённый контент.

**Navbar:**

- guest видит кнопки входа и регистрации;
- авторизованный пользователь видит ссылку на интервью и профиль;
- ссылка на админ-панель видна только admin.

**ResourcesPage:**

- страница загружает материалы при открытии;
- показывает ошибку при недоступности API;
- отправляет новый запрос при поиске по навыку.

---

## 4. E2E-тестирование

Добавлен Playwright:

```text
ai-interview-frontend/playwright.config.ts
```

E2E-конфигурация стартует backend и frontend перед тестами:

- backend: `uvicorn app.main:app --host 127.0.0.1 --port 8000`;
- frontend: `npm run dev -- --host 127.0.0.1 --port 5173`.

Добавлены E2E-сценарии:

```text
ai-interview-frontend/e2e/auth-flow.spec.ts
ai-interview-frontend/e2e/resources-flow.spec.ts
```

### E2E-сценарии

1. Пользователь регистрируется через UI, попадает в профиль и выходит из аккаунта.
2. Пользователь открывает `/resources`, вводит навык и получает результаты/состояние источника.

---

## 5. Команды проверки

### Backend

```bash
cd ai-interview-platform
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
pytest
pytest --cov=app --cov-report=term-missing
```

### Frontend

```bash
cd ai-interview-frontend
npm install
npm run typecheck
npm run test
npm run test:coverage
```

### E2E

```bash
cd ai-interview-frontend
npm install
npx playwright install
npm run e2e
```

---

## 6. Итог по ЛР5

В результате лабораторной работы добавлены:

- unit-тесты backend-сервисов;
- integration-тесты FastAPI endpoint'ов;
- frontend unit/component-тесты;
- E2E-тесты основных пользовательских сценариев;
- тестовое окружение и отдельная тестовая БД;
- мокирование внешнего API;
- coverage-команды и метрики качества;
- разделение unit/integration/e2e через pytest markers и структуру файлов.

