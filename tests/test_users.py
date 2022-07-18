import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.main import app
from app import schemas
from app.config import settings
from app.database import get_db, Base


# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:fastapi:fastapi@127.0.0.1:5432/fastapi_test"
SQLALCHEMY_DATABASE_URL = f'postgresql://' \
                          f'{settings.database_username}:' \
                          f'{settings.database_password}@' \
                          f'{settings.database_hostname}:' \
                          f'{settings.database_port}/' \
                          f'{settings.database_name}_test'

# The engine is responsible for establishing a connection
engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get a session to the database to send SQL statement
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    # This logic will help in troubleshooting
    Base.metadata.drop_all(bind=engine)    # This will tell sqlalchemy to all of our tables
    # We can run our code before we run our test
    Base.metadata.create_all(bind=engine)  # This will tell sqlalchemy to create all of our tables
    yield TestClient(app)   # yield is the same as return
    # Run our code after our test finish


def test_root(client):
    res = client.get("/")
    print(res.json().get("message"))
    assert res.json().get("message") == "Welcome to my API"
    assert res.status_code == 200


def test_create_user(client):
    res = client.post("/users/", json={"email": "developer@fastapi.com", "password": "developer"})
    new_user = schemas.UserOut(**res.json())    # Unpacking the dictionary
    assert new_user.email == "developer@fastapi.com"
    assert res.status_code == 201

