import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { http } from "../api/http";
import { useAuth } from "../auth/AuthContext";
import { getDisplayName } from "../auth/access";
import Seo from "../seo/Seo";

type Grade = "Junior" | "Middle" | "Senior";
const GRADE_OPTIONS: Grade[] = ["Junior", "Middle", "Senior"];

const SKILL_OPTIONS = [
  "Python",
  "FastAPI",
  "React",
  "TypeScript",
  "SQL",
  "Docker",
  "Git",
  "Алгоритмы",
  "ООП",
  "System Design",
] as const;

type ResumeItem = {
  id: number;
  owner_id: string;
  title: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  status: string;
  grade?: string | null;
  skills: string[];
  summary?: string | null;
  created_at: string;
  download_url?: string | null;
};

type ResumeListResponse = {
  items: ResumeItem[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
};

type UploadTargetResponse = {
  resume: ResumeItem;
  upload_url: string;
  upload_method: string;
  expires_in: number;
};

function formatBytes(value: number) {
  if (!value) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = value;
  let unit = 0;
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024;
    unit += 1;
  }
  return `${size.toFixed(size >= 10 || unit === 0 ? 0 : 1)} ${units[unit]}`;
}

function formatDate(value?: string) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export default function ResumePage() {
  const { user, hasPermission } = useAuth();
  const navigate = useNavigate();

  const displayName = getDisplayName(user);
  const email = user?.email ?? "unknown@email";

  const [title, setTitle] = useState<string>("Моё резюме");
  const [grade, setGrade] = useState<Grade | null>(null);
  const [skills, setSkills] = useState<string[]>([]);
  const [summary, setSummary] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [startingInterview, setStartingInterview] = useState<boolean>(false);

  const [search, setSearch] = useState<string>("");
  const [searchInput, setSearchInput] = useState<string>("");
  const [gradeFilter, setGradeFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortOrder, setSortOrder] = useState<string>("desc");
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(5);
  const [listLoading, setListLoading] = useState<boolean>(true);
  const [listError, setListError] = useState<string | null>(null);
  const [resumes, setResumes] = useState<ResumeItem[]>([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, page_size: 5, pages: 1, has_next: false, has_prev: false });

  const canCreateSession = hasPermission("ai_sessions:create");
  const canUploadResume = hasPermission("resumes:upload");
  const canReadAnyResume = hasPermission("resumes:read:any");

  const queryLabel = useMemo(() => {
    if (gradeFilter === "all" && statusFilter === "all" && !search) return "Все резюме";
    return "Отфильтрованный список";
  }, [gradeFilter, statusFilter, search]);

  const toggleSkill = (skill: string) => {
    setSkills((prev) => (prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]));
  };

  const loadResumes = async () => {
    setListLoading(true);
    setListError(null);
    try {
      const res = await http.get<ResumeListResponse>("/resumes", {
        params: {
          page,
          page_size: pageSize,
          search: search || undefined,
          grade: gradeFilter !== "all" ? gradeFilter.toLowerCase() : undefined,
          status: statusFilter !== "all" ? statusFilter : undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
        },
      });
      setResumes(res.data.items);
      setMeta({
        total: res.data.total,
        page: res.data.page,
        page_size: res.data.page_size,
        pages: res.data.pages,
        has_next: res.data.has_next,
        has_prev: res.data.has_prev,
      });
    } catch (err: any) {
      setListError(err?.response?.data?.detail || "Не удалось загрузить список резюме");
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    void loadResumes();
  }, [page, pageSize, search, gradeFilter, statusFilter, sortBy, sortOrder]);

  const onUploadResume = async () => {
    setError(null);
    if (!canUploadResume) {
      setError("У текущей роли нет прав на загрузку резюме.");
      return;
    }
    if (!selectedFile) {
      setError("Выберите файл резюме.");
      return;
    }
    if (!grade) {
      setError("Выберите Grade перед загрузкой резюме.");
      return;
    }
    if (skills.length === 0) {
      setError("Выберите хотя бы один навык.");
      return;
    }

    setUploading(true);
    try {
      const target = await http.post<UploadTargetResponse>("/resumes/upload-url", {
        title: title.trim() || selectedFile.name,
        filename: selectedFile.name,
        content_type: selectedFile.type || "application/octet-stream",
        size_bytes: selectedFile.size,
        grade: grade.toLowerCase(),
        skills,
        summary: summary.trim() || undefined,
      });

      const uploadResponse = await fetch(target.data.upload_url, {
        method: target.data.upload_method || "PUT",
        headers: {
          "Content-Type": selectedFile.type || "application/octet-stream",
        },
        body: selectedFile,
      });

      if (!uploadResponse.ok) {
        throw new Error(`Загрузка файла завершилась с кодом ${uploadResponse.status}`);
      }

      await http.post(`/resumes/${target.data.resume.id}/complete`, { status: "uploaded" });
      setSelectedFile(null);
      setSummary("");
      setPage(1);
      await loadResumes();
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "Не удалось загрузить резюме");
    } finally {
      setUploading(false);
    }
  };

  const onSaveAndStart = async () => {
    setError(null);

    if (!canCreateSession) {
      setError("У текущей роли нет прав на запуск AI-сессии.");
      return;
    }
    if (!grade) {
      setError("Выберите Grade");
      return;
    }
    if (skills.length === 0) {
      setError("Выберите хотя бы один навык");
      return;
    }

    setStartingInterview(true);
    try {
      const res = await http.post("/ai/sessions", { grade, skills });
      const sessionId = res.data?.session_id;
      if (!sessionId) {
        setError("Не удалось создать сессию интервью");
        return;
      }
      navigate(`/interview/${sessionId}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Ошибка запуска интервью");
    } finally {
      setStartingInterview(false);
    }
  };

  const applyResume = (resume: ResumeItem) => {
    setTitle(resume.title);
    setSummary(resume.summary || "");
    setGrade(resume.grade ? ((resume.grade.charAt(0).toUpperCase() + resume.grade.slice(1)) as Grade) : null);
    setSkills(resume.skills || []);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <section className="page-wrapper">
      <Seo title="Резюме и запуск интервью" description="Закрытая страница загрузки резюме и запуска интервью." noIndex />
      <div className="profile-page">
        <div className="profile-header">
          <div className="profile-header-main">
            <h1 className="page-title">Резюме, объектное хранилище и запуск интервью</h1>
            <p className="hint">
              Аккаунт: <b>{displayName}</b> <span className="muted">({email})</span>
            </p>
          </div>
        </div>

        <div className="profile-grid">
          <div className="profile-card">
            <h3 className="card-title">Данные кандидата</h3>
            {error ? <p className="error-text">{error}</p> : null}

            <div className="form-field">
              <span>Название резюме</span>
              <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Например: Python Backend CV" />
            </div>

            <div className="form-field">
              <span>Ваш Grade</span>
              <div className="chip-group" role="radiogroup" aria-label="Grade">
                {GRADE_OPTIONS.map((opt) => {
                  const selected = grade === opt;
                  return (
                    <button
                      key={opt}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      className={`chip ${selected ? "chip-selected" : ""}`}
                      onClick={() => setGrade(opt)}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="form-field">
              <span>Навыки</span>
              <div className="chip-group" aria-label="Skills">
                {SKILL_OPTIONS.map((skill) => {
                  const selected = skills.includes(skill);
                  return (
                    <button
                      key={skill}
                      type="button"
                      aria-pressed={selected}
                      className={`chip ${selected ? "chip-selected" : ""}`}
                      onClick={() => toggleSkill(skill)}
                    >
                      {skill}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="form-field">
              <span>Краткое описание</span>
              <textarea value={summary} onChange={(e) => setSummary(e.target.value)} placeholder="Кратко перечисли стек, опыт и сильные стороны" />
            </div>

            <div className="form-field">
              <span>Файл резюме</span>
              <input
                type="file"
                accept=".pdf,.doc,.docx,.txt"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              />
              <div className="hint">
                {selectedFile ? `Выбрано: ${selectedFile.name} (${formatBytes(selectedFile.size)})` : "Файл пока не выбран"}
              </div>
            </div>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <button className="btn-secondary" onClick={onUploadResume} disabled={uploading || !canUploadResume}>
                {uploading ? "Загрузка..." : "Загрузить резюме"}
              </button>
              <button className="btn-primary" onClick={onSaveAndStart} disabled={startingInterview || !canCreateSession}>
                {startingInterview ? "Стартуем..." : "Сохранить профиль и приступить к интервью"}
              </button>
            </div>
          </div>

          <div className="profile-card">
            <h3 className="card-title">Фильтры и сортировка</h3>
            <div className="form-field">
              <span>Поиск по названию или файлу</span>
              <div style={{ display: "flex", gap: 8 }}>
                <input value={searchInput} onChange={(e) => setSearchInput(e.target.value)} placeholder="Например, backend" />
                <button className="btn-secondary" onClick={() => { setPage(1); setSearch(searchInput.trim()); }}>
                  Найти
                </button>
              </div>
            </div>

            <div className="form-field">
              <span>Grade</span>
              <select value={gradeFilter} onChange={(e) => { setPage(1); setGradeFilter(e.target.value); }}>
                <option value="all">Все</option>
                <option value="junior">Junior</option>
                <option value="middle">Middle</option>
                <option value="senior">Senior</option>
              </select>
            </div>

            <div className="form-field">
              <span>Статус</span>
              <select value={statusFilter} onChange={(e) => { setPage(1); setStatusFilter(e.target.value); }}>
                <option value="all">Все</option>
                <option value="pending_upload">pending_upload</option>
                <option value="uploaded">uploaded</option>
              </select>
            </div>

            <div className="form-field">
              <span>Сортировка</span>
              <div style={{ display: "flex", gap: 8 }}>
                <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                  <option value="created_at">По дате</option>
                  <option value="title">По названию</option>
                  <option value="size_bytes">По размеру</option>
                  <option value="grade">По grade</option>
                  <option value="status">По статусу</option>
                </select>
                <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value)}>
                  <option value="desc">Сначала новые</option>
                  <option value="asc">Сначала старые</option>
                </select>
              </div>
            </div>

            <div className="form-field">
              <span>Размер страницы</span>
              <select value={pageSize} onChange={(e) => { setPage(1); setPageSize(Number(e.target.value)); }}>
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={20}>20</option>
              </select>
            </div>

            <div className="hint">
              {queryLabel}. Доступ ко всем резюме: <b>{canReadAnyResume ? "да" : "нет"}</b>
            </div>
          </div>
        </div>

        <div className="profile-card" style={{ marginTop: 16 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 16, flexWrap: "wrap" }}>
            <h3 className="card-title">Загруженные резюме</h3>
            <div className="hint">Всего: <b>{meta.total}</b></div>
          </div>

          {listLoading ? <p className="muted">Загружаю список...</p> : null}
          {listError ? <p className="error-text">{listError}</p> : null}
          {!listLoading && !listError && resumes.length === 0 ? <p className="muted">Пока нет загруженных резюме.</p> : null}

          <div style={{ display: "grid", gap: 12 }}>
            {resumes.map((resume) => (
              <div key={resume.id} className="profile-card" style={{ padding: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                  <div>
                    <h4 style={{ margin: "0 0 6px" }}>{resume.title}</h4>
                    <p className="muted" style={{ margin: 0 }}>{resume.original_filename}</p>
                  </div>
                  <div className="profile-badges">
                    <span className="badge">{resume.status}</span>
                    <span className="badge badge-soft">{formatBytes(resume.size_bytes)}</span>
                    {resume.grade ? <span className="badge badge-soft">{resume.grade}</span> : null}
                  </div>
                </div>

                <div className="permission-list" style={{ marginTop: 12 }}>
                  {resume.skills.map((skill) => (
                    <span key={`${resume.id}-${skill}`} className="badge badge-soft">{skill}</span>
                  ))}
                </div>

                {resume.summary ? <p className="muted" style={{ marginTop: 12 }}>{resume.summary}</p> : null}

                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
                  <div className="hint">Загружено: <b>{formatDate(resume.created_at)}</b></div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button className="btn-secondary" onClick={() => applyResume(resume)}>
                      Использовать в форме
                    </button>
                    {resume.download_url ? (
                      <button className="btn-primary" onClick={() => window.open(resume.download_url ?? "#", "_blank", "noopener,noreferrer")}>
                        Скачать
                      </button>
                    ) : null}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", marginTop: 16, flexWrap: "wrap" }}>
            <div className="hint">
              Страница <b>{meta.page}</b> из <b>{meta.pages}</b>
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button className="btn-secondary" disabled={!meta.has_prev} onClick={() => setPage((prev) => Math.max(1, prev - 1))}>
                Назад
              </button>
              <button className="btn-secondary" disabled={!meta.has_next} onClick={() => setPage((prev) => prev + 1)}>
                Вперёд
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
