from typing import Any
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from core.database import Base


class Airport(Base):
    __tablename__ = "airports"

    iata_code: Mapped[str] = mapped_column(String(3), primary_key=True)
    name: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    timezone: Mapped[str] = mapped_column(String)

    location: Mapped[Any] = mapped_column(Geometry(geometry_type="POINT", srid=4326))




