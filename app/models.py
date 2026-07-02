from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    nickname: str = Field(index=True, unique=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskSet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source_text: str
    instructions: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EssayTopic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_set_id: int = Field(foreign_key="taskset.id", index=True)
    topic_code: str
    title: str
    order_index: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EssayAttempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key="user.id", index=True)
    task_set_id: int = Field(foreign_key="taskset.id", index=True)
    topic_id: int = Field(foreign_key="essaytopic.id", index=True)

    topic_code: str
    topic_title: str

    source_text: str
    essay_text: str

    word_count: int
    not_graded: bool = False
    not_graded_reason: str = ""

    total_score: int

    sk1: int
    sk2: int
    sk3: int
    sk4: int

    gk1: int
    gk2: int
    gk3: int
    gk4: int

    fk1: int

    overall_comment: str
    raw_model_json: str

    created_at: datetime = Field(default_factory=datetime.utcnow)