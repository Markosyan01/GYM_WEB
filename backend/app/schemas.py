from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    token: str


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    price: float
    features: list[str]


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    plan: PlanOut | None = None


class TrainerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    specialty: str
    bio: str
    image: str = ""


class ClassOut(BaseModel):
    id: int
    title: str
    description: str
    day: str
    start: str
    trainer: str
    capacity: int
    booked: int
    joined: bool
    image: str = ""
