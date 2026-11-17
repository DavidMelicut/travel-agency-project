from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import get_db
from schemas import Booking, BookingCreate, Offer, OfferListResponse, SearchQuery
from services import BookingService, NotEnoughSeats, OfferNotFound, OfferService

app = FastAPI(title="Travel Agency Project API", version="1.0.0")

# CORS: permite și deschiderea paginilor direct din fișier / Live Server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# 1. CĂUTARE OFERTE
@app.post("/api/search", response_model=OfferListResponse)
def perform_search(query: SearchQuery, db: Session = Depends(get_db)):
    results = OfferService(db).search_offers(query)
    return {"results_count": len(results), "data": results}


# 2. OFERTE POPULARE (pagina principală)
@app.get("/api/popular-offers", response_model=OfferListResponse)
def get_popular_offers(db: Session = Depends(get_db)):
    offers = OfferService(db).popular_offers()
    return {"results_count": len(offers), "data": offers}


# 3. DETALII OFERTĂ
@app.get("/api/offers/{offer_id}", response_model=Offer)
def get_offer(offer_id: int, db: Session = Depends(get_db)):
    try:
        return OfferService(db).get_offer(offer_id)
    except OfferNotFound:
        raise HTTPException(status_code=404, detail="Oferta nu a fost găsită.")


# 4. REZERVARE
@app.post("/api/bookings", response_model=Booking, status_code=201)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    try:
        return BookingService(db).create_booking(data)
    except OfferNotFound:
        raise HTTPException(status_code=404, detail="Oferta nu mai este disponibilă.")
    except NotEnoughSeats as e:
        raise HTTPException(status_code=409, detail=str(e))


# Servim și frontend-ul din același server -> http://127.0.0.1:8000/
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.is_dir():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
