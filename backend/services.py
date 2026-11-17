from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import BookingDB, OfferDB
from schemas import BookingCreate, SearchQuery

# Câte zile în plus/minus acceptăm față de datele alese de utilizator
DATE_FLEX_DAYS = 3


class OfferNotFound(Exception):
    pass


class NotEnoughSeats(Exception):
    def __init__(self, available: int):
        self.available = available
        super().__init__(f"Mai sunt doar {available} locuri disponibile.")


def _normalize(column_or_text):
    """unaccent + fără spații și cratime -> 'Cluj Napoca' == 'cluj-napoca' == 'Cluj-Napoca'."""
    return func.replace(func.replace(func.unaccent(column_or_text), "-", ""), " ", "")


class OfferService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def _upcoming(self):
        return self.db.query(OfferDB).filter(OfferDB.departure_date >= date.today())

    def search_offers(self, query: SearchQuery) -> list[OfferDB]:
        q = self._upcoming()

        if query.destination:
            q = q.filter(func.unaccent(OfferDB.location).ilike(func.unaccent(f"%{query.destination}%")))

        if query.departure_city:
            q = q.filter(_normalize(OfferDB.departure_city).ilike(_normalize(f"%{query.departure_city}%")))

        flex = timedelta(days=DATE_FLEX_DAYS)
        if query.departure_date:
            q = q.filter(OfferDB.departure_date.between(query.departure_date - flex, query.departure_date + flex))

        if query.return_date:
            q = q.filter(OfferDB.return_date.between(query.return_date - flex, query.return_date + flex))

        q = q.filter(OfferDB.available_seats >= query.persons)

        return q.order_by(OfferDB.price.asc()).all()

    def popular_offers(self, limit: int = 6) -> list[OfferDB]:
        return (
            self._upcoming()
            .filter(OfferDB.stars >= 4, OfferDB.available_seats > 0)
            .order_by(OfferDB.price.asc())
            .limit(limit)
            .all()
        )

    def get_offer(self, offer_id: int) -> OfferDB:
        offer = self.db.get(OfferDB, offer_id)
        if offer is None:
            raise OfferNotFound()
        return offer


class BookingService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_booking(self, data: BookingCreate) -> BookingDB:
        # SELECT ... FOR UPDATE: blocăm rândul ofertei ca două rezervări simultane
        # să nu poată vinde același loc de două ori
        offer = (
            self.db.query(OfferDB)
            .filter(OfferDB.id == data.offer_id)
            .with_for_update()
            .one_or_none()
        )
        if offer is None or offer.departure_date < date.today():
            self.db.rollback()
            raise OfferNotFound()

        if offer.available_seats < data.persons:
            available = offer.available_seats
            self.db.rollback()
            raise NotEnoughSeats(available)

        offer.available_seats -= data.persons
        booking = BookingDB(
            offer_id=offer.id,
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            persons=data.persons,
            total_price=round(offer.price * data.persons, 2),
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
