import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Seo from "../seo/Seo";

const RegisterPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);

    if (!firstName.trim() || !lastName.trim() || !email.trim() || !password) {
      setError("Заполните все поля");
      return;
    }

    if (password.length < 6) {
      setError("Пароль должен быть минимум 6 символов");
      return;
    }

    try {
      setLoading(true);
      await register(firstName.trim(), lastName.trim(), email.trim(), password);
      navigate("/profile");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || "Ошибка регистрации";
      setError(String(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-wrapper">
      <Seo title="Регистрация" description="Создание аккаунта AI Interview Platform." noIndex />
      <div className="auth-card">
        <h2>Регистрация</h2>

        {error ? <p className="form-error">{error}</p> : null}

        <form className="form" onSubmit={onSubmit}>
          <label className="form-field">
            <span>Имя</span>
            <input value={firstName} onChange={(e) => setFirstName(e.target.value)} type="text" />
          </label>
          <label className="form-field">
            <span>Фамилия</span>
            <input value={lastName} onChange={(e) => setLastName(e.target.value)} type="text" />
          </label>
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
              autoComplete="new-password"
            />
          </label>
          <button disabled={loading} type="submit" className="btn btn-primary form-submit">
            {loading ? "Создаём..." : "Создать аккаунт"}
          </button>
        </form>

        <p className="auth-hint">
          Уже есть аккаунт? <Link to="/login">Войти</Link>
        </p>
      </div>
    </section>
  );
};

export default RegisterPage;
