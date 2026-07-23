from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from config import settings

load_dotenv()

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()