from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    full_name: str | None = None


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    full_name: str | None = None


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    full_name: str | None = None
