from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


from app.core.database import Base



class Country(Base):
    __tablename__ = "countries"

    name: Mapped[str] = mapped_column(String(50), primary_key=True)
    code: Mapped[str] = mapped_column(String(2))
