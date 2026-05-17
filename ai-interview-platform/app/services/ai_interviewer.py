from __future__ import annotations

import random
from typing import Dict, List, Optional

from app.ml.text_scorer import score_answer


SKILL_ALIASES: Dict[str, str] = {
    "python": "python",
    "fastapi": "fastapi",
    "react": "react",
    "typescript": "typescript",
    "sql": "sql",
    "docker": "docker",
    "git": "git",
    "алгоритмы": "algorithms",
    "ооп": "oop",
    "system design": "system_design",
    "system_design": "system_design",
}


def normalize_grade(grade: str) -> str:
    g = (grade or "").strip().lower()
    mapping = {
        "junior": "junior",
        "jr": "junior",
        "джуниор": "junior",
        "джун": "junior",
        "middle": "middle",
        "mid": "middle",
        "мидл": "middle",
        "мид": "middle",
        "senior": "senior",
        "sr": "senior",
        "сеньор": "senior",
        "сень": "senior",
    }
    return mapping.get(g, "junior")


def normalize_skills(skills: List[str]) -> List[str]:
    out: List[str] = []
    for s in skills or []:
        key = SKILL_ALIASES.get((s or "").strip().lower())
        if key and key not in out:
            out.append(key)
    return out


QUESTION_BANK: List[dict] = [
    {"id": "python_easy_1", "skill": "python", "level": "easy", "text": "В чём разница между list и tuple в Python и когда что выбирать?", "keywords": ["list", "tuple", "измен", "immutable"]},
    {"id": "python_easy_2", "skill": "python", "level": "easy", "text": "Что такое исключения в Python и как работает try/except/finally?", "keywords": ["try", "except", "finally", "exception"]},
    {"id": "python_med_1", "skill": "python", "level": "medium", "text": "Что такое генераторы и в чём отличие generator от list comprehension?", "keywords": ["yield", "generator", "lazy"]},
    {"id": "python_med_2", "skill": "python", "level": "medium", "text": "Как работает GIL и когда он мешает?", "keywords": ["gil", "thread", "cpu"]},
    {"id": "python_hard_1", "skill": "python", "level": "hard", "text": "Как бы вы оптимизировали медленный Python‑код: профилирование, алгоритм, структуры данных?", "keywords": ["profile", "complexity", "cache", "dict"]},

    {"id": "fastapi_easy_1", "skill": "fastapi", "level": "easy", "text": "Как устроен роутинг в FastAPI и что такое APIRouter?", "keywords": ["router", "endpoint", "path"]},
    {"id": "fastapi_easy_2", "skill": "fastapi", "level": "easy", "text": "Чем отличается Depends от обычного вызова функции и зачем dependency injection?", "keywords": ["depends", "dependency", "injection"]},
    {"id": "fastapi_med_1", "skill": "fastapi", "level": "medium", "text": "Как в FastAPI реализовать валидацию входных данных и обработку ошибок?", "keywords": ["pydantic", "validation", "httpexception"]},
    {"id": "fastapi_med_2", "skill": "fastapi", "level": "medium", "text": "Как устроены middleware в FastAPI и какие задачи ими решают?", "keywords": ["middleware", "request", "response"]},
    {"id": "fastapi_hard_1", "skill": "fastapi", "level": "hard", "text": "Как бы вы спроектировали JWT‑аутентификацию и refresh‑токены, чтобы было безопасно?", "keywords": ["jwt", "refresh", "cookie", "storage"]},

    {"id": "sql_easy_1", "skill": "sql", "level": "easy", "text": "Что такое первичный ключ и внешний ключ?", "keywords": ["primary", "foreign", "key"]},
    {"id": "sql_easy_2", "skill": "sql", "level": "easy", "text": "Зачем нужны индексы и когда они вредят?", "keywords": ["index", "plan", "write"]},
    {"id": "sql_med_1", "skill": "sql", "level": "medium", "text": "Что такое нормализация и какие проблемы решает 3НФ?", "keywords": ["normalization", "3nf", "redundancy"]},
    {"id": "sql_med_2", "skill": "sql", "level": "medium", "text": "Как работают транзакции и уровни изоляции?", "keywords": ["transaction", "isolation", "acid"]},
    {"id": "sql_hard_1", "skill": "sql", "level": "hard", "text": "Как вы находите и оптимизируете медленные запросы (EXPLAIN, индексы, план)?", "keywords": ["explain", "plan", "index", "join"]},

    {"id": "docker_easy_1", "skill": "docker", "level": "easy", "text": "Что такое Docker image и container, чем они отличаются?", "keywords": ["image", "container", "layer"]},
    {"id": "docker_easy_2", "skill": "docker", "level": "easy", "text": "Зачем нужен docker-compose и что обычно описывают в compose.yml?", "keywords": ["compose", "service", "port"]},
    {"id": "docker_med_1", "skill": "docker", "level": "medium", "text": "Как уменьшить размер Docker‑образа и ускорить сборку?", "keywords": ["multistage", "cache", "slim"]},
    {"id": "docker_med_2", "skill": "docker", "level": "medium", "text": "Как безопасно хранить секреты (пароли, ключи) в Docker‑окружении?", "keywords": ["secret", "env", "vault"]},
    {"id": "docker_hard_1", "skill": "docker", "level": "hard", "text": "Что такое healthcheck и как его использовать при деплое?", "keywords": ["health", "check", "readiness"]},

    {"id": "react_easy_1", "skill": "react", "level": "easy", "text": "Что такое state и props в React и чем они отличаются?", "keywords": ["state", "props", "component"]},
    {"id": "react_easy_2", "skill": "react", "level": "easy", "text": "Зачем нужен React Router и что такое Route/Link?", "keywords": ["router", "route", "link"]},
    {"id": "react_med_1", "skill": "react", "level": "medium", "text": "Как работает useEffect и какие типичные ошибки с зависимостями?", "keywords": ["useeffect", "dependency", "render"]},
    {"id": "react_med_2", "skill": "react", "level": "medium", "text": "Что такое controlled components и зачем это нужно?", "keywords": ["controlled", "input", "value"]},
    {"id": "react_hard_1", "skill": "react", "level": "hard", "text": "Как вы оптимизируете React‑приложение (memo, virtualization, split)?", "keywords": ["memo", "bundle", "virtual"]},

    {"id": "ts_easy_1", "skill": "typescript", "level": "easy", "text": "Зачем нужен TypeScript и какие основные преимущества?", "keywords": ["types", "compile", "safety"]},
    {"id": "ts_easy_2", "skill": "typescript", "level": "easy", "text": "В чём разница между interface и type?", "keywords": ["interface", "type", "extend"]},
    {"id": "ts_med_1", "skill": "typescript", "level": "medium", "text": "Что такое generics в TypeScript и где их применяют?", "keywords": ["generic", "<t>", "type"]},
    {"id": "ts_med_2", "skill": "typescript", "level": "medium", "text": "Как работает narrowing (type guards) в TypeScript?", "keywords": ["narrow", "guard", "typeof"]},
    {"id": "ts_hard_1", "skill": "typescript", "level": "hard", "text": "Как вы типизируете сложный API‑ответ и обеспечиваете совместимость версий?", "keywords": ["api", "schema", "version"]},

    {"id": "git_easy_1", "skill": "git", "level": "easy", "text": "Чем отличается merge от rebase и когда что использовать?", "keywords": ["merge", "rebase", "history"]},
    {"id": "git_easy_2", "skill": "git", "level": "easy", "text": "Что такое pull request и зачем нужны code review?", "keywords": ["pull", "review", "branch"]},
    {"id": "git_med_1", "skill": "git", "level": "medium", "text": "Как откатить ошибочный commit, если он уже попал в удалённую ветку?", "keywords": ["revert", "reset", "push"]},
    {"id": "git_hard_1", "skill": "git", "level": "hard", "text": "Как вы организуете git‑flow или trunk‑based development и почему?", "keywords": ["flow", "trunk", "release"]},

    {"id": "algo_easy_1", "skill": "algorithms", "level": "easy", "text": "Оцените сложность поиска в отсортированном массиве. Какой алгоритм выберете?", "keywords": ["binary", "log", "complexity"]},
    {"id": "algo_easy_2", "skill": "algorithms", "level": "easy", "text": "Чем стек отличается от очереди и где используются?", "keywords": ["stack", "queue", "fifo"]},
    {"id": "algo_med_1", "skill": "algorithms", "level": "medium", "text": "Объясните разницу между BFS и DFS и когда что лучше.", "keywords": ["bfs", "dfs", "graph"]},
    {"id": "algo_hard_1", "skill": "algorithms", "level": "hard", "text": "Как найти k‑й по величине элемент в массиве эффективнее сортировки?", "keywords": ["quickselect", "heap", "kth"]},

    {"id": "oop_easy_1", "skill": "oop", "level": "easy", "text": "Назовите 4 принципа ООП и коротко объясните их.", "keywords": ["инкапс", "наслед", "полимор", "абстрак"]},
    {"id": "oop_easy_2", "skill": "oop", "level": "easy", "text": "Чем отличается интерфейс от абстрактного класса?", "keywords": ["interface", "abstract", "method"]},
    {"id": "oop_med_1", "skill": "oop", "level": "medium", "text": "Что такое SOLID и приведите пример нарушения и исправления?", "keywords": ["solid", "srp", "ocp"]},
    {"id": "oop_hard_1", "skill": "oop", "level": "hard", "text": "Какие паттерны (Factory/Strategy/Observer) вы применяли и зачем?", "keywords": ["pattern", "factory", "strategy"]},

    {"id": "sd_easy_1", "skill": "system_design", "level": "easy", "text": "Что такое REST и какие есть альтернативы (RPC/GraphQL), когда их выбирают?", "keywords": ["rest", "graphql", "rpc"]},
    {"id": "sd_med_1", "skill": "system_design", "level": "medium", "text": "Как обеспечивать идемпотентность запросов и защищаться от дублей?", "keywords": ["idempot", "retry", "dedup"]},
    {"id": "sd_hard_1", "skill": "system_design", "level": "hard", "text": "Как спроектировать сервис интервью: хранение сессий, масштабирование, очереди?", "keywords": ["scale", "cache", "queue", "db"]},
]


_BY_ID = {q["id"]: q for q in QUESTION_BANK}


def get_question_by_id(qid: str) -> Optional[dict]:
    return _BY_ID.get(qid)


def _coverage(text: str, keywords: List[str]) -> int:
    if not keywords:
        return 50
    t = (text or "").lower()
    hit = sum(1 for k in keywords if (k or "").lower() in t)
    return int(round(100 * hit / len(keywords)))


def _difficulty_from_score(score: int) -> str:
    if score >= 70:
        return "hard"
    if score >= 40:
        return "medium"
    return "easy"


def _cap_level_for_grade(level: str, grade: str) -> str:
    g = normalize_grade(grade)
    if g == "junior" and level == "hard":
        return "medium"
    return level


def _skill_counts(asked_ids: List[str]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for qid in asked_ids:
        q = get_question_by_id(qid)
        if not q:
            continue
        sk = q.get("skill")
        if not sk:
            continue
        counts[sk] = counts.get(sk, 0) + 1
    return counts


def pick_next_question(
    *,
    grade: str,
    skills: List[str],
    asked_ids: List[str],
    prev_score: Optional[int] = None,
    prev_skill: Optional[str] = None,
) -> dict:
    g = normalize_grade(grade)
    s_norm = normalize_skills(skills)
    if not s_norm:
        s_norm = ["python", "fastapi", "sql"]

    counts = _skill_counts(asked_ids)

    target_skill: Optional[str] = None
    if prev_score is not None and prev_score < 40 and prev_skill in s_norm:
        target_skill = prev_skill
    if target_skill is None:
        target_skill = min(s_norm, key=lambda sk: counts.get(sk, 0))

    desired_level = "medium" if prev_score is None else _difficulty_from_score(prev_score)
    desired_level = _cap_level_for_grade(desired_level, g)

    def candidates(skill: Optional[str], level: Optional[str]) -> List[dict]:
        out: List[dict] = []
        for q in QUESTION_BANK:
            if q["id"] in asked_ids:
                continue
            if skill and q.get("skill") != skill:
                continue
            if level and q.get("level") != level:
                continue
            out.append(q)
        return out

    pool = candidates(target_skill, desired_level)
    if not pool:
        pool = candidates(target_skill, None)
    if not pool:
        for sk in s_norm:
            pool = candidates(sk, desired_level)
            if pool:
                break
    if not pool:
        pool = candidates(None, None)
    if not pool:
        return random.choice(QUESTION_BANK)

    return random.choice(pool)


def evaluate_answer(answer_text: str, question: dict, direction: Optional[str] = None) -> dict:
    ml = score_answer(answer_text, question=question.get("text"), direction=direction)
    kw = _coverage(answer_text, question.get("keywords", []))
    score = int(round(0.7 * ml["score"] + 0.3 * kw))

    if score >= 70:
        verdict = "good"
    elif score >= 40:
        verdict = "ok"
    else:
        verdict = "bad"

    return {"score": score, "verdict": verdict}
