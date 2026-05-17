import Seo from "../seo/Seo";

const AboutPage = () => {
  return (
    <section className="page-wrapper">
      <Seo
        title="О платформе AI Interview Platform"
        description="AI Interview Platform помогает готовиться к техническим собеседованиям в безопасном формате с виртуальным интервьюером."
        canonicalPath="/about"
      />
      <div className="page-content">
        <h1>О нас</h1>
        <p className="page-subtitle">
          Наша платформа помогает готовиться к техническим собеседованиям в
          безопасном формате с виртуальным интервьюером.
        </p>
        <p>
          Вы заполняете профиль, выбираете направление и проходите интервью с
          ИИ: он задаёт вопросы, анализирует ответы и формирует обратную
          связь. Это удобный способ потренироваться перед реальным собеседованием.
        </p>
      </div>
    </section>
  );
};

export default AboutPage;
