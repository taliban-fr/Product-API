import logging
import os
import platform
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from fastapi.responses import HTMLResponse
import psutil
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from auth import create_access_token, get_current_user, hash_password, verify_password
from database.session import create_db_and_tables, get_session
from models.product import (
    Category,
    CategoryCreate,
    Product,
    ProductCreate,
    ProductUpdate,
)
from models.user import User, UserCreate, UserRead

LOG_FILE = os.getenv("LOG_FILE", "app.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Catalog API", version="1.0.0")

@app.get("/", response_class=HTMLResponse)
async def portfolio():
    html_content = """
    <html>
    <head>
        <title>Student Portfolio - Backend Assignments</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            .student-info { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0; }
            .student-info strong { color: #2c3e50; }
            .admission { font-size: 1.2em; color: #2980b9; font-weight: bold; }
            .assignment { margin: 12px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #3498db; transition: all 0.3s ease; }
            .assignment:hover { background: #e8f4fd; transform: translateX(5px); }
            .assignment a { color: #0366d6; text-decoration: none; font-weight: 500; display: flex; align-items: center; }
            .assignment a:hover { text-decoration: underline; }
            .badge { display: inline-block; background: #3498db; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em; margin-right: 10px; }
            .lesson-topic { color: #7f8c8d; font-size: 0.9em; margin-left: 10px; }
            .footer { margin-top: 30px; text-align: center; color: #95a5a6; font-size: 0.9em; border-top: 1px solid #ecf0f1; padding-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Backend Development Portfolio</h1>

            <div class="student-info">
                <p><strong>Student Name:</strong> Mike Kioko</p>
                <p><strong>Admission Number:</strong> <span class="admission">C027-01-1023/2022</span></p>
                <p><strong>Email:</strong> kyalo.kioko22@students.dkut.ac.ke</p>
            </div>

            <h2>Backend Assignments</h2>
            <p style="color: #7f8c8d; margin-bottom: 20px;">Click on any assignment to view the complete code on GitHub</p>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/gighub-api/tree/main" target="_blank">
                    <span class="badge">Lesson 1</span>
                    <span>HTTP & Your First API</span>
                    <span class="lesson-topic">— FastAPI + Uvicorn, HTTP Methods, Status Codes</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/gighub-api/tree/main" target="_blank">
                    <span class="badge">Lesson 2</span>
                    <span>Docker - Packaging Your API</span>
                    <span class="lesson-topic">— Containers, Dockerfiles, Docker Compose</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/gighub-api/tree/main" target="_blank">
                    <span class="badge">Lesson 3</span>
                    <span>Routing, Parameters & Request Bodies</span>
                    <span class="lesson-topic">— Path Parameters, Query Parameters, Pydantic Validation</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/Library-API/tree/main" target="_blank">
                    <span class="badge">Lesson 4</span>
                    <span>PostgreSQL & SQLModel – Your First Database</span>
                    <span class="lesson-topic">— ORM, Database Migrations, SQLModel</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/Bookstore-API/blob/main/submission.md" target="_blank">
                    <span class="badge">Lesson 5</span>
                    <span>CRUD Operations</span>
                    <span class="lesson-topic">— Create, Read, Update, Delete with Error Handling</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/TechVault-API/tree/main" target="_blank">
                    <span class="badge">Lesson 6</span>
                    <span>Error Handling & Validation</span>
                    <span class="lesson-topic">— HTTPException, Custom Validators, Global Handlers</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/HEALTHTRACK-API/tree/main" target="_blank">
                    <span class="badge">Lesson 7</span>
                    <span>User Authentication – JWT & Password Hashing</span>
                    <span class="lesson-topic">— JWT Tokens, bcrypt, Login/Register Endpoints</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/ClinicGuard-Patient-Management-API/tree/main" target="_blank">
                    <span class="badge">Lesson 8</span>
                    <span>Authorization & Rate Limiting</span>
                    <span class="lesson-topic">— RBAC, Dependency Injection, Rate Limiting</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/Sendit-Document-Management-API/tree/main" target="_blank">
                    <span class="badge">Lesson 9</span>
                    <span>File Uploads & External APIs</span>
                    <span class="lesson-topic">— File Validation, httpx, Environment Variables</span>
                </a>
            </div>

            <div class="assignment">
                <a href="https://github.com/taliban-fr/Product-API/tree/main" target="_blank">
                    <span class="badge">Lesson 10</span>
                    <span>Testing & Deployment (Cloud)</span>
                    <span class="lesson-topic">— Pytest, CI/CD, Render Deployment</span>
                </a>
            </div>

            <div class="footer">
                <p>Deployed on Render | Last Updated: August 2026</p>
                <p style="font-size: 0.8em;">Click on any assignment link to view the complete source code on GitHub</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

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
            "python": platform.python_version(),
        },
    }


@app.get("/metrics")
def get_metrics(current_user: User = Depends(get_current_user)):
    """Metrics endpoint for monitoring (requires authentication)."""
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
    }


# ============================================================
# CATEGORY CRUD
# ============================================================


@app.post("/categories", response_model=Category, status_code=201)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    """Create a new category"""
    existing = session.exec(
        select(Category).where(Category.name == category.name)
    ).first()
    if existing:
        raise HTTPException(400, "Category already exists")

    db_category = Category(**category.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.get("/categories", response_model=list[Category])
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


@app.get("/products", response_model=list[Product])
def list_products(
    skip: int = 0,
    limit: int = 10,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    session: Session = Depends(get_session),
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


@app.get("/products/search", response_model=list[Product])
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
    session: Session = Depends(get_session),
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
