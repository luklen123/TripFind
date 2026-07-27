from sqlalchemy.ext.asyncio import AsyncSession
from itertools import product
from datetime import date
import asyncio
import logging


from app.schemas.search import ScrapedFlight, FlightSearchRequest
from app.services.tools import check_airports_reality, check_country_reality, compute_nearby_airports, compute_country_airports, compute_weekend_dates, compute_date_chunks
from app.services.scraper.ryanair import RyanairScraper, BaseScraper



async def fetch_with_semaphore(scraper: BaseScraper, semaphore: asyncio.Semaphore, param: tuple) -> list:
    airports, dates = param
    dep_iata, arr_iata = airports
    dep_date, arr_date = dates

    async with semaphore:
        try:
            result = await scraper.fetch_flights(dep_iata, arr_iata, dep_date, arr_date)

            return scraper.parse_response(result)
        except Exception as e:
            logging.error(f"Scraper failed for {dep_iata}->{arr_iata} on {dep_date}: {e}")
            return []


async def execute_scraping_batch(search_params: list[tuple]) -> list[ScrapedFlight]:
    max_concurrent_requests = 5
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    ryanair_scraper = RyanairScraper()

    tasks = [fetch_with_semaphore(ryanair_scraper, semaphore, param) for param in search_params]

    results = await asyncio.gather(*tasks)
    flat_results = [flight for batch in results for flight in batch]

    return flat_results


async def perform_scrape(db: AsyncSession, params: FlightSearchRequest):
    search_params = await compute_search_params(db, params)

    return await execute_scraping_batch(search_params)


async def compute_search_params(db: AsyncSession, params: FlightSearchRequest) -> list[tuple[tuple[str, str], tuple[date, date | None]]]:
    await validate_params(db, params)

    # AIRPORTS
    dep_airports_to_search = set()

    if params.dep_airports and not params.dep_max_distance_km:
        dep_airports_to_search.update(params.dep_airports)

    dep_airports_to_search.update(await compute_nearby_airports(db, params.dep_airports, params.dep_max_distance_km))
    dep_airports_to_search.update(await compute_country_airports(db, params.dep_airport_country_code))

    arr_airports_to_search = set()

    if params.arr_airports and not params.arr_max_distance_km:
        arr_airports_to_search.update(params.arr_airports)

    arr_airports_to_search.update(await compute_nearby_airports(db, params.arr_airports, params.arr_max_distance_km))
    arr_airports_to_search.update(await compute_country_airports(db, params.arr_airport_country_code))

    airports_to_search = [
        (dep, arr)
        for dep, arr in product(dep_airports_to_search, arr_airports_to_search)
        if dep != arr
    ]


    # DATES
    date_ranges = []

    if params.weekend_flights:
        date_ranges += compute_weekend_dates(params.dep_date_start, params.arr_date_end)
    else:
        date_ranges += compute_date_chunks(params.dep_date_start, params.dep_date_end, params.arr_date_start, params.arr_date_end)


    search_params = list(product(airports_to_search, date_ranges))

    return search_params


async def validate_params(db: AsyncSession, params: FlightSearchRequest) -> None:

    if params.dep_airports:
        await check_airports_reality(db, params.dep_airports)

    if params.arr_airports and params.arr_airports[0] != "ANY":
        await check_airports_reality(db, params.arr_airports)

    if params.dep_airport_country_code:
        await check_country_reality(db, params.dep_airport_country_code)

    if params.arr_airport_country_code:
        await check_country_reality(db, params.arr_airport_country_code)