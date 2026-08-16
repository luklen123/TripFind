import asyncio
from datetime import date, datetime
from playwright.async_api import async_playwright
from pprint import pprint

from app.services.scraper.base import BaseScraper
from app.schemas.search import SimpleScrapedFlight
from app.services.tools import convert_to_mins



class RyanairScraper(BaseScraper):

    async def fetch_flights(self, origin: str, destination: str, date_from: date, date_to: date) -> dict | None:
        print(f"Fetching flights: {origin} -> {destination} (from {date_from} to {date_to}) ...")
        
        date_from_str = date_from.strftime("%Y-%m-%d")
        if date_to is None:
            date_to_str = ""
            is_return = "false"
        else:
            date_to_str = date_to.strftime("%Y-%m-%d")
            is_return = "true"

        frontend_url = (
            f"https://www.ryanair.com/pl/pl/trip/flights/select?"
            f"adults=1&teens=0&children=0&infants=0&"
            f"dateOut={date_from_str}&dateIn={date_to_str}&isConnectedFlight=false&"
            f"discount=0&promoCode=&isReturn={is_return}&"
            f"originIata={origin}&destinationIata={destination}"
        )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                captured_data = None
                route_declined = False

                async def handle_response(response):
                    nonlocal captured_data, route_declined

                    if "booking/v4" in response.url and "availability" in response.url and response.request.method == "GET":

                        if response.status == 409:
                            route_declined = True
                            return 
                        
                        try:
                            json_data = await response.json()
                            if "trips" in json_data:
                                captured_data = json_data
                        except Exception:
                            pass

                page.on("response", handle_response)
                
                print(f"Starting browser and visiting: {frontend_url}")
                await page.goto(frontend_url)
                
                for _ in range(15):
                    if captured_data:
                        break
                    if route_declined:
                        break

                    await asyncio.sleep(1)

                await browser.close()

                if route_declined:
                    print("Route does not exists!")
                    return None
                
                if not captured_data:
                    print("Scrape failed. WAITING TIMEOUT")
                    return None

                return captured_data
            
        except Exception as e:
            print(f"Occurred Exception in Playwright: {e}")
            return None


    @staticmethod
    def parse_response(response: dict | None) -> list[SimpleScrapedFlight]:
        if not response:
            return []
        
        fetched_results = []
        scraped_at_utc = int(datetime.fromisoformat(response['serverTimeUTC'].replace('Z', '+00:00')).timestamp())
        currency = response['currency']

        for trip in response['trips']:
            dep_iata = trip['origin']
            arr_iata = trip['destination']

            for flight_day in trip['dates']:
                for flight in flight_day['flights']:
                    if 'regularFare' not in flight or not flight['regularFare']['fares']:
                        continue

                    mapped_data = {
                        "airline_name": flight['operatedBy'] if flight['operatedBy'] != "" else "RyanAir",
                        "flight_number": flight['flightNumber'],
                        "dep_iata": dep_iata,
                        "arr_iata": arr_iata,
                        "dep_time_utc": int(datetime.fromisoformat(flight['timeUTC'][0].replace('Z', '+00:00')).timestamp()),
                        "arr_time_utc": int(datetime.fromisoformat(flight['timeUTC'][1].replace('Z', '+00:00')).timestamp()),
                        "flight_time_mins": convert_to_mins(flight['duration']),
                        "scraped_at_utc": scraped_at_utc,
                        "seats_left": flight['faresLeft'], # in RyanAir API if 9+ seats left -1 is returned
                        "price": flight['regularFare']['fares'][0]['amount'],
                        "price_currency": currency
                    }
                    fetched_results.append(SimpleScrapedFlight(**mapped_data))

        return fetched_results