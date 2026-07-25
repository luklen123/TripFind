from sqlalchemy import select
from sqlalchemy.orm import AsyncSession 
from geoalchemy2.functions import ST_DWithin


from app.models.airport import Airport



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