import { useEffect, useMemo, useState, type FormEvent } from "react";
import { fetchInterviewPrepResources, type ExternalResourceResponse } from "../api/resources";
import Seo from "../seo/Seo";

const SKILLS = ["FastAPI", "React", "TypeScript", "SQL", "Docker", "Algorithms", "System Design"];

function formatUpdatedAt(value?: string | null) {
  if (!value) return "дата не указана";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString();
}

export default function ResourcesPage() {
  const [skill, setSkill] = useState("FastAPI");
  const [input, setInput] = useState("FastAPI");
  const [data, setData] = useState<ExternalResourceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const jsonLd = useMemo(
    () => ({
      "@context": "https://schema.org",
      "@type": "CollectionPage",
      name: "Материалы для подготовки к техническому собеседованию",
      description: "Подборка внешних материалов и репозиториев для подготовки к техническому интервью по выбранному навыку.",
      about: skill,
    }),
    [skill]
  );

  function loadResources(nextSkill = skill) {
    setLoading(true);
    setError(null);

    return fetchInterviewPrepResources(nextSkill, 6)
      .then((response) => {
        setData(response);
      })
      .catch((err: any) => {
        setError(err?.response?.data?.detail || err?.message || "Не удалось загрузить внешние материалы. Попробуйте позже.");
        setData(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    void loadResources("FastAPI");
  }, []);

  const onSubmit = (event: FormEvent) => {
    event.preventDefault();
    const nextSkill = input.trim() || "FastAPI";
    setSkill(nextSkill);
    void loadResources(nextSkill);
  };

  return (
    <section className="page-wrapper">
      <Seo
        title="Материалы для подготовки к интервью"
        description="Поиск внешних материалов для подготовки к техническим собеседованиям по FastAPI, React, TypeScript, SQL, Docker и другим навыкам."
        canonicalPath="/resources"
        jsonLd={jsonLd}
      />

      <div className="profile-page">
        <div className="profile-header">
          <div className="profile-header-main">
            <h1 className="page-title">Материалы для подготовки к интервью</h1>
          </div>
        </div>

        <div className="profile-grid">
          <div className="profile-card">
            <h2 className="card-title">Поиск по навыку</h2>
            <form className="form" onSubmit={onSubmit}>
              <div className="form-field">
                <span>Навык или технология</span>
                <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Например: FastAPI" />
              </div>

              <div className="chip-group" aria-label="Быстрый выбор навыка">
                {SKILLS.map((item) => (
                  <button
                    key={item}
                    type="button"
                    className={`chip ${input === item ? "chip-selected" : ""}`}
                    onClick={() => {
                      setInput(item);
                      setSkill(item);
                      void loadResources(item);
                    }}
                  >
                    {item}
                  </button>
                ))}
              </div>

              <button className="btn-primary" type="submit" disabled={loading}>
                {loading ? "Ищу материалы..." : "Найти материалы"}
              </button>
            </form>
          </div>

          <div className="profile-card">
            <h2 className="card-title">Как это связано с проектом</h2>
            <p className="muted">
              Пользователь готовится к виртуальному интервью и может быстро получить внешние материалы по выбранному
              стеку. Сервер скрывает детали внешнего API, контролирует таймауты, повторы, кэширование и rate limit.
            </p>
            <div className="permission-list">
              <span className="badge badge-soft">GitHub Search API</span>
              <span className="badge badge-soft">service/adapter</span>
              <span className="badge badge-soft">retry + timeout</span>
              <span className="badge badge-soft">fallback</span>
            </div>
          </div>
        </div>

        <div className="profile-card resources-card">
          <div className="section-heading-row">
            <h2 className="card-title">Результаты: {data?.query ?? skill}</h2>
            {data ? <span className="badge">Источник: {data.source}</span> : null}
          </div>

          {loading ? <p className="muted">Загрузка внешних данных...</p> : null}
          {error ? <p className="error-text">{error}</p> : null}
          {data?.warning ? <p className="warning-text">{data.warning}</p> : null}
          {!loading && data && data.items.length === 0 ? <p className="muted">Материалы по запросу не найдены.</p> : null}

          <div className="resource-list">
            {data?.items.map((item) => (
              <article className="resource-item" key={item.url}>
                <div>
                  <h3>
                    <a href={item.url} target="_blank" rel="noreferrer">
                      {item.title}
                    </a>
                  </h3>
                  <p>{item.description || "Описание отсутствует."}</p>
                  <div className="resource-meta">
                    <span>⭐ {item.stars}</span>
                    {item.language ? <span>{item.language}</span> : null}
                    <span>Обновлено: {formatUpdatedAt(item.updated_at)}</span>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
