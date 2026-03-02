from pydantic import BaseModel, EmailStr, Field


class LoginDto(BaseModel):
    email: str | None = None
    username: str | None = None
    password: str


class RegisterDto(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None
    firstName: str | None = None
    lastName: str | None = None


class SignupDto(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    firstName: str
    lastName: str
    username: str


class ChangePasswordDto(BaseModel):
    oldPassword: str
    newPassword: str


class AuthResponse(BaseModel):
    accessToken: str
    user: dict
