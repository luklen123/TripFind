import asyncio
import json
from sqlalchemy import select


from app.core.database import SessionLocal
from app.models.country import Country



async def load_countries_to_db(file_path: str):
    print("Starting loading countries to db...")

    with open(file_path, "r", encoding="utf-8") as file:
        countries_data = json.load(file)

    async with SessionLocal() as db:
        result = await db.execute(select(Country.name).limit(1))
        if result.scalars().first():
            print("Found country in the database. Aborting the load")
            return 

        countries_to_insert = []

        for country in countries_data:
            if not country.get("name"):
                continue

            new_country= Country(
                name = country.get("name"),
                code = country.get("code"),
            )
            countries_to_insert.append(new_country)

        db.add_all(countries_to_insert)
        await db.commit()

        print(f"Success. Loaded {len(countries_to_insert)} countries to the database")

if __name__ == "__main__":
    asyncio.run(load_countries_to_db("data/countries.json"))