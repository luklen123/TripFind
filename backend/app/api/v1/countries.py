from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.country import CountryResponse
from app.models.country import Country
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/countries", tags=["Countries"])

@router.get("/", response_model=list[CountryResponse])
async def get_all_countries(db: AsyncSession = Depends(get_db)):
    query = select(Country).order_by(Country.name)

    result = await db.scalars(query)

    return result.all()
