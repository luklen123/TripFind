from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
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
    async with SessionLocal() as session:
            yield session
    