from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.models.airport import Airport
from app.schemas.airport import AirportResponse
from app.core.database import get_db



router = APIRouter(prefix="/api/v1/airports", tags=["Airports"])

@router.get("/", response_model=list[AirportResponse])
async def get_all_airports(db: AsyncSession = Depends(get_db)):
    query = select(Airport).order_by(Airport.city)

    result = await db.scalars(query)
    return result.all()