from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SearchQuery(BaseModel):
    destination: Optional[str] = None
    departure_city: Optional[str] = None
    departure_date: Optional[date] = None
    return_date: Optional[date] = None
    persons: int = Field(default=1, ge=1, le=20)

    # Frontend-ul poate trimite "" pentru câmpurile goale -> le tratăm ca None
    @field_validator("destination", "departure_city", "departure_date", "return_date", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        if isinstance(value, str) and value.strip() == "":
            return None
        return value.strip() if isinstance(value, str) else value


class Offer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hotel_name: str
    stars: int
    location: str
    price: float
    image_url: Optional[str] = None
    board_type: Optional[str] = None
    description: Optional[str] = None
    departure_city: str
    departure_date: date
    return_date: date
    available_seats: int


class OfferListResponse(BaseModel):
    status: str = "success"
    results_count: int
    data: list[Offer]


class BookingCreate(BaseModel):
    offer_id: int
    full_name: str = Field(min_length=3, max_length=100)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=120)
    phone: str = Field(pattern=r"^\+?[0-9 ()-]{8,20}$")
    persons: int = Field(ge=1, le=20)

    @field_validator("full_name", "email", "phone", mode="before")
    @classmethod
    def strip(cls, value):
        return value.strip() if isinstance(value, str) else value


class Booking(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    offer_id: int
    full_name: str
    email: str
    phone: str
    persons: int
    total_price: float
    created_at: datetime
