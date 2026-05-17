import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Seo from "../seo/Seo";

const LoginPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!email.trim() || !password) {
      setError("Заполните email и пароль");
      return;
    }

    try {
      setLoading(true);
      await login(email.trim(), password);
      navigate("/profile");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || "Ошибка входа";
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-wrapper">
      <Seo title="Вход" description="Вход в личный кабинет AI Interview Platform." noIndex />
      <div className="auth-card">
        <h2>Вход</h2>

        {error ? <p className="form-error">{error}</p> : null}

        <form className="form" onSubmit={onSubmit}>
          <label className="form-field">
            <span>Email</span>
            <input
              type="email"
              placeholder="example@mail.ru"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </label>
          <label className="form-field">
            <span>Пароль</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </label>
          <button disabled={loading} type="submit" className="btn btn-primary form-submit">
            {loading ? "Входим..." : "Войти"}
          </button>
        </form>

        <p className="auth-hint">
          Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
        </p>
      </div>
    </section>
  );
};

export default LoginPage;
