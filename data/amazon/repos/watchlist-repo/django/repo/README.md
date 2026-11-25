# MovieDB (Django): User Watchlist

## Overview
MovieDB is an online app that allows users to explore movies, submit ratings, and share reviews.
The watchlist feature helps users save and manage movies they want to watch later. Currently, this
feature is not functioning correctly on the backend and your task is to fix it.

## Expected API Behavior
Every route needs the header `Authorization: Bearer <token>`. Without a valid token the API answers
`401 {"message": "Unauthorized"}`. Errors always have the shape `{"message": "..."}`.

| Route | Rate limited | Success | Errors |
|---|---|---|---|
| `GET /api/watchlist/` | no | `200`, an array of the user's **movie** documents (`id`, `title`, `year`, `genre`) in the order they were added | `500` Server error |
| `GET /api/watchlist/check/<movieId>` | no | `200 {"isInWatchlist": true}` or `false` | `400` Invalid movie ID format |
| `POST /api/watchlist/add` body `{"movieId": "..."}` | yes | `201` Movie added to watchlist successfully | `400` Movie ID is required · `400` Invalid movie ID format · `404` Movie not found · `400` Movie already in watchlist · `429` |
| `POST /api/watchlist/remove` body `{"movieId": "..."}` | yes | `200` Movie removed from watchlist successfully | `400` Movie ID is required · `400` Invalid movie ID format · `404` Movie not found in watchlist · `429` |

Movie ids are 24 hexadecimal characters, like `65f0a1b2c3d4e5f600000002`.

### Rate limiting
Each user can add or remove movies at most **10 times within any 2-minute period**; adds and removes
are counted together. The check runs before the view, so every add or remove request it lets through
counts, even one that then fails validation. A rejected request doesn't count. A request made at time
`t` stops counting once `now - t >= 2 minutes`. When the limit is reached the API answers:

```
429 {"message": "Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes."}
```

### Other endpoints (working)
| Route | Notes |
|---|---|
| `POST /api/auth/login` body `{"email", "password"}` | `200 {"token": "...", "user": {...}}`, no token needed |
| `GET /api/movies/` | every movie |
| `GET /api/movies/<movieId>` | one movie with its average rating |
| `POST /api/movies/<movieId>/rate` body `{"stars": 1-5, "review"}` | saves the user's rating |

## Test credentials
```
Email: sam.rivera@email.com      Password: Password@123
Email: alex.chen@email.com       Password: Password@123
```

## Getting started
```
pip install -r requirements.txt     # already done in this environment
python manage.py migrate            # create the database (db.sqlite3)
python manage.py seed               # add the sample movies and the two users
python manage.py runserver          # http://127.0.0.1:8000
python manage.py test               # run the tests
```

Example:
```
curl -s -X POST localhost:8000/api/auth/login -H 'Content-Type: application/json' \
     -d '{"email":"sam.rivera@email.com","password":"Password@123"}'
curl -s localhost:8000/api/watchlist/ -H 'Authorization: Bearer <token>'
```

## Project structure
```
moviedb/        settings, root urls, error format (exceptions.py)
accounts/       users, login, bearer-token authentication (authMiddleware)
movies/         movies and ratings
watchlist/
  models.py       Watchlist(user, movie, created_at), unique per user + movie
  views.py        the watchlist controller
  urls.py         the watchlist routes
  throttling.py   watchlistRateLimiter (10 operations per 2 minutes)
  validators.py   movie id format
  tests/          the acceptance tests (read-only)
```

## Additional Information
- When movies are added or removed from the watchlist, entries should be created or deleted in the database.
- To reset the database, delete `db.sqlite3` and run `migrate` and `seed` again.
- The tests use their own fresh database, seeded on every run.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
