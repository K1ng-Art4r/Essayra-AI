import hashlib
import hmac
import os
import random
import re
from typing import Optional

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select, or_
from starlette.middleware.sessions import SessionMiddleware

from app.db import create_db_and_tables, get_session
from app.models import EssayAttempt, EssayTopic, TaskSet, User
from app.seed import seed_task_sets
from app.services.openai_service import evaluate_essay
from app.settings import settings

app = FastAPI(title="AI OGE")
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=False,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static",
)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+(?:-[A-Za-zА-Яа-яЁё0-9]+)*")

CRITERIA_META = [
    ("SK1", "Наличие ответа на вопрос"),
    ("SK2", "Наличие примеров"),
    ("SK3", "Логичность речи"),
    ("SK4", "Композиционная стройность"),
    ("GK1", "Соблюдение орфографических норм"),
    ("GK2", "Соблюдение пунктуационных норм"),
    ("GK3", "Соблюдение грамматических норм"),
    ("GK4", "Соблюдение речевых норм"),
    ("FK1", "Фактическая точность речи"),
]


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_task_sets()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    )
    return f"{salt.hex()}:{password_hash.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_hash = bytes.fromhex(hash_hex)
    except ValueError:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000
    )
    return hmac.compare_digest(password_hash, expected_hash)


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def get_topics_for_task_set(session: Session, task_set_id: int) -> list[EssayTopic]:
    return session.exec(
        select(EssayTopic)
        .where(EssayTopic.task_set_id == task_set_id)
        .order_by(EssayTopic.order_index)
    ).all()


def get_random_task_set(session: Session) -> tuple[Optional[TaskSet], list[EssayTopic]]:
    task_sets = session.exec(select(TaskSet)).all()
    if not task_sets:
        return None, []

    task_set = random.choice(task_sets)
    topics = get_topics_for_task_set(session, task_set.id)
    return task_set, topics


def build_criteria_rows(result) -> list[dict]:
    return [
        {
            "code": code,
            "title": title,
            "score": getattr(result.criteria, code).score,
            "explanation": getattr(result.criteria, code).explanation,
        }
        for code, title in CRITERIA_META
    ]


def get_current_user(request: Request, session: Session) -> Optional[User]:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return session.get(User, user_id)


def require_user(request: Request, session: Session) -> User:
    user = get_current_user(request, session)
    if user is None:
        raise PermissionError("auth_required")
    return user


def render_index(
    request: Request,
    task_set: Optional[TaskSet],
    topics: list[EssayTopic],
    current_user: User,
    essay_text: str = "",
    error: Optional[str] = None,
    selected_topic_id: Optional[int] = None,
):
    if selected_topic_id is None and topics:
        selected_topic_id = topics[0].id

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "task_set": task_set,
            "topics": topics,
            "essay_text": essay_text,
            "error": error,
            "selected_topic_id": selected_topic_id,
            "current_user": current_user,
        },
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, session: Session = Depends(get_session)):
    current_user = get_current_user(request, session)
    if current_user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error": None,
            "current_user": None,
        },
    )


@app.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    login_value: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    login_value = login_value.strip()

    user = session.exec(
        select(User).where(
            or_(
                User.email == login_value,
                User.nickname == login_value,
            )
        )
    ).first()

    if user is None or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "error": "Неверный логин или пароль.",
                "current_user": None,
            },
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request, session: Session = Depends(get_session)):
    current_user = get_current_user(request, session)
    if current_user:
        return RedirectResponse(url="/", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "error": None,
            "current_user": None,
        },
    )


@app.post("/register", response_class=HTMLResponse)
def register(
    request: Request,
    email: str = Form(...),
    nickname: str = Form(...),
    password: str = Form(...),
    password_repeat: str = Form(...),
    session: Session = Depends(get_session),
):
    email = email.strip().lower()
    nickname = nickname.strip()

    if not email or not nickname or not password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Все поля обязательны.",
                "current_user": None,
            },
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Пароль должен содержать минимум 6 символов.",
                "current_user": None,
            },
        )

    if password != password_repeat:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Пароли не совпадают.",
                "current_user": None,
            },
        )

    existing_user = session.exec(
        select(User).where(
            or_(
                User.email == email,
                User.nickname == nickname,
            )
        )
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Пользователь с таким email или nickname уже существует.",
                "current_user": None,
            },
        )

    user = User(
        email=email,
        nickname=nickname,
        password_hash=hash_password(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    try:
        current_user = require_user(request, session)
    except PermissionError:
        return RedirectResponse(url="/login", status_code=303)

    task_set, topics = get_random_task_set(session)

    if task_set is None:
        return render_index(
            request=request,
            task_set=None,
            topics=[],
            current_user=current_user,
            error="В базе пока нет заданий. Добавь их в app/data/task_sets.py и перезапусти приложение.",
        )

    return render_index(
        request=request,
        task_set=task_set,
        topics=topics,
        current_user=current_user,
    )


@app.get("/task/random", response_class=HTMLResponse)
def random_task(request: Request, session: Session = Depends(get_session)):
    try:
        current_user = require_user(request, session)
    except PermissionError:
        return RedirectResponse(url="/login", status_code=303)

    task_set, topics = get_random_task_set(session)

    if task_set is None:
        return render_index(
            request=request,
            task_set=None,
            topics=[],
            current_user=current_user,
            error="В базе пока нет заданий. Добавь их в app/data/task_sets.py и перезапусти приложение.",
        )

    return render_index(
        request=request,
        task_set=task_set,
        topics=topics,
        current_user=current_user,
    )


@app.post("/evaluate", response_class=HTMLResponse)
def evaluate(
    request: Request,
    topic_id: int = Form(...),
    essay_text: str = Form(...),
    session: Session = Depends(get_session),
):
    try:
        current_user = require_user(request, session)
    except PermissionError:
        return RedirectResponse(url="/login", status_code=303)

    topic = session.get(EssayTopic, topic_id)

    if topic is None:
        task_set, topics = get_random_task_set(session)
        return render_index(
            request=request,
            task_set=task_set,
            topics=topics,
            current_user=current_user,
            essay_text=essay_text,
            error="Выбранная тема не найдена.",
        )

    task_set = session.get(TaskSet, topic.task_set_id)
    topics = get_topics_for_task_set(session, topic.task_set_id)

    if task_set is None:
        return render_index(
            request=request,
            task_set=None,
            topics=[],
            current_user=current_user,
            essay_text=essay_text,
            error="Исходный текст для выбранной темы не найден.",
            selected_topic_id=topic_id,
        )

    if len(essay_text.strip()) < 10:
        return render_index(
            request=request,
            task_set=task_set,
            topics=topics,
            current_user=current_user,
            essay_text=essay_text,
            error="Слишком короткий ввод. Напиши сочинение полностью.",
            selected_topic_id=topic_id,
        )

    word_count = count_words(essay_text)

    try:
        result, raw_json = evaluate_essay(
            topic_title=topic.title,
            topic_code=topic.topic_code,
            source_text=task_set.source_text,
            instructions=task_set.instructions,
            essay_text=essay_text,
            word_count=word_count,
        )

        attempt = EssayAttempt(
            user_id=current_user.id,
            task_set_id=task_set.id,
            topic_id=topic.id,
            topic_code=topic.topic_code,
            topic_title=topic.title,
            source_text=task_set.source_text,
            essay_text=essay_text,
            word_count=result.wordCount,
            not_graded=result.notGraded,
            not_graded_reason=result.notGradedReason,
            total_score=result.totalScore,
            sk1=result.criteria.SK1.score,
            sk2=result.criteria.SK2.score,
            sk3=result.criteria.SK3.score,
            sk4=result.criteria.SK4.score,
            gk1=result.criteria.GK1.score,
            gk2=result.criteria.GK2.score,
            gk3=result.criteria.GK3.score,
            gk4=result.criteria.GK4.score,
            fk1=result.criteria.FK1.score,
            overall_comment=result.overallComment,
            raw_model_json=raw_json,
        )
        session.add(attempt)
        session.commit()

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "task_set": task_set,
                "topic": topic,
                "essay_text": essay_text,
                "result": result,
                "criteria_rows": build_criteria_rows(result),
                "current_user": current_user,
            },
        )

    except Exception as e:
        return render_index(
            request=request,
            task_set=task_set,
            topics=topics,
            current_user=current_user,
            essay_text=essay_text,
            error=f"Ошибка при проверке сочинения: {str(e)}",
            selected_topic_id=topic_id,
        )


@app.get("/new")
def new_attempt(request: Request, session: Session = Depends(get_session)):
    current_user = get_current_user(request, session)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return RedirectResponse(url="/task/random", status_code=303)