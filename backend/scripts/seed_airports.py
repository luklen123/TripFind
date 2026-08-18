import asyncio
import json
from sqlalchemy import select


from app.core.database import SessionLocal
from app.models.airport import Airport



async def load_airports_to_db(file_path: str):
    print("Starting loading airports to db...")

    with open(file_path, "r", encoding="utf-8") as file:
        airports_data = json.load(file)

    async with SessionLocal() as db:
        result = await db.execute(select(Airport.iata_code).limit(1))
        if result.scalars().first():
            print("Found airports in the database. Aborting the load")
            return 

        airports_to_insert = []

        for airport in airports_data:
            if not airport.get("iata"):
                continue

            lon = airport["longitude"]
            lat = airport["latitude"]
            location = f"SRID=4326;POINT({lon} {lat})"

            new_airport = Airport(
                iata_code = airport.get("iata"),
                name = airport.get("name"),
                city = airport.get("city"),
                country_code = airport.get("country"),
                timezone = airport.get("timezone"),
                location = location
            )
            airports_to_insert.append(new_airport)

        db.add_all(airports_to_insert)
        await db.commit()

        print(f"Success. Loaded {len(airports_to_insert)} airports to the database")

if __name__ == "__main__":
    asyncio.run(load_airports_to_db("airports.json"))