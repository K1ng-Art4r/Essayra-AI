from sqlmodel import Session, select

from app.db import engine
from app.data.task_sets import TASK_SETS
from app.models import TaskSet, EssayTopic


def seed_task_sets() -> None:
    with Session(engine) as session:
        existing = session.exec(select(TaskSet)).first()
        if existing:
            return

        for item in TASK_SETS:
            task_set = TaskSet(
                source_text=item["source_text"].strip(),
                instructions=item["instructions"].strip(),
            )
            session.add(task_set)
            session.flush()

            topics = item.get("topics", [])
            for idx, topic in enumerate(topics, start=1):
                session.add(
                    EssayTopic(
                        task_set_id=task_set.id,
                        topic_code=topic["topic_code"].strip(),
                        title=topic["title"].strip(),
                        order_index=idx,
                    )
                )

        session.commit()