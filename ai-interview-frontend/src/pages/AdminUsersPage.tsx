import { useEffect, useState } from "react";
import { http } from "../api/http";
import { getDisplayName, getRoleLabel, type User } from "../auth/access";
import Seo from "../seo/Seo";

type AdminUser = User & {
  id: string;
  created_at?: string;
};

const ROLE_OPTIONS = ["guest", "user", "manager", "admin"];

export default function AdminUsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingUserId, setSavingUserId] = useState<string | null>(null);

  const loadUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await http.get<AdminUser[]>("/admin/users");
      setUsers(response.data);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Не удалось загрузить пользователей");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const updateRole = async (userId: string, role: string) => {
    try {
      setSavingUserId(userId);
      await http.patch(`/admin/users/${userId}/role`, { role });
      await loadUsers();
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Не удалось обновить роль");
    } finally {
      setSavingUserId(null);
    }
  };

  return (
    <section className="page-wrapper">
      <Seo title="Управление пользователями" description="Закрытая административная страница управления ролями." noIndex />
      <div className="profile-page">
        <div className="profile-header">
          <div className="profile-header-main">
            <h1 className="page-title">Управление ролями пользователей</h1>
            <p className="profile-subtitle">
              Администратор может просматривать пользователей и менять их роль в рамках RBAC-модели.
            </p>
          </div>
        </div>

        <div className="profile-card">
          {loading ? <p>Загрузка пользователей…</p> : null}
          {error ? <p className="error-text">{error}</p> : null}

          {!loading && !users.length ? <p>Пользователи пока не найдены.</p> : null}

          {!loading && users.length ? (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Пользователь</th>
                    <th>Email</th>
                    <th>Текущая роль</th>
                    <th>Изменить роль</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td>
                        <strong>{getDisplayName(user)}</strong>
                      </td>
                      <td>{user.email}</td>
                      <td>{getRoleLabel(user.role)}</td>
                      <td>
                        <select
                          className="role-select"
                          value={user.role}
                          onChange={(e) => updateRole(user.id, e.target.value)}
                          disabled={savingUserId === user.id}
                        >
                          {ROLE_OPTIONS.map((role) => (
                            <option key={role} value={role}>
                              {getRoleLabel(role)}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
