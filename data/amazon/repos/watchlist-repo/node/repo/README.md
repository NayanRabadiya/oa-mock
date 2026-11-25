# MovieDB (MERN): User Watchlist

## Overview
MovieDB is an online app that allows users to explore movies, submit ratings, and share reviews.
The watchlist feature helps users save and manage movies they want to watch later. Currently, this
feature is not functioning correctly on the backend and your task is to fix it.

## Expected API Behavior
Every route needs the header `Authorization: Bearer <token>`. `authMiddleware` sets `req.userId` or answers
`401 {"message": "Unauthorized"}`. Errors always have the shape `{"message": "..."}`.

| Route | Rate limited | Success | Errors |
|---|---|---|---|
| `GET /api/watchlist/` | no | `200`, an array of the user's **movie** documents (`_id`, `title`, `year`, `genre`) in the order they were added | `500` Server error |
| `GET /api/watchlist/check/:movieId` | no | `200 {"isInWatchlist": true}` or `false` | `400` Invalid movie ID format |
| `POST /api/watchlist/add` body `{"movieId": "..."}` | yes | `201` Movie added to watchlist successfully | `400` Movie ID is required · `400` Invalid movie ID format · `404` Movie not found · `400` Movie already in watchlist · `429` |
| `POST /api/watchlist/remove` body `{"movieId": "..."}` | yes | `200` Movie removed from watchlist successfully | `400` Movie ID is required · `400` Invalid movie ID format · `404` Movie not found in watchlist · `429` |

Movie ids are MongoDB ObjectIds, like `65f0a1b2c3d4e5f600000002`.

### Rate limiting
Each user can add or remove movies at most **10 times within any 2-minute period**; adds and removes
are counted together. The limiter runs before the controller, so every add or remove request it lets
through counts, even one that then fails validation. A rejected request doesn't count. A request made at
time `t` stops counting once `now - t >= 2 minutes`. When the limit is reached the API answers:

```
429 {"message": "Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes."}
```

### Other endpoints (working)
| Route | Notes |
|---|---|
| `POST /api/auth/login` body `{"email", "password"}` | `200 {"token": "...", "user": {...}}`, no token needed |
| `GET /api/movies/` | every movie |
| `GET /api/movies/:movieId` | one movie with its average rating |
| `POST /api/movies/:movieId/rate` body `{"stars": 1-5, "review"}` | saves the user's rating |

## Test credentials
```
Email: sam.rivera@email.com      Password: Password@123
Email: alex.chen@email.com       Password: Password@123
```

## Getting started
```
npm install          # already done in this environment
npm test             # run the tests (they start their own in-memory MongoDB)
cp .env.example .env # then point MONGO_URI at a running MongoDB to use the app itself
npm run seed         # add the sample movies and the two users
npm start            # http://localhost:5000
```

## Project structure
```
app.js                          the Express app and its routers
server.js                       connects to MongoDB and starts the server
config/db.js                    the MongoDB connection
models/                         User, Movie, Rating, Watchlist (unique per user + movie)
middleware/auth.js              authMiddleware (JWT)
middleware/rateLimiter.js       rateLimiter and watchlistRateLimiter
controllers/watchlistController.js   the watchlist controller
routes/watchlistRoutes.js       the watchlist routes
tests/                          the acceptance tests (read-only)
```

## Additional Information
- When movies are added or removed from the watchlist, entries should be created or deleted in the database.
- Running the tests starts a fresh in-memory database, seeded for every test.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
