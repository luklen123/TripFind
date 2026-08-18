from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.schemas.search import FlightSearchRequest, ScrapedFlight
from app.core.database import get_db
from app.services.scraper.runner import perform_scrape



router = APIRouter(prefix="/api/v1/search", tags=["Search"])

@router.post("/")
async def perform_search(request: FlightSearchRequest, db: AsyncSession = Depends(get_db)):
    results = await perform_scrape(db, request)

    return results