import re

from pydantic import BaseModel, EmailStr, Field, field_validator

_PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d]).{8,}$")


def _validate_password_strength(v: str) -> str:
    if not _PASSWORD_RE.match(v):
        raise ValueError(
            "Password must be at least 8 characters and contain uppercase, lowercase, "
            "a digit, and a special character."
        )
    return v


class LoginDto(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str


class RegisterDto(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    username: str | None = None
    firstName: str | None = None
    lastName: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class SignupDto(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    firstName: str
    lastName: str
    username: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class ChangePasswordDto(BaseModel):
    oldPassword: str
    newPassword: str = Field(min_length=8)

    @field_validator("newPassword")
    @classmethod
    def password_strength(cls, v: str) -> str:
        return _validate_password_strength(v)


class RefreshTokenDto(BaseModel):
    refreshToken: str


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: dict
