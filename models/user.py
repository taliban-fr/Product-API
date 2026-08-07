from sqlmodel import SQLModel, Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: Optional[str] = None


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None