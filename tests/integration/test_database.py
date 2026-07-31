from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

test_engine = create_engine(TEST_DATABASE_URL)

TestSessionLocal = sessionmaker(bind=test_engine)

def override_get_db():

    db = TestSessionLocal()

    try:
        yield db

    finally:
        db.close()
 