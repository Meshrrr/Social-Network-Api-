from pydantic import BaseModel, EmailStr, ConfigDict


class createUser(BaseModel):
    username: str
    email: str
    password: str

class UserSchema(BaseModel):
    #Должны быть указаны типы которые мы передали:
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    is_active: bool = True