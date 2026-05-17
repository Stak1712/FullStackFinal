import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { getDisplayName } from "../auth/access";

export default function Navbar() {
  const navigate = useNavigate();
  const { isAuth, user, logout, hasRole } = useAuth();

  const onLogout = async () => {
    await logout();
    navigate("/login");
  };

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `nav-link ${isActive ? "nav-link-active" : ""}`;

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <NavLink to="/" className="nav-logo">
          AI
        </NavLink>

        <nav className="nav-links">
          <NavLink to="/" className={linkClass}>
            Главная
          </NavLink>

          <NavLink to="/ai" className={linkClass}>
            ИИ
          </NavLink>

          <NavLink to="/directions" className={linkClass}>
            Направления
          </NavLink>

          <NavLink to="/about" className={linkClass}>
            О платформе
          </NavLink>

          <NavLink to="/resources" className={linkClass}>
            Материалы
          </NavLink>

          {isAuth && (
            <NavLink to="/resume" className={linkClass}>
              Начать интервью
            </NavLink>
          )}

          {hasRole("admin") && (
            <NavLink to="/admin/users" className={linkClass}>
              Админ-панель
            </NavLink>
          )}
        </nav>

        <div className="nav-right">
          {isAuth ? (
            <>
              <NavLink to="/profile" className="nav-user">
                {getDisplayName(user)}
              </NavLink>

              <button type="button" className="btn-ghost" onClick={() => void onLogout()}>
                Выйти
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn-ghost">
                Войти
              </NavLink>

              <NavLink to="/register" className="btn-primary">
                Регистрация
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
