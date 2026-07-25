from curl_cffi import requests

def test_wizzair_api():
    # Zaktualizowana wersja API wyciągnięta z Twojego cURL
    url = "https://be.wizzair.com/29.7.1/Api/search/search"

    # Dokładne odwzorowanie Twoich nagłówków
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Sec-Fetch-Site": "same-site",
        "Accept-Language": "pl-PL,pl;q=0.9",
        "Sec-Fetch-Mode": "cors",
        "Origin": "https://www.wizzair.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5.2 Safari/605.1.15",
        "Referer": "https://www.wizzair.com/en-gb/booking/select-flight/WRO/BCN/2026-08-19/null/1/0/0/null",
        "Sec-Fetch-Dest": "empty",
        
        # Ciasteczka sesyjne i Akamai
        "Cookie": "ak_bm_vw_1.1=0RLkITbkCUOgGyxCBqOGO5BupQpnbXFjxJ3vhgA7xc308Waf9Bob86pdXFwNehI2k4mP2slieAe9FhXjhoCqO4iLdpPf0R4DyExNmzb6VdR0bnyVKy1Mx8H064NuzcHm4FcOBCzbT7NnM4vvdGJYPqvRdEcDDNBNbM5uBbbhNySe; ak_bm_vw_1.1-ssn=0RLkITbkCUOgGyxCBqOGO5BupQpnbXFjxJ3vhgA7xc308Waf9Bob86pdXFwNehI2k4mP2slieAe9FhXjhoCqO4iLdpPf0R4DyExNmzb6VdR0bnyVKy1Mx8H064NuzcHm4FcOBCzbT7NnM4vvdGJYPqvRdEcDDNBNbM5uBbbhNySe; RequestVerificationToken=0b30771130c841c6bb9a28f40d1e4163; ASP.NET_SessionId=xayzvz2phggncdbn5p3ack3s; configCatBeId=To83_qDVGNZHvZFAP8z5-",
        
        # Nagłówki weryfikacyjne Kasada (Dowód pracy przeglądarki)
        "x-kpsdk-ct": "0RLkITbkCUOgGyxCBqOGO5BupQpnbXFjxJ3vhgA7xc308Waf9Bob86pdXFwNehI2k4mP2slieAe9FhXjhoCqO4iLdpPf0R4DyExNmzb6VdR0bnyVKy1Mx8H064NuzcHm4FcOBCzbT7NnM4vvdGJYPqvRdEcDDNBNbM5uBbbhNySe",
        "x-kpsdk-cd": '{"workTime":1784836619404,"id":"94c3b37018ee12d10e5063200277ebbb","answers":[1,8],"duration":19,"d":-45,"st":1784836562109,"rst":1784836562064}',
        "x-kpsdk-h": "01LAYcQHBsrRxyq9ja+CNVxPZlQ9g=",
        "x-kpsdk-v": "j-1.2.522",
        
        # Wewnętrzny token CSRF Wizz Aira (musi pasować do tego w Cookie)
        "X-RequestVerificationToken": "0b30771130c841c6bb9a28f40d1e4163",
        "Priority": "u=3, i"
    }

    # Zwróć uwagę na format daty z dodanym T00:00:00 (tak jak w oryginalnym cURL)
    payload = {
        "isFlightChange": False,
        "flightList": [
            {
                "departureStation": "WRO",
                "arrivalStation": "BCN",
                "departureDate": "2026-08-19T00:00:00"
            }
        ],
        "adultCount": 1,
        "childCount": 0,
        "infantCount": 0,
        "wdc": True
    }

    print("Wysyłam żądanie POST do API Wizz Air (Akamai + Kasada)...")

    try:
        # Ponownie impersonujemy Safari, bo Twój User-Agent to Mac/Safari
        response = requests.post(
            url, 
            headers=headers, 
            json=payload, 
            impersonate="safari15_5"
        )

        print(f"Status HTTP: {response.status_code}")
        
        if response.status_code == 200:
            print("\n✅ SUKCES! Ominięto Akamai i Kasadę.")
            data = response.json()
            outbound_flights = data.get("outboundFlights", [])
            
            if outbound_flights:
                first_flight = outbound_flights[0]
                print(f"Lot Wizz: {first_flight.get('flightNumber')}")
                print(f"Wylot:    {first_flight.get('departureDateTime')}")
            else:
                print("Brak lotów w tym dniu.")
                
        else:
            print(f"\n⚠️ Odrzucenie zapytania. Status: {response.status_code}")
            print(response.text[:500])

    except Exception as e:
        print(f"\n🔥 Wystąpił błąd: {e}")

if __name__ == "__main__":
    test_wizzair_api()