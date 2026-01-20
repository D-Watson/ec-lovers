from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# 替换为你的数据库 URL
DATABASE_URL = "postgresql://postgres:000708@localhost/emotional_company"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

