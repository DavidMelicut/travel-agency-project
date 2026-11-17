# Travel Agency Project

A full-stack web app for a (fictional) travel agency: users search holiday packages, filter and sort the results, open an offer and send a booking that is saved in a PostgreSQL database.

**Stack:** Python · FastAPI · SQLAlchemy · PostgreSQL · HTML · CSS · JavaScript (vanilla) · Flatpickr

## Features

- **Search** by destination, departure city, dates and number of people
  - accent- and hyphen-insensitive matching (`timisoara` → *Timișoara*, `cluj napoca` → *Cluj-Napoca*) using PostgreSQL's `unaccent`
  - flexible dates (±3 days around the chosen departure/return dates)
  - only offers with enough free seats are returned
- **Popular offers** on the home page (4★+ hotels, cheapest first)
- **Client-side filters & sorting** on the results page: stars, board type, max price per person, sort by price/stars/date
- **Offer page + booking form** – validated on the client and the server; the booking is stored in a `bookings` table and the available seats are decreased in the same transaction (`SELECT … FOR UPDATE`, so two simultaneous bookings can't oversell a trip)
- REST API with automatic docs (Swagger) at `/docs`
- Responsive layout (desktop / tablet / phone)

## Project structure

```
backend/
  main.py          FastAPI app – API endpoints + serves the frontend
  services.py      Search and booking logic
  models.py        SQLAlchemy models (offers, bookings)
  schemas.py       Pydantic request/response schemas and validation
  database.py      DB connection (reads DATABASE_URL from .env)
  populate_db.py   Creates the tables and inserts demo offers
  requirements.txt
  .env.example
database/
  setup.sql        Creates the database and the unaccent extension
frontend/
  index.html       Home page – search + popular offers
  rezultate.html   Search results with filters and sorting
  oferta.html      Offer details + booking form
  style.css
  js/common.js     Shared helpers (API calls, formatting, date pickers)
```

## API

| Method | Endpoint               | Description                         |
|--------|------------------------|-------------------------------------|
| POST   | `/api/search`          | Search offers                       |
| GET    | `/api/popular-offers`  | Up to 6 popular offers              |
| GET    | `/api/offers/{id}`     | Offer details                       |
| POST   | `/api/bookings`        | Create a booking (409 if sold out)  |

## Running locally

Requirements: Python 3.10+ and PostgreSQL.

```bash
# 1. Create the database (once)
psql -U postgres -f database/setup.sql

# 2. Install the dependencies
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt

# 3. Configure the connection
copy .env.example .env          # Linux/macOS: cp .env.example .env
#    then put your PostgreSQL password in .env

# 4. Create the tables and the demo data
python populate_db.py

# 5. Start the server
python main.py
```

Open **http://127.0.0.1:8000** for the website and **http://127.0.0.1:8000/docs** for the API docs.

> If your password contains `@`, `:`, `/` or `#`, URL-encode it in `DATABASE_URL` (e.g. `@` → `%40`).

## Notes

The agency is fictional and the site was built as a personal project; the company details in the footer are placeholders. Demo offer dates are generated relative to the current day, so the data never expires.
