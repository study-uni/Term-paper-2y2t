import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.dal.database import Base
from app.dal.uow.sqlalchemy_uow import SQLAlchemyUnitOfWork
from app.main import app
from app.pl.dependencies import get_uow
from app.seed import seed_db

TEST_DATABASE_URL = "sqlite:///./test_api.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_api.db"):
        try:
            os.remove("./test_api.db")
        except OSError:
            pass


@pytest.fixture(autouse=True)
def override_uow():
    def get_test_uow():
        return SQLAlchemyUnitOfWork(TestingSessionLocal)

    app.dependency_overrides[get_uow] = get_test_uow
    yield
    app.dependency_overrides.clear()
