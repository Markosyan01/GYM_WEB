# Iron Yard Gym

React + FastAPI + MySQL, run with Docker Compose.

    docker compose up --build

- Site: http://localhost:3000
- API docs: http://localhost:8000/docs

Languages: English, Russian, Armenian (switcher in the header; choice is remembered).
Features: home with photos, class timetable with booking, plans, trainers, shop with cart and orders, gallery with lightbox, contact form + FAQ, JWT accounts.
trainers, JWT register/login, account page. Sample data is seeded on first start.
Copy `.env.example` to `.env` to change credentials (set a real SECRET_KEY).

Images are local illustrations in `frontend/public/images/` (no external hosts). Regenerate or restyle
them with `python3 tools/make_images.py`. To use real photos, drop files in that folder and change the
`image` values in `backend/app/seed.py` (e.g. `/images/rack.jpg`); the Hero uses `/images/hero.svg`.

Upgrading from the first version: run `docker compose down -v` once to reset the database
(new columns and tables), then `docker compose up --build`.

## Translations
All UI text and the seeded gym content (plans, classes, trainers, products) are translated in
`frontend/src/translations.js`. Keys are the English texts; anything missing falls back to English.
To translate content you add later, add its English text as a key in both `ru` and `hy`.
