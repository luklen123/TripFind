from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.airport import Airport
from app.models.flight import ScrapedFlight as DbScrapedFlight
from app.schemas.search import SimpleScrapedFlight, ScrapedFlight as SchemaScrapedFlight



async def save_scraped_flights(db: AsyncSession, scraped_flights: list[SimpleScrapedFlight]) -> list[SchemaScrapedFlight]:
    if scraped_flights is None or len(scraped_flights) == 0:
        return []

    try:
        origin_iata = scraped_flights[0].dep_iata
        destination_iata = scraped_flights[0].arr_iata

        airports_query = select(Airport).where(Airport.iata_code.in_([origin_iata, destination_iata]))
        airport_results = await db.execute(airports_query)
        airports = airport_results.scalars().all()

        airport_map = {airport.iata_code: airport for airport in airports}
        missing_airports = [iata for iata in (origin_iata, destination_iata) if iata not in airport_map]

        if missing_airports:
            raise ValueError(f"MISSING_AIRPORT_IN_DB: Scraper found airports which are not present in database ({missing_airports})")

        flights_to_db = []
        for flight in scraped_flights:
            new_flight = DbScrapedFlight(
                airline_name=flight.airline_name,
                flight_number=flight.flight_number,
                dep_iata=flight.dep_iata,
                departure_airport=airport_map[flight.dep_iata],
                arr_iata=flight.arr_iata,
                arrival_airport=airport_map[flight.arr_iata],
                dep_time_utc=flight.dep_time_utc,
                arr_time_utc=flight.arr_time_utc,
                flight_time_mins=flight.flight_time_mins,
                scraped_at_utc=flight.scraped_at_utc,
                seats_left=flight.seats_left,
                price=flight.price,
                price_currency=flight.price_currency,
                price_in_euro=0.0 # for future improvement add exchange feature
            )
            flights_to_db.append(new_flight)

        db.add_all(flights_to_db)
        await db.flush()

        saved_flights = []
        for db_flight in flights_to_db:
            new_flight = SchemaScrapedFlight(
                id=db_flight.id, 
                airline_name=db_flight.airline_name,
                flight_number=db_flight.flight_number,
                dep_iata=db_flight.dep_iata,
                departure_airport=db_flight.departure_airport,
                arr_iata=db_flight.arr_iata,
                arrival_airport=db_flight.arrival_airport,
                price_in_euro=db_flight.price_in_euro,
                dep_time_utc=db_flight.dep_time_utc,
                arr_time_utc=db_flight.arr_time_utc,
                flight_time_mins=db_flight.flight_time_mins,
                scraped_at_utc=db_flight.scraped_at_utc,
                seats_left=db_flight.seats_left,
                price=db_flight.price,
                price_currency=db_flight.price_currency
            )
            saved_flights.append(new_flight)

        await db.commit()

        return saved_flights

    except Exception as e:
        await db.rollback()
        print(f"Write error: {e}")

        return []