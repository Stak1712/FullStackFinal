import { Link } from "react-router-dom";
import Seo from "../seo/Seo";

export default function ForbiddenPage() {
  return (
    <section className="page-wrapper">
      <Seo title="Доступ запрещён" description="Служебная страница ошибки доступа." noIndex />
      <div className="profile-card" style={{ maxWidth: 720 }}>
        <h1 className="page-title">Доступ запрещён</h1>
        <p className="profile-subtitle">
          У вашей текущей роли нет прав для выполнения этого действия или открытия этой страницы.
        </p>
        <div style={{ display: "flex", gap: 12, marginTop: 16, justifyContent: "center", flexWrap: "wrap" }}>
          <Link className="btn-secondary" to="/profile">
            Вернуться в профиль
          </Link>
          <Link className="btn-primary" to="/">
            На главную
          </Link>
        </div>
      </div>
    </section>
  );
}
