from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    name: str
    code: str

    model_config = ConfigDict(from_attributes=True)