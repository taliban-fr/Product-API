from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from database.session import get_session, create_db_and_tables
from models.product import Product, ProductCreate, ProductUpdate, Category, CategoryCreate
from models.user import User, UserCreate, UserRead
from auth import hash_password, verify_password, create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
import time
import platform
import psutil
import logging
from logging.handlers import RotatingFileHandler
import os
from fastapi import Request

LOG_FILE = os.getenv("LOG_FILE", "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Catalog API", version="1.0.0")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_start = time.time()
    response = await call_next(request)
    process_time = time.time() - request_start
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    return response

start_time = time.time()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ============================================================
# AUTH
# ============================================================

@app.post("/register", response_model=UserRead, status_code=201)
def register(user: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    existing = session.exec(select(User).where(User.username == user.username)).first()
    if existing:
        raise HTTPException(409, "Username already exists")

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    """Log in and receive a JWT access token"""
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ============================================================
# MONITORING
# ============================================================

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "uptime_seconds": time.time() - start_time,
        "system": {
            "platform": platform.platform(),
            "python": platform.python_version()
        }
    }


@app.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_user)):
    """Metrics endpoint for monitoring (requires authentication)."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent
    }

# ============================================================
# CATEGORY CRUD
# ============================================================

@app.post("/categories", response_model=Category, status_code=201)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    """Create a new category"""
    existing = session.exec(select(Category).where(Category.name == category.name)).first()
    if existing:
        raise HTTPException(400, "Category already exists")

    db_category = Category(**category.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.get("/categories", response_model=List[Category])
def list_categories(session: Session = Depends(get_session)):
    """List all categories"""
    return session.exec(select(Category)).all()


# ============================================================
# PRODUCT CRUD
# ============================================================

@app.post("/products", response_model=Product, status_code=201)
def create_product(product: ProductCreate, session: Session = Depends(get_session)):
    """Create a new product"""
    if product.category_id:
        category = session.get(Category, product.category_id)
        if not category:
            raise HTTPException(404, "Category not found")

    db_product = Product(**product.dict())
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@app.get("/products", response_model=List[Product])
def list_products(
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    session: Session = Depends(get_session)
):
    """List products with filters"""
    query = select(Product)

    if category_id:
        query = query.where(Product.category_id == category_id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if in_stock is not None:
        if in_stock:
            query = query.where(Product.stock > 0)
        else:
            query = query.where(Product.stock == 0)

    return session.exec(query.offset(skip).limit(limit)).all()


@app.get("/products/search", response_model=List[Product])
def search_products(q: str, session: Session = Depends(get_session)):
    """Search products by name or description"""
    query = select(Product).where(
        (Product.name.contains(q)) | (Product.description.contains(q))
    )
    return session.exec(query).all()


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):
    """Get a specific product by ID"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product


@app.patch("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_session)
):
    """Partially update a product"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    for key, value in product_update.dict(exclude_unset=True).items():
        setattr(product, key, value)

    product.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(product)
    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, session: Session = Depends(get_session)):
    """Delete a product"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    session.delete(product)
    session.commit()
    return None