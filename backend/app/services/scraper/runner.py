from sqlalchemy.ext.asyncio import AsyncSession
from itertools import product
from datetime import date
import asyncio
import logging


from app.schemas.search import SimpleScrapedFlight, ScrapedFlight, FlightSearchRequest
from app.services.flight_processor import prepare_cheapest_flight, prepare_flexible_durations, prepare_flights_calendar
from app.services.flight_repository import save_scraped_flights
from app.utils.date_helpers import compute_date_chunks, compute_weekend_dates
from app.services.geo import check_airports_reality, check_country_reality, compute_country_airports, compute_nearby_airports
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


async def execute_scraping_batch(search_params: list[tuple]) -> list[SimpleScrapedFlight]:
    max_concurrent_requests = 5
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    ryanair_scraper = RyanairScraper()

    tasks = [fetch_with_semaphore(ryanair_scraper, semaphore, param) for param in search_params]

    results = await asyncio.gather(*tasks)
    flat_results = [flight for batch in results for flight in batch]

    return flat_results


async def perform_scrape(db: AsyncSession, params: FlightSearchRequest) -> dict:
    search_params, airports_iata= await compute_search_params(db, params)

    scraped_flights = await execute_scraping_batch(search_params)
    saved_flights = await save_scraped_flights(db, scraped_flights)
    outgoing_flights, retrun_flights = separate_flights(airports_iata, saved_flights)

    results = compute_best_routes(params, outgoing_flights, retrun_flights)

    return results


async def compute_search_params(db: AsyncSession, params: FlightSearchRequest) -> tuple[list[tuple[tuple[str, str], tuple[date, date | None]]], tuple[list[str], list[str]]]:
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

    return (search_params, (dep_airports_to_search, arr_airports_to_search))


async def validate_params(db: AsyncSession, params: FlightSearchRequest) -> None:

    if params.dep_airports:
        await check_airports_reality(db, params.dep_airports)

    if params.arr_airports and params.arr_airports[0] != "ANY":
        await check_airports_reality(db, params.arr_airports)

    if params.dep_airport_country_code:
        await check_country_reality(db, params.dep_airport_country_code)

    if params.arr_airport_country_code:
        await check_country_reality(db, params.arr_airport_country_code)


def separate_flights(airports_iata: tuple[list[str], list[str]], flights: list[ScrapedFlight]) -> tuple[list[ScrapedFlight], list[ScrapedFlight]]:
    origin_iata, destination_iata = airports_iata

    outgoing_flights = []
    return_flights = []

    for flight in flights:
        if flight.dep_iata in origin_iata:
            outgoing_flights.append(flight)
        else:
            return_flights.append(flight)

    return (outgoing_flights, return_flights)

def compute_best_routes(params: FlightSearchRequest, outbound_flights: list[ScrapedFlight], return_flights: list[ScrapedFlight]) -> dict:
    outbound_calendar = prepare_flights_calendar(outbound_flights)
    return_calendar = prepare_flights_calendar(return_flights)

    flexible_durations = prepare_flexible_durations(params, outbound_calendar, return_calendar)
    cheapest_flight = prepare_cheapest_flight(flexible_durations)

    return {
        "best_overall": cheapest_flight,
        "calendar_view": {
            "outbound": outbound_calendar,
            "return": return_calendar
        },
        "flexible_durations": flexible_durations
    }


