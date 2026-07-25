from curl_cffi import requests
from pprint import pprint
from datetime import datetime


def parse_response(response: dict) -> list[dict]:
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
                    "airline_name": flight['operatedBy'],
                    "flight_number": flight['flightNumber'],
                    "dep_iata": dep_iata,
                    "arr_iata": arr_iata,
                    "dep_time_utc": int(datetime.fromisoformat(flight['timeUTC'][0].replace('Z', '+00:00')).timestamp()),
                    "arr_time_utc": int(datetime.fromisoformat(flight['timeUTC'][1].replace('Z', '+00:00')).timestamp()),
                    "flight_time_mins": 0,
                    "scraped_at_utc": scraped_at_utc,
                    "seats_left": flight['faresLeft'],
                    "price": flight['regularFare']['fares'][0]['amount'],
                    "price_currency": currency
                }
                fetched_results.append(mapped_data)

    return fetched_results

# URL wyciągnięty z Twojego cURLa (Zwróć uwagę na dodatkowe parametry)
url = "https://www.ryanair.com/api/booking/v4/pl-pl/availability?ADT=5&TEEN=0&CHD=0&INF=0&Origin=WRO&Destination=ATH&promoCode=&IncludeConnectingFlights=false&DateOut=2026-08-24&DateIn=2026-09-30&FlexDaysBeforeOut=0&FlexDaysOut=6&FlexDaysBeforeIn=0&FlexDaysIn=6&RoundTrip=true&IncludePrimeFares=false&ToUs=AGREED"

# Słownik z nagłówkami
headers = {
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "same-origin",
    "Accept-Language": "pl-PL,pl;q=0.9",
    "Sec-Fetch-Mode": "cors",
    
    # UWAGA DOTYCZĄCA USER-AGENT:
    # Twój cURL pochodzi z przeglądarki Safari na Macu. 
    # Zostawiamy go, ale musimy dostosować parametr 'impersonate' (wyjaśnienie niżej).
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5.2 Safari/605.1.15",
    
    "Referer": "https://www.ryanair.com/pl/pl/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut=2026-08-24&dateIn=&isConnectedFlight=false&discount=0&promoCode=&isReturn=false&originIata=WRO&destinationIata=BLQ&tpAdults=1&tpTeens=0&tpChildren=0&tpInfants=0&tpStartDate=2026-08-24&tpEndDate=&tpDiscount=0&tpPromoCode=&tpOriginIata=WRO&tpDestinationIata=BLQ",
    "Sec-Fetch-Dest": "empty",
    
    # To jest kluczowy element, który naprawi błąd 409:
    "Cookie": "mkt=/pl/pl/; rid.sig=jyna6R42wntYgoTpqvxHMK7H+KyM6xLed+9I3KsvYZaVt7P36AL6zp9dGFPu5uVxaIiFpNXrszr+LfNCdY3IT9XJkXVopZUx32eDaalfBO8J28s1crcX3gj26LKIPP4af6yZM5cZg4ZwSYUAuc4+HRxoduLmTpPkLXG7BJfvjKH8RpjSAIjmDhIFO2cbDxdN7DrFinuIad7qFrfCK1/9AYSuo1cNe2c59Qsp6iklyJHxlQdmiqClvJu5dfWMZVNdmRsv9gyD1KDXG+Ya5J7kafbClQkaA5Suq4HgZ/7AHqs+cO1ILWdMAuRZmK3vpmcFh/LzTitNGjpLHNtZ702v1yPZPLvC47iGcqHczdX/Pf3NtFk5+6iU1XLmMMllp+rcrN070sD6BF27Ht9NNazQ1wDBbEb4uZE6SxGKgUbZcVRIjGalLbEXiXl9Cj+wwDmJEQrV4jmJ2zMEeZ3Um2o8mRkoRQypmJJHRB//JOtlqpud7gb4iJLaGByrXQFxifxQiLAwJIBabSKAolEE8379gKoIOoXBbFJwhVqN29lkpP4O0G+YOVhGjedcAr0SmMSMSHuaUnwqnai6vKl+Jp52MtAeh48Mv/MNEn1cCu07jc6kWK8HGNmj3CZBnU1acFSA6eAi5H++0XBdfkFajzUJ/T8U+c9V+0wQ5CTLRw91RAb6k9AGzJH4effJ6+OtzKxEWbJ26Z7LvWtNVrUCbMFu2ShFP5rdn+nYtp3DfX21SMiL+Akj6w81no2C1ylW1Rr2VNLFMq8wdvvGbqWX+V0sIFHdjqRh5AnYIiCSv8jkCRkeRXt1g9UQuf2a0Lp/RT4z87OFpcA9YdWPq0AZYKRdM3ePuV7CJw/UBrDTPik+BFSFyKPatQP8+8bSkxlumNXaHrH1CGp8XiEc68riYEQC90NtU6XnfNcYin+f3iTCrU1B+25KIeVd0WiduSmucNYiP73wOdMYmopv9gXBXGtAYyz02EyGr1ufXmwStty0rKxdUXM8ulohjRfMR86V3gaw2g28vhcYMkhr4EM7WRVzse61yXqZNpOYCOo7h5VML55mvEsybkPMrlFU3uQSbkBv1MJz/zb/s9yJRRno584tXhxqgyiTNyvUqusV2nW2zxE=; rid=7ab71e97-711f-410e-b5f7-3ba9325de094; xid=4ab58cef-d6c9-4f32-8702-a00f0a27a114; fr-correlation-id=5398a90b-8995-4cff-bfaf-013f2e89026d; ry-welcome-to-portal-seen=true; RY_COOKIE_CONSENT=true; STORAGE_PREFERENCES={\"STRICTLY_NECESSARY\":true,\"PERFORMANCE\":false,\"FUNCTIONAL\":false,\"TARGETING\":false,\"SOCIAL_MEDIA\":false,\"PIXEL\":false,\"__VERSION\":5}",
    
    "Priority": "u=3, i",
    "client-version": "3.209.0", # Wymagany nagłówek wewnętrzny Ryanaira
    "client": "desktop"          # Wymagany nagłówek wewnętrzny Ryanaira
}

# Usunięto z Twojego cURL nagłówek: 'Accept-Encoding: gzip, deflate, br, zstd'
# Dlaczego? Biblioteka curl_cffi sama ustawia odpowiednie dekodowanie (np. brotli).
# Ręczne wymuszanie 'zstd' w Pythonie często kończy się błędem dekodowania znaków.

try:
    # UWAGA: Skoro Twój User-Agent to Safari, musimy udawać Safari, a nie Chrome!
    response = requests.get(url, headers=headers, impersonate="safari15_5")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Działa! Pobrano JSON:")
        pprint(parse_response(response.json())) # Odkomentuj, żeby zobaczyć całe dane
    else:
        print(response.text)

except Exception as e:
    print(f"Błąd: {e}")