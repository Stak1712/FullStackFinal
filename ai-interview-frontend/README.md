# AI Interview Frontend

## Запуск

```bash
npm install
cp .env.example .env   # Windows: copy .env.example .env
npm run dev
```

## Что реализовано для ЛР2

- централизованное состояние аутентификации через `AuthContext`;
- хранение пары токенов access/refresh;
- автоматическое обновление access token через axios interceptor;
- logout с отзывом refresh token на backend;
- очистка состояния и редирект на вход при невалидной сессии.


## Lab 3
Resume page now includes upload to object storage and paginated search/filter UI.
