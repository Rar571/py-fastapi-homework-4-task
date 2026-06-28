from datetime import date
from pydantic import BaseModel, field_validator
from database.models.accounts import GenderEnum
from validation import (
    validate_name,
    validate_gender,
    validate_birth_date,
)


class ProfileCreateSchema(BaseModel):
    first_name: str
    last_name: str
    gender: GenderEnum
    date_of_birth: date
    info: str
    avatar: str | None = None
    user_id: int | None = None
    model_config = {"from_attributes": True}

    @field_validator("first_name")
    @classmethod
    def check_first_name(cls, v):
        validate_name(v)

        return v.lower()

    @field_validator("last_name")
    @classmethod
    def check_last_name(cls, v):
        validate_name(v)
        return v.lower()

    @field_validator("date_of_birth")
    @classmethod
    def check_birth_date(cls, v):
        validate_birth_date(v)
        return v
