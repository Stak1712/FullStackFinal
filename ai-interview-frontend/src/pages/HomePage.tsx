import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import Seo from "../seo/Seo";

const HomePage = () => {
  const navigate = useNavigate();
  const { isAuth } = useAuth();

  return (
    <section className="hero">
      <Seo
        title="ИИ-платформа для технических собеседований"
        description="Тренируйтесь с виртуальным интервьюером: загрузите резюме, выберите навыки и получите обратную связь перед реальным техническим собеседованием."
        canonicalPath="/"
        jsonLd={{
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          name: "AI Interview Platform",
          applicationCategory: "EducationalApplication",
          operatingSystem: "Web",
          description: "ИИ-платформа для прохождения тренировочных технических собеседований.",
        }}
      />
      <div className="hero-content">
        <h1>ИИ-платформа для прохождения технических собеседований</h1>
        <p>
          Тренируйся с виртуальным интервьюером, а ролевой доступ защищает пользовательские сценарии,
          служебные разделы и управление ролями.
        </p>
        <button className="btn btn-primary" onClick={() => navigate(isAuth ? "/profile" : "/login")}>
          {isAuth ? "Перейти в профиль" : "Войти и начать"}
        </button>
      </div>
    </section>
  );
};

export default HomePage;
