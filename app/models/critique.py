from pydantic import BaseModel, Field


class CritiqueReport(BaseModel):
    valid: bool = False

    errors: list[str] = Field(
        default_factory=list
    )

    warnings: list[str] = Field(
        default_factory=list
    )

    repair_required: bool = False

    repair_attempt: int = 0