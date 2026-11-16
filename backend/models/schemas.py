from pydantic import BaseModel, ConfigDict, Field


class StrictContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
    )


class AnalyzeRequest(BaseModel):
    question: str = Field(min_length=3, max_length=5000)


class SurveyRequest(BaseModel):
    rating_ocr: int = Field(ge=1, le=5)
    rating_socratic: int = Field(ge=1, le=5)
    rating_overall: int = Field(ge=1, le=5)


class VariableItem(StrictContractModel):
    name: str = Field(min_length=1)
    val: str = Field(min_length=1)


class SocraticCard(StrictContractModel):
    question: str = Field(min_length=1)
    hint: str = Field(min_length=1)
    checkpoint: str = Field(min_length=1)


class SolutionStep(StrictContractModel):
    title: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class AnalyzeResponse(StrictContractModel):
    answer: str = Field(min_length=1)
    vars: list[VariableItem]
    socraticCards: list[SocraticCard]
    steps: list[SolutionStep]
    pdfRef: str = Field(min_length=1)
