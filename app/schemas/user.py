from pydantic import BaseModel, EmailStr


class SignUpModel(BaseModel):
    email: EmailStr
    password: str
    is_staff: bool  # type:ignore

    class Config:
        from_attributes = True


class LoginModel(BaseModel):
    email: str
    password: str
