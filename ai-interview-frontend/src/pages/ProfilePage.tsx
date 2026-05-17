import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { getDisplayName, getRoleLabel } from "../auth/access";
import Seo from "../seo/Seo";

function getInitials(name?: string) {
  if (!name) return "U";
  const parts = name.trim().split(/\s+/).slice(0, 2);
  return parts.map((p) => p[0]?.toUpperCase()).join("") || "U";
}

export default function ProfilePage() {
  const { user, hasRole, hasPermission } = useAuth();

  const displayName = getDisplayName(user);
  const email = user?.email ?? "unknown@email";
  const role = user?.role ?? "user";
  const permissions = user?.permissions ?? [];
  const canUploadResume = hasPermission("resumes:upload");

  return (
    <section className="page-wrapper">
      <Seo title="Профиль" description="Закрытая страница профиля пользователя." noIndex />
      <div className="profile-page">
        <div className="profile-header">
          <div className="profile-avatar">{getInitials(displayName)}</div>

          <div className="profile-header-main">
            <h1 className="page-title">Профиль</h1>
            <p className="profile-subtitle">
              <b>{displayName}</b> <span className="muted">({email})</span>
            </p>

            <div className="profile-badges">
              <span className="badge">роль: {getRoleLabel(role)}</span>
              <span className="badge badge-soft">RBAC + Auth + Storage</span>
            </div>
          </div>

          <div style={{ marginLeft: "auto", display: "flex", gap: 10, flexWrap: "wrap" }}>
            <Link className="btn-secondary" to="/resume">
              {canUploadResume ? "Резюме" : "Заполнить профиль"}
            </Link>
            {hasRole("admin") ? (
              <Link className="btn-primary" to="/admin/users">
                Управлять ролями
              </Link>
            ) : null}
          </div>
        </div>

        <div className="profile-grid">
          <div className="profile-card">
            <h3 className="card-title">О пользователе</h3>
            <div className="kv">
              <span>Имя</span>
              <b>{displayName}</b>
            </div>
            <div className="kv">
              <span>Email</span>
              <b>{email}</b>
            </div>
            <div className="kv">
              <span>Роль</span>
              <b>{getRoleLabel(role)}</b>
            </div>
            <div className="kv">
              <span>Количество permissions</span>
              <b>{permissions.length}</b>
            </div>
          </div>

          <div className="profile-side">
            <div className="profile-card">
              <h3 className="card-title">Доступные права</h3>
              {!permissions.length ? <p className="muted">Для роли пока нет прав.</p> : null}
              <div className="permission-list">
                {permissions.map((permission) => (
                  <span key={permission} className="badge badge-soft">
                    {permission}
                  </span>
                ))}
              </div>
            </div>

            <div className="profile-card">
              <h3 className="card-title">Текущее состояние проекта</h3>
              <p className="muted">
                После ЛР1 у проекта есть ролевая модель. После ЛР2 — access/refresh auth. После ЛР3 —
                объектное хранилище для резюме и поиск с фильтрами, сортировкой и пагинацией.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
