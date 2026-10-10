from pydantic import BaseModel, Field


class GeneratedAttackSchema(BaseModel):
    name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    description: str = Field(min_length=1)
    payload: str = Field(min_length=1)
    severity: str = Field(pattern="^(low|medium|high|critical)$")


class GeneratedAttackResponse(BaseModel):
    attacks: list[GeneratedAttackSchema] = Field(min_length=1)
