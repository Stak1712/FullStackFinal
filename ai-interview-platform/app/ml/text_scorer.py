from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple


_TOKEN_RE = re.compile(r"[a-zA-Zа-яА-Я0-9]+", re.UNICODE)


def _tokenize(text: str) -> List[str]:
    return _TOKEN_RE.findall(text.lower())


@dataclass
class NaiveBayesModel:
    classes: List[str]
    log_prior: Dict[str, float]
    log_likelihood: Dict[str, Dict[str, float]]
    vocab: List[str]


def _default_dataset() -> List[Tuple[str, str]]:
    return [
        ("Я бы оценил сложность O(n log n), использовал хеш-таблицу, описал крайние случаи и добавил тесты", "good"),
        ("Нужны транзакции, индексы, нормализация; я объясню почему и приведу пример запроса", "good"),
        ("Решение: BFS/DFS, учту память, сложность, и оптимизирую", "good"),
        ("Использую кэширование и мемоизацию, чтобы ускорить, и приведу пример", "good"),
        ("Можно сделать через сортировку и потом пройтись по массиву", "ok"),
        ("Я бы написал API на FastAPI, сделал эндпоинты и проверку ошибок", "ok"),
        ("Нужно хранить данные в базе и сделать авторизацию", "ok"),
        ("Ну просто сделаю как-нибудь", "bad"),
        ("Не знаю", "bad"),
        ("Скачаю готовое решение", "bad"),
    ]


def train(dataset: List[Tuple[str, str]] | None = None, alpha: float = 1.0) -> NaiveBayesModel:
    dataset = dataset or _default_dataset()
    classes = sorted({label for _, label in dataset})
    class_doc_counts: Dict[str, int] = {c: 0 for c in classes}
    class_word_counts: Dict[str, Dict[str, int]] = {c: {} for c in classes}
    class_total_words: Dict[str, int] = {c: 0 for c in classes}
    vocab_set = set()

    for text, label in dataset:
        class_doc_counts[label] += 1
        tokens = _tokenize(text)
        for t in tokens:
            vocab_set.add(t)
            class_total_words[label] += 1
            class_word_counts[label][t] = class_word_counts[label].get(t, 0) + 1

    vocab = sorted(vocab_set)
    total_docs = len(dataset)

    log_prior = {c: math.log((class_doc_counts[c] + 1) / (total_docs + len(classes))) for c in classes}

    log_likelihood: Dict[str, Dict[str, float]] = {c: {} for c in classes}
    V = len(vocab)
    for c in classes:
        denom = class_total_words[c] + alpha * V
        for w in vocab:
            cnt = class_word_counts[c].get(w, 0)
            prob = (cnt + alpha) / denom
            log_likelihood[c][w] = math.log(prob)

    return NaiveBayesModel(classes=classes, log_prior=log_prior, log_likelihood=log_likelihood, vocab=vocab)


def save(model: NaiveBayesModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "classes": model.classes,
        "log_prior": model.log_prior,
        "log_likelihood": model.log_likelihood,
        "vocab": model.vocab,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load(path: Path) -> NaiveBayesModel:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return NaiveBayesModel(
        classes=list(payload["classes"]),
        log_prior=dict(payload["log_prior"]),
        log_likelihood=dict(payload["log_likelihood"]),
        vocab=list(payload["vocab"]),
    )


def get_or_create_model() -> NaiveBayesModel:
    model_path = Path("data/ml_model.json")
    if model_path.exists():
        try:
            return load(model_path)
        except Exception:
            pass

    m = train()
    save(m, model_path)
    return m


def _softmax(logits: List[float]) -> List[float]:
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps) or 1.0
    return [e / s for e in exps]


def predict_proba(model: NaiveBayesModel, text: str) -> Dict[str, float]:
    tokens = _tokenize(text)
    tokens = [t for t in tokens if t in set(model.vocab)]

    logits = []
    for c in model.classes:
        score = model.log_prior[c]
        ll = model.log_likelihood[c]
        for t in tokens:
            score += ll.get(t, 0.0)
        logits.append(score)

    probs = _softmax(logits)
    return {c: p for c, p in zip(model.classes, probs)}


def score_answer(answer: str, question: str | None = None, direction: str | None = None) -> dict:
    model = get_or_create_model()
    probs = predict_proba(model, answer)
    p_good = probs.get("good", 0.0)
    score = int(round(p_good * 100))

    if score >= 70:
        verdict = "good"
    elif score >= 40:
        verdict = "ok"
    else:
        verdict = "bad"

    return {"score": score, "verdict": verdict}
