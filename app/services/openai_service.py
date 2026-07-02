import json

from openai import OpenAI

from app.prompts import build_evaluation_prompt
from app.schemas import EssayEvaluationResult
from app.settings import settings

client = OpenAI(api_key=settings.openai_api_key)

CRITERIA_NAMES = [
    "SK1",
    "SK2",
    "SK3",
    "SK4",
    "GK1",
    "GK2",
    "GK3",
    "GK4",
    "FK1",
]


def build_criterion_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "score": {"type": "integer"},
            "explanation": {"type": "string"},
        },
        "required": ["score", "explanation"],
    }


EVALUATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "wordCount": {"type": "integer"},
        "notGraded": {"type": "boolean"},
        "notGradedReason": {"type": "string"},
        "totalScore": {"type": "integer"},
        "criteria": {
            "type": "object",
            "additionalProperties": False,
            "properties": {name: build_criterion_schema() for name in CRITERIA_NAMES},
            "required": CRITERIA_NAMES,
        },
        "overallComment": {"type": "string"},
    },
    "required": [
        "wordCount",
        "notGraded",
        "notGradedReason",
        "totalScore",
        "criteria",
        "overallComment",
    ],
}


def evaluate_essay(
    topic_title: str,
    topic_code: str,
    source_text: str,
    instructions: str,
    essay_text: str,
    word_count: int,
) -> tuple[EssayEvaluationResult, str]:
    prompt = build_evaluation_prompt(
        topic_title=topic_title,
        topic_code=topic_code,
        source_text=source_text,
        instructions=instructions,
        essay_text=essay_text,
        word_count=word_count,
    )

    response = client.responses.create(
        model=settings.openai_model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "oge_essay_evaluation",
                "strict": True,
                "schema": EVALUATION_SCHEMA,
            }
        },
    )

    raw_text = response.output_text
    parsed = json.loads(raw_text)
    result = EssayEvaluationResult.model_validate(parsed)

    return result, raw_text