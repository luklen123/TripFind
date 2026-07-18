from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from datetime import date


from airport import AirportResponse

class FlightSearchRequest(BaseModel):
    dep_airports: list[str]
    dep_max_distance_km: int | None = Field(default=None, ge=0, description="Maximal distance of airport from departure airport")
    dep_airport_country: str | None = None

    arr_airports: list[str]
    arr_max_distance_km: int | None = Field(defalut=None, ge=0, description="Maximal distance of airport from arrival airport")
    arr_airport_country: str | None = None
    arr_airport_all: bool

    dep_date_start: date
    dep_date_end: date
    arr_date_start: date
    arr_date_end: date
    min_stay_days: int | None = Field(default=None, ge=0, description="Minimal number of stay days")
    max_stay_days: int | None= Field(default=None, ge=0, description="Maximal number of stay days")

    weekend_flights: bool
    ext_weekend_flights: bool 


    @model_validator(mode='after')
    def check_max_stay_greater_than_min(self):
        if self.max_stay_days is not None and self.min_stay_days is not None:
            if self.max_stay_days < self.min_stay_days:
                raise ValueError('Number of max stay days can not be smaller than min stay days')
        
        return self
    
    @model_validator(mode='after')
    def check_dep_end_greater_than_start(self):
        if self.dep_date_end < self.dep_date_start:
            raise ValueError('End date of departure date has to be later or equal then start date of departure')
        
        return self
        
    @model_validator(mode='after')
    def check_arr_end_greater_than_start(self):
        if self.arr_date_end < self.arr_date_start:
            raise ValueError('End date of arr date has to be later or equal then start date of departure')
        
        return self
        
    @model_validator(mode='after')
    def check_arr_dates_later_then_dep(self):
        if self.arr_date_end < self.dep_date_end:
            raise ValueError('Arrival date have to be later than departure date')
        
        return self
        
    @field_validator('dep_airports', 'arr_airports')
    @classmethod
    def validate_airports_lists(cls, airports_list: list[str]):
        cleaned_list = []

        for code in airports_list:
            if len(code) != 3 or not code.isalpha():
                raise ValueError(f'Code {code} is not valid')
            
            cleaned_list.append(code.upper())

        return cleaned_list