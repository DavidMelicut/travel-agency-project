"""Recreează tabelele și le populează cu oferte demo.

Rulare:  python populate_db.py
ATENȚIE: șterge toate datele existente (oferte + rezervări).
"""
from datetime import date, timedelta

from sqlalchemy import text

from database import Base, SessionLocal, engine
from models import BookingDB, OfferDB  # noqa: F401  (importul înregistrează tabelele)

IMG_RESORT = "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80"
IMG_POOL = "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80"
IMG_ISLAND = "https://images.unsplash.com/photo-1539020140153-e479b8c22e70?w=800&q=80"
IMG_LUXURY = "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80"


def trip(start_in_days: int, nights: int):
    """Datele sunt relative la ziua de azi, ca ofertele demo să fie mereu în viitor."""
    start = date.today() + timedelta(days=start_in_days)
    return start, start + timedelta(days=nights)


OFFERS = [
    ("Blue Palace Resort", 5, "Creta, Grecia", 1250.0, IMG_RESORT, "All Inclusive", "București", 30, 7, 10),
    ("Sunshine Village", 4, "Creta, Grecia", 890.0, IMG_POOL, "Demipensiune", "Cluj-Napoca", 30, 7, 2),
    ("Knossos Beach Hotel", 3, "Creta, Grecia", 610.0, IMG_ISLAND, "Mic dejun", "Iași", 45, 7, 14),
    ("Tenerife Sol", 4, "Tenerife, Spania", 1100.0, IMG_ISLAND, "Mic dejun", "București", 60, 7, 4),
    ("Costa Adeje Gran Hotel", 5, "Tenerife, Spania", 1590.0, IMG_LUXURY, "All Inclusive", "Cluj-Napoca", 62, 7, 8),
    ("Rixos Premium", 5, "Antalya, Turcia", 1450.0, IMG_LUXURY, "Ultra All Inclusive", "Timișoara", 20, 7, 6),
    ("Lara Family Club", 4, "Antalya, Turcia", 780.0, IMG_POOL, "All Inclusive", "București", 21, 7, 20),
    ("Hurghada Coral Bay", 4, "Hurghada, Egipt", 690.0, IMG_RESORT, "All Inclusive", "Cluj-Napoca", 40, 7, 12),
    ("Marina Mallorca", 3, "Mallorca, Spania", 720.0, IMG_ISLAND, "Demipensiune", "Târgu Mureș", 75, 7, 9),
    ("Dubrovnik Old Town Suites", 4, "Dubrovnik, Croația", 960.0, IMG_RESORT, "Mic dejun", "București", 50, 5, 5),
]


def populate_database():
    with engine.begin() as conn:
        # Necesar pentru căutarea fără diacritice (Timișoara == Timisoara)
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for hotel, stars, location, price, img, board, city, start, nights, seats in OFFERS:
            dep, ret = trip(start, nights)
            db.add(OfferDB(
                hotel_name=hotel,
                stars=stars,
                location=location,
                price=price,
                image_url=img,
                board_type=board,
                description=f"{nights} nopți la {hotel}, {location}. Zbor dus-întors din {city}, "
                            f"transfer aeroport-hotel și {board.lower()} incluse.",
                departure_city=city,
                departure_date=dep,
                return_date=ret,
                available_seats=seats,
            ))
        db.commit()
        print(f"Succes! Baza de date a fost recreată cu {len(OFFERS)} oferte.")
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
