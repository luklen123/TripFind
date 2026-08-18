from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from geoalchemy2.functions import ST_DWithin


from app.models.airport import Airport
from app.services.exceptions import AirportNotFoundError


async def check_airports_reality(db: AsyncSession, iata_codes: list[str]) -> None:

    iata_codes = set(iata_codes)
    query = select(Airport.iata_code).where(Airport.iata_code.in_(iata_codes))

    result = await db.execute(query)
    found_codes = result.scalars().all()

    missing_codes = set(iata_codes) - set(found_codes)
    if missing_codes:
        raise AirportNotFoundError(missing_codes)


async def get_nearby_airports(db: AsyncSession, origin_iata: str, radious_km: int) -> list[str]:
    """Finds airports in provided radious"""

    query_origin = select(Airport).where(Airport.iata_code == origin_iata)   
    origin_airport = await db.scalar(query_origin)

    if not origin_airport:
        return []
    
    radious_meters = radious_km * 1000
    query_nearby = (
        select(Airport.iata_code)
        .where(
            ST_DWithin(Airport.location, origin_airport.location, radious_meters)
        )
    )
    nearby_airports = await db.scalars(query_nearby)

    return list(nearby_airports.all())


async def compute_nearby_airports(db: AsyncSession, airports_iata: list[str], max_radius: int) -> list[str]:
    if airports_iata is None or len(airports_iata) != 1 or max_radius is None:
        return []

    return await get_nearby_airports(db, airports_iata[0], max_radius)


async def check_country_reality(db: AsyncSession, country_code: str) -> None:

    query = select(Airport).where(Airport.country_code == country_code).limit(1)
    result = await db.execute(query)
    found_airports = result.scalars().first()

    if not found_airports:
        raise ValueError("Provided country code does not exist or has no airports")


async def compute_country_airports(db: AsyncSession, country_code: str) -> list[str]:
    if country_code is None:
        return []

    query = select(Airport.iata_code).where(Airport.country_code == country_code)
    result = await db.execute(query)
    found_airports = result.scalars().all()

    return found_airports