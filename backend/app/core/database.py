from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import settings

engine = create_async_engine(settings.DATABASE_URL)

SessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False, 
    expire_on_commit=False
)

class Base(DeclarativeBase): 
    pass 

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    