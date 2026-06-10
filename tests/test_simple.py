import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.api.v1.api import api_router
from app.core.config import settings

from sqlalchemy.pool import StaticPool
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create fresh app
app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
app.dependency_overrides[get_db] = override_get_db

# Import models to register tables
from app.models import user, dataset, notebook, competition, course, job, community  # noqa: F401
Base.metadata.create_all(bind=engine)

# Verify tables exist
inspector = inspect(engine)
print(f"Tables in test engine: {inspector.get_table_names()}")

client = TestClient(app)


def test_register():
    print(f"Registered tables: {list(Base.metadata.tables.keys())}")
    response = client.post("/api/v1/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    print(f"Response: {response.status_code}")
    print(f"Data: {response.json()}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_login():
    response = client.post("/api/v1/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
