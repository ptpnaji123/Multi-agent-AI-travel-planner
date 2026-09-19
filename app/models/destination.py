from pydantic import BaseModel, Field


class DestinationResearch(BaseModel):
    destination: str

    best_season: str = ""

    neighborhoods: list[str] = Field(default_factory=list)

    must_see: list[str] = Field(default_factory=list)

    food: list[str] = Field(default_factory=list)

    visa_notes: list[str] = Field(default_factory=list)

    safety_notes: list[str] = Field(default_factory=list)

    local_transport: list[str] = Field(default_factory=list)