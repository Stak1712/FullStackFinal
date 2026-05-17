# ЛР3 — объектное хранилище, поиск, фильтры и пагинация

## Что реализовано

- Файлы резюме **хранятся в MinIO**, а не в локальной папке проекта.
- Backend использует `STORAGE_PROVIDER=s3` и подключается к MinIO через S3-совместимый API.
- Для загрузки и скачивания резюме используются **signed backend URLs**:
  - `PUT /api/v1/resumes/storage/upload/{token}`
  - `GET /api/v1/resumes/storage/download/{token}`
- При загрузке backend принимает файл по signed URL и сохраняет его в bucket `ai-interview-assets` в MinIO.
- Метаданные резюме по-прежнему хранятся в SQLite в таблице `resume_assets`.
- Для списка резюме и каталога интервью реализованы поиск, фильтры, сортировка и пагинация.

## Ключевые файлы

- `app/services/storage.py` — адаптер хранения, работа с MinIO
- `app/api/v1/endpoints/resumes.py` — API резюме и signed upload/download URL
- `app/models/resume_asset.py` — модель метаданных резюме
- `src/pages/ResumePage.tsx` — загрузка, список резюме, поиск, фильтры, сортировка, пагинация

## Запуск MinIO

Из папки `ai-interview-platform`:

```bash
docker compose up -d minio
```

После запуска:
- API MinIO: `http://127.0.0.1:9000`
- Web Console: `http://127.0.0.1:9001`
- login: `minioadmin`
- password: `minioadmin`

## Где лежат данные

- **Файлы резюме**: в bucket `ai-interview-assets` внутри MinIO
- **Метаданные**: `data/app.db`, таблица `resume_assets`
