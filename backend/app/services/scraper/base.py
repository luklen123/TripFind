from abc import ABC, abstractmethod
from datetime import date


from app.schemas.search import SimpleScrapedFlight



class BaseScraper(ABC):

    @abstractmethod
    async def fetch_flights(self, origin: str, destination: str, date_from: date, date_to: date | None) -> dict | None:
        """Fetches flights for given route and date"""

        pass


    @staticmethod
    @abstractmethod
    def parse_response(response: dict | None) -> list[SimpleScrapedFlight]:
        """Parses fetched flight response"""
        
        pass