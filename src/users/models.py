from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    status: bool | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str
