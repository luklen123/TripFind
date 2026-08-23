from datetime import datetime
from zoneinfo import ZoneInfo


from app.models.flight import ScrapedFlight
from app.schemas.search import FlightSearchRequest



def prepare_flights_calendar(flights: list[ScrapedFlight]) -> dict:
    calendar = {}

    for flight in flights:
        tz_name = flight.departure_airport.timezone
        local_date = datetime.fromtimestamp(flight.dep_time_utc, tz=ZoneInfo(tz_name)).strftime('%Y-%m-%d')

        if local_date not in calendar:
            calendar[local_date] = {
                "cheapest_price": flight.price,
                "cheapest_flight": flight,
                "currency": flight.price_currency,
                "flights": []
            }

        if flight.price < calendar[local_date]["cheapest_price"]:
            calendar[local_date]["cheapest_price"] = flight.price
            calendar[local_date]["cheapest_flight"] = flight

        calendar[local_date]["flights"].append(flight)

    for day_data in calendar.values():
        day_data["flights"].sort(key=lambda x: x.dep_time_utc)

    return calendar


def prepare_flexible_durations(params: FlightSearchRequest, outbound_calendar: dict, return_calendar: dict) -> dict:
    if params.min_stay_days is None or params.max_stay_days is None:
        if params.weekend_flights:
            min_limit = 0
            max_limit = 3
        else:
            min_limit = 0
            max_limit = 10000
    else:
        min_limit = params.min_stay_days
        max_limit = params.max_stay_days
        

    flexible_durations = {}
    for out_date_str, out_details in outbound_calendar.items():
        out_price = out_details["cheapest_price"]
        out_flight = out_details["cheapest_flight"]
        currency = out_details["currency"]

        out_date = datetime.strptime(out_date_str, "%Y-%m-%d")

        for ret_date_str, ret_details in return_calendar.items():
            ret_price = ret_details["cheapest_price"]
            ret_flight = ret_details["cheapest_flight"]

            ret_date = datetime.strptime(ret_date_str, "%Y-%m-%d")

            day_diff = (ret_date.date() - out_date.date()).days

            if day_diff < min_limit or day_diff > max_limit or ret_date <= out_date:
                continue

            if day_diff not in flexible_durations:
                flexible_durations[day_diff] = {
                    "cheapest_price": out_price + ret_price,
                    "outbound_flight": out_flight,
                    "return_flight": ret_flight,
                    "currency": currency
                }
            elif out_price + ret_price < flexible_durations[day_diff]["cheapest_price"]:
                flexible_durations[day_diff]["cheapest_price"] = out_price + ret_price
                flexible_durations[day_diff]["outbound_flight"] = out_flight
                flexible_durations[day_diff]["return_flight"] = ret_flight

    return flexible_durations


def prepare_cheapest_flight(flexible_durations: dict, validated_outbound_flights: list) -> dict:
    cheapest_flight = {}

    if flexible_durations:
        for details in flexible_durations.values():
            if "cheapest_price" not in cheapest_flight or details["cheapest_price"] < cheapest_flight["cheapest_price"]:
                cheapest_flight["cheapest_price"] = details["cheapest_price"]
                cheapest_flight["currency"] = details["currency"]
                cheapest_flight["flights"] = [{
                    "outbound_flight": details["outbound_flight"],
                    "return_flight": details["return_flight"]
                }]
            elif details["cheapest_price"] == cheapest_flight["cheapest_price"]:
                cheapest_flight["flights"].append({
                    "outbound_flight": details["outbound_flight"],
                    "return_flight": details["return_flight"]                
                })
    else:
        for flight in validated_outbound_flights:
            if "cheapest_price" not in cheapest_flight or flight.price < cheapest_flight["cheapest_price"]:
                cheapest_flight["cheapest_price"] = flight.price
                cheapest_flight["currency"] = flight.price_currency
                cheapest_flight["flights"] = [{
                    "outbound_flight": flight,
                    "return_flight": None
                }]

    return cheapest_flight 