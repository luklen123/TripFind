from abc import ABC, abstractmethod
from datetime import date


from app.schemas.search import SimpleScrapedFlight



class BaseScraper(ABC):

    @abstractmethod
    async def fetch_flights(self, origin: str, destination: str, date_from: date, date_to: date) -> dict:
        """Fetches flights for given route and date"""

        pass


    @abstractmethod
    def parse_response(response: dict) -> list[SimpleScrapedFlight]:
        """Parses fetched flight response"""
        
        pass