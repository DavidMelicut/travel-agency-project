-- Rulează o singură dată, ca utilizator postgres (ex. din psql sau pgAdmin):
--   psql -U postgres -f database/setup.sql

CREATE DATABASE travel_agency;

\connect travel_agency

-- Extensia folosită pentru căutarea fără diacritice (Timișoara == Timisoara).
-- populate_db.py o creează și el automat, dacă utilizatorul are drepturi.
CREATE EXTENSION IF NOT EXISTS unaccent;
