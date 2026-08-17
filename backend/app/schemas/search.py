from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from datetime import date


from app.schemas.airport import AirportResponse



class FlightSearchRequest(BaseModel):

    # departure airports selected by user (iata_code)
    dep_airports: list[str] | None = None
    # if user selected only one departure airport searching nearby airports can be applied (km)
    dep_max_distance_km: int | None = Field(default=None, ge=0, le=500, description="Maximal distance of airport from departure airport")
    # if user did not selected any dep airport we are selecting every airport in given country (iso 3166 alpha-2)
    dep_airport_country_code: str | None = None 

    # arrival airports selected by user (iata_code)
    arr_airports: list[str] | None = None
    # if user selected only one arrival airport searching nearby airports can be applied (km)
    arr_max_distance_km: int | None = Field(default=None, ge=0, le=500, description="Maximal distance of airport from arrival airport")
    # if user did not selected any arr airport we are selecting every airport in given country (iso 3166 alpha-2)
    arr_airport_country_code: str | None = None

    dep_date_start: date
    dep_date_end: date
    arr_date_start: date | None = None
    arr_date_end: date | None = None
    min_stay_days: int | None = Field(default=None, ge=0, le=30, description="Minimal number of stay days")
    max_stay_days: int | None= Field(default=None, ge=0, le=30, description="Maximal number of stay days")

    # can be only true when dep_date_start = dep_date_end and arr_date_start = arr_date_end
    weekend_flights: bool = False


    @field_validator('dep_airports', 'arr_airports')
    @classmethod
    def validate_airports_iata_codes(cls, airports_list: list[str]):
        if airports_list:
            cleaned_list = []

            for code in airports_list:
                if len(code) != 3 or not code.isalpha():
                    raise ValueError(f'Iata code {code} is not valid')
                
                cleaned_list.append(code.upper())

            return cleaned_list
        return None

    @field_validator('dep_airport_country_code', 'arr_airport_country_code')
    @classmethod
    def validate_countries_codes(cls, country_code):
        if country_code:
            if len(country_code) != 2 or not country_code.isalpha():
                raise ValueError(f"Country code {country_code} is not valid") 

            return country_code.upper()
        return None

    @model_validator(mode='after')
    def validate_dep_airport_params(self):

        has_airports = bool(self.dep_airports)
        airports_count = len(self.dep_airports) if has_airports else 0
        has_radius = self.dep_max_distance_km is not None
        has_country = self.dep_airport_country_code is not None

        if has_country and (has_radius or has_airports):
            raise ValueError('Cannot combine country search with specific airports or distance radius.')

        if has_radius and airports_count != 1:
            raise ValueError('Distance radius can only be used when exactly ONE departure airport is provided.')

        if not has_country and not has_airports:
            raise ValueError('You must provide either departure airports or a departure country code.')

        return self
     
    @model_validator(mode='after')
    def validate_arr_airport_params(self):

        has_airports = bool(self.arr_airports)
        airports_count = len(self.arr_airports) if has_airports else 0
        has_radius = self.arr_max_distance_km is not None
        has_country = self.arr_airport_country_code is not None

        if has_country and (has_radius or has_airports):
            raise ValueError('Cannot combine country search with specific airports or distance radius.')

        if has_radius and airports_count != 1:
            raise ValueError('Distance radius can only be used when exactly ONE arrival airport is provided.')

        if not has_country and not has_airports:
            raise ValueError('You must provide either arrival airports or a arrival country code.')

        return self

    @model_validator(mode="after")
    def check_dep_and_arr_separation(self):
        dep_iata_set = set(self.dep_airports)
        arr_iata_set = set(self.arr_airports)

        common_iata = dep_iata_set & arr_iata_set
        if common_iata:
            raise ValueError(f"The following airports cannot be in both departure and arrival: {common_iata}")
        
        return self
    
    @model_validator(mode='after')
    def check_dep_end_greater_than_start(self):
        if self.dep_date_end < self.dep_date_start:
            raise ValueError('End date of departure date has to be later or equal then start date of departure')
        
        return self

    @model_validator(mode='after')
    def check_arr_end_greater_than_start(self):
        count = 0

        count += 1 if self.arr_date_start else 0
        count += 1 if self.arr_date_end else 0

        if count == 1:
            raise ValueError("Both arrival start and end date should be passed")

        if count == 2:
            if self.arr_date_end < self.arr_date_start:
                raise ValueError('End date of arrival date has to be later or equal then start date of arrival')
        
        return self

    @model_validator(mode='after')
    def check_arr_dates_later_then_dep(self):
        if self.arr_date_end:
            if self.arr_date_end < self.dep_date_end:
                raise ValueError('Arrival date have to be later than departure date')
        
        return self

    @model_validator(mode='after')
    def check_max_stay_greater_than_min(self):
        count = 0

        count += 1 if self.min_stay_days is not None else 0
        count += 1 if self.max_stay_days is not None else 0

        if count == 1:
            raise ValueError("Both min and max stay days should be passed")
        
        if count == 2:
            if self.max_stay_days < self.min_stay_days:
                raise ValueError('Number of max stay days can not be smaller than min stay days')
        
        return self 

    @model_validator(mode='after')
    def check_stay_days_validity(self):
        if self.max_stay_days is not None:
            if self.arr_date_end:
                days_diff = (self.arr_date_end - self.dep_date_start).days

                if days_diff < self.max_stay_days:
                    raise ValueError("Given range for stay days is too wide")

        return self

    @model_validator(mode='after')
    def check_weekend_flights_validity(self):
        if self.weekend_flights:
            count = 0

            count += 1 if self.arr_date_start else 0
            count += 1 if self.arr_date_end else 0

            if self.min_stay_days or self.max_stay_days:
                raise ValueError("For weekend flight search mininal and maximal stay days can not be applied")

            if count != 2:
                raise ValueError("For weekend flight search arrival dates range has to be selected")

            if self.dep_date_start != self.dep_date_end or self.arr_date_start != self.arr_date_end:
                raise ValueError("For weekend flight search departure and arrival start and end has to be the same")

            if (self.arr_date_end - self.dep_date_end).days < 7:
                raise ValueError("For weekend search at least 7 days period has to be selected")
            
        return self



class ScrapedFlight(BaseModel):
    id: int

    airline_name: str
    flight_number: str

    dep_iata: str
    departure_airport: AirportResponse

    arr_iata: str
    arrival_airport: AirportResponse

    dep_time_utc: int
    arr_time_utc: int
    flight_time_mins: int
    scraped_at_utc: int

    seats_left: int
    price: float
    price_currency: str
    price_in_euro: float

    @field_validator('dep_iata', 'arr_iata')
    @classmethod
    def validate_airport(cls, airport_iata: str) -> str:
        if len(airport_iata) != 3 or not airport_iata.isalpha():
            raise ValueError(f'Code {airport_iata} is not valid')

        return airport_iata.upper()

    model_config = ConfigDict(from_attributes=True)



class SimpleScrapedFlight(BaseModel):

    airline_name: str
    flight_number: str

    dep_iata: str
    arr_iata: str

    dep_time_utc: int
    arr_time_utc: int
    flight_time_mins: int
    scraped_at_utc: int

    seats_left: int
    price: float
    price_currency: str

    @field_validator('dep_iata', 'arr_iata')
    @classmethod
    def validate_airport(cls, airport_iata: str) -> str:
        if len(airport_iata) != 3 or not airport_iata.isalpha():
            raise ValueError(f'Code {airport_iata} is not valid')

        return airport_iata.upper()

    model_config = ConfigDict(from_attributes=True)