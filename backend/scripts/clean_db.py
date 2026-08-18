import asyncio
from app.core.database import engine
from sqlalchemy import text

async def clean():
    async with engine.begin() as conn:
        print("Usuwanie resztek...")
        await conn.execute(text("DROP TABLE IF EXISTS airports CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS scraped_flights CASCADE;"))
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE;"))
        # Zabijamy osierocony indeks!
        await conn.execute(text("DROP INDEX IF EXISTS idx_airports_location CASCADE;"))
        print("Baza w 100% czysta!")

if __name__ == "__main__":
    asyncio.run(clean())