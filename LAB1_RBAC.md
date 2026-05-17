# Лабораторная работа №1 — RBAC для AI Interview Platform

## Что реализовано

В проект добавлена ролевая модель доступа (RBAC) для backend на **FastAPI** и frontend на **React + TypeScript**.

### Роли
- `guest` — только публичные страницы;
- `user` — работа со своим профилем и своими AI-сессиями;
- `manager` — права пользователя + управление каталогом интервью;
- `admin` — полный доступ + управление ролями пользователей.

### Матрица ролей и прав

| Роль | Основные права |
|---|---|
| guest | `platform:read` |
| user | `profile:read:self`, `interviews:read`, `ai_sessions:create`, `ai_sessions:read:own`, `ai_sessions:answer:own`, `ml:score` |
| manager | права `user` + `profile:read:any`, `users:list`, `interviews:create`, `interviews:update`, `ai_sessions:read:any` |
| admin | права `manager` + `users:role:manage`, `interviews:delete`, `admin:panel` |

## Backend

### Что добавлено
- `app/auth/rbac.py` — матрица ролей и permissions;
- `app/auth/dependencies.py` — guards/dependencies для проверки ролей и прав;
- защита endpoint'ов по permissions;
- административные endpoint'ы:
  - `GET /api/v1/admin/rbac`
  - `GET /api/v1/admin/users`
  - `PATCH /api/v1/admin/users/{user_id}/role`

### Ограничения
- пользователь видит только свои AI-сессии;
- пользователь не может менять роли;
- удаление интервью доступно только `admin`;
- при нехватке прав сервер возвращает `403 Forbidden`.

### Автонастройка администратора
Первый зарегистрированный пользователь получает роль `admin`.
Если в уже существующей базе нет администратора, при старте приложения старейший пользователь автоматически повышается до `admin`.

## Frontend

### Что добавлено
- расширенный `ProtectedRoute` с проверкой ролей и permissions;
- страница `ForbiddenPage` для запрета доступа;
- страница `AdminUsersPage` для управления ролями;
- адаптация интерфейса под роль текущего пользователя;
- отображение permissions в профиле;
- пункт "Админ-панель" в навигации только для администратора.

## Основные сценарии проверки
1. Зарегистрировать первого пользователя — он станет `admin`.
2. Создать второго пользователя.
3. Под `admin` открыть `/admin/users` и выдать второму пользователю роль `manager`.
4. Проверить, что:
   - обычный `user` не может открыть `/admin/users`;
   - `manager` может создавать/редактировать интервью, но не менять роли;
   - `user` может запускать только свои AI-сессии;
   - `admin` видит административный интерфейс и управляет ролями.
