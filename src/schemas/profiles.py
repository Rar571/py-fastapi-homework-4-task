from datetime import date
from fastapi import UploadFile, Form, File, HTTPException
from pydantic import BaseModel, field_validator, HttpUrl
from database.models.accounts import GenderEnum
from validation import (
    validate_name,
    validate_image,
    validate_gender,
    validate_birth_date
)

class ProfileCreateSchema(BaseModel):
    first_name: str
    @field_validator("first_name")
    @classmethod
    def check_english_letters(cls, first_name: str):
        validate_name(first_name)
        return first_name
    last_name: str
    @field_validator("last_name")
    @classmethod
    def check_english_letters(cls, last_name: str):
        validate_name(last_name)
        return last_name
    gender: GenderEnum
    @field_validator("gender")
    @classmethod
    def check_gender(cls, gender: str):
        validate_gender(gender)
        return gender
    date_of_birth: date
    @field_validator("date_of_birth")
    @classmethod
    def check_date_of_birth(cls, date_of_birth: date):
        validate_birth_date(date_of_birth)
        return date_of_birth
    info: str
    @field_validator("info")
    @classmethod
    def check_info(cls, info: str):
        if not info or not info.strip():
            raise ValueError("Info can not be empty or consist only of spaces")
        return info
