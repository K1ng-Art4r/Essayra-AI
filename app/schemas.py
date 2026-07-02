from pydantic import BaseModel, Field


class CriterionResult(BaseModel):
    score: int = Field(ge=0)
    explanation: str


class CriteriaResult(BaseModel):
    SK1: CriterionResult
    SK2: CriterionResult
    SK3: CriterionResult
    SK4: CriterionResult
    GK1: CriterionResult
    GK2: CriterionResult
    GK3: CriterionResult
    GK4: CriterionResult
    FK1: CriterionResult


class EssayEvaluationResult(BaseModel):
    wordCount: int = Field(ge=0)
    notGraded: bool = False
    notGradedReason: str = ""
    totalScore: int = Field(ge=0)
    criteria: CriteriaResult
    overallComment: str