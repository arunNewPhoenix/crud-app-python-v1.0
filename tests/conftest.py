import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.cache import get_redis
from app.main import app


@pytest.fixture()
def client():
    test_engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    fake_cache = fakeredis.FakeRedis(decode_responses=True)

    def override_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = lambda: fake_cache
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
