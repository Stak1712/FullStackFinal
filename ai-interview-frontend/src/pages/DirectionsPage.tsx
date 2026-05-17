import Seo from "../seo/Seo";

const DirectionsPage = () => {
  const mockDirections = [
    "Backend (Python, FastAPI)",
    "Frontend (React, TypeScript)",
    "Data Science",
    "DevOps / SRE",
    "Mobile (Kotlin / Swift)",
  ];

  return (
    <section className="page-wrapper">
      <Seo
        title="Направления технических интервью"
        description="Список направлений для тренировки технических собеседований: Backend, Frontend, Data Science, DevOps и Mobile."
        canonicalPath="/directions"
      />
      <div className="page-content">
        <h1>Список направлений</h1>
        <p className="page-subtitle">
          Выберите направление, по которому хотите пройти техническое интервью.
        </p>

        <ol className="directions-list-numbered">
          {mockDirections.map((d, i) => (
            <li key={i} className="directions-item-numbered">
              {d}
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
};

export default DirectionsPage;
