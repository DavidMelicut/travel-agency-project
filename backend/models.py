from datetime import datetime

from sqlalchemy import CheckConstraint, Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class OfferDB(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    hotel_name = Column(String, nullable=False, index=True)
    stars = Column(Integer, nullable=False)
    location = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)  # preț per persoană, în EUR
    image_url = Column(String)
    board_type = Column(String)
    description = Column(String)

    departure_city = Column(String, nullable=False)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    available_seats = Column(Integer, nullable=False, default=0)

    bookings = relationship("BookingDB", back_populates="offer", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("stars BETWEEN 1 AND 5", name="ck_offers_stars"),
        CheckConstraint("price >= 0", name="ck_offers_price"),
        CheckConstraint("available_seats >= 0", name="ck_offers_seats"),
        CheckConstraint("return_date > departure_date", name="ck_offers_dates"),
    )


class BookingDB(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    persons = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    offer = relationship("OfferDB", back_populates="bookings")

    __table_args__ = (CheckConstraint("persons > 0", name="ck_bookings_persons"),)
