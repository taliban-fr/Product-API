import re
from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel


class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True, min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=200)
    products: list[Product] = Relationship(back_populates="category")


class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    category_id: int | None = Field(default=None, foreign_key="category.id")
    category: Category | None = Relationship(back_populates="products")


class ProductCreate(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=10, max_length=500)
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)
    category_id: int | None = None

    @field_validator("name")
    def validate_name(cls, v):
        if not v[0].isupper():
            raise ValueError("Name must start with a capital letter")
        if not re.match(r"^[A-Za-z0-9\s\-]+$", v):
            raise ValueError("Name cannot contain special characters")
        if len(v.strip().split()) < 1:
            raise ValueError("Name must contain at least one word")
        return v


ALLOWED_BRANDS = [
    "HP",
    "Dell",
    "Lenovo",
    "Apple",
    "Samsung",
    "Intel",
    "AMD",
    "Corsair",
    "Logitech",
    "Other",
]

ALLOWED_CATEGORIES = [
    "Laptops",
    "Monitors",
    "Storage",
    "Processors",
    "Memory",
    "Keyboards",
    "Mice",
    "Accessories",
]


@field_validator("brand")
def validate_brand(cls, v):
    normalized = v.strip().upper()
    brand_map = {b.upper(): b for b in ALLOWED_BRANDS}
    if normalized not in brand_map:
        raise ValueError(f"Brand must be one of: {', '.join(ALLOWED_BRANDS)}")
    return brand_map[normalized]


class ProductUpdate(SQLModel):
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, min_length=10, max_length=500)
    price: float | None = Field(None, gt=0)
    stock: int | None = Field(None, ge=0)


class CategoryCreate(SQLModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(None, max_length=200)
