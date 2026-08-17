from pydantic import BaseModel, ConfigDict


class AirportResponse(BaseModel):
    iata_code: str
    name: str
    city: str
    country_code: str
    timezone: str

    model_config = ConfigDict(from_attributes=True)
