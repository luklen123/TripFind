from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.airport import Airport

class ScrapedFlight(Base):
    __tablename__ = "scraped_flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    airline_name: Mapped[str] = mapped_column(String)
    flight_number: Mapped[str] = mapped_column(String)

    dep_iata: Mapped[str] = mapped_column(String(3), ForeignKey("airports.iata_code"))
    departure_airport: Mapped["Airport"] = relationship(
        "Airport", 
        foreign_keys=[dep_iata]
    )

    arr_iata: Mapped[str] = mapped_column(String(3), ForeignKey("airports.iata_code"))
    arrival_airport: Mapped["Airport"] = relationship(
        "Airport", 
        foreign_keys=[arr_iata]
    )

    dep_time_utc: Mapped[int] = mapped_column(Integer)
    arr_time_utc: Mapped[int] = mapped_column(Integer)
    flight_time_mins: Mapped[int] = mapped_column(Integer)
    scraped_at_utc: Mapped[int] = mapped_column(Integer)

    seats_left: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float)
    price_currency: Mapped[str] = mapped_column(String)
    price_in_euro: Mapped[float] = mapped_column(Float)
