# MovieDB (Spring Boot): User Watchlist

## Overview
MovieDB is an online app that allows users to explore movies, submit ratings, and share reviews.
The watchlist feature helps users save and manage movies they want to watch later. Currently, this
feature is not functioning correctly on the backend and your task is to fix it.

## Expected API Behavior
Every route needs the header `Authorization: Bearer <token>`. `AuthFilter` (the auth middleware) sets the request
attribute `userId`, or answers `401 {"message": "Unauthorized"}`. Errors always have the shape `{"message": "..."}`.

| Route | Rate limited | Success | Errors |
|---|---|---|---|
| `GET /api/watchlist/` | no | `200`, an array of the user's **movie** documents (`id`, `title`, `year`, `genre`) in the order they were added | `500` Server error |
| `GET /api/watchlist/check/{movieId}` | no | `200 {"isInWatchlist": true}` or `false` | `400` Invalid movie ID format |
| `POST /api/watchlist/add` body `{"movieId": "..."}` | yes | `201` Movie added to watchlist successfully | `400` Movie ID is required · `400` Invalid movie ID format · `404` Movie not found · `400` Movie already in watchlist · `429` |
| `POST /api/watchlist/remove` body `{"movieId": "..."}` | yes | `200` Movie removed from watchlist successfully | `400` Movie ID is required · `400` Invalid movie ID format · `404` Movie not found in watchlist · `429` |

Movie ids are 24 hexadecimal characters, like `65f0a1b2c3d4e5f600000002`.

### Rate limiting
Each user can add or remove movies at most **10 times within any 2-minute period**; adds and removes
are counted together. The interceptor runs before the controller, so every add or remove request it lets through
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
| `GET /api/movies/{movieId}` | one movie with its average rating |
| `POST /api/movies/<movieId>/rate` body `{"stars": 1-5, "review"}` | saves the user's rating |

## Test credentials
```
Email: sam.rivera@email.com      Password: Password@123
Email: alex.chen@email.com       Password: Password@123
```

## Getting started
```
mvn test                    # run the tests (Java 17+; the dependencies are already downloaded here)
mvn spring-boot:run         # http://localhost:8080, with an in-memory H2 database seeded at start
```

Example:
```
curl -s -X POST localhost:8080/api/auth/login -H 'Content-Type: application/json' \
     -d '{"email":"sam.rivera@email.com","password":"Password@123"}'
curl -s localhost:8080/api/watchlist/ -H 'Authorization: Bearer <token>'
```

## Project structure
```
src/main/java/com/moviedb/
  MovieDbApplication.java
  model/                    Movie, User, ApiToken, Rating, Watchlist (unique per user + movie)
  repository/               Spring Data JPA repositories
  security/AuthFilter.java  bearer-token authentication (authMiddleware)
  ratelimit/WatchlistRateLimiter.java   the watchlist rate limiter (an interceptor)
  config/WebConfig.java     the routes the rate limiter guards
  config/ObjectIds.java     movie id format
  controller/WatchlistController.java   the watchlist controller
  seed/DataSeeder.java      sample movies and the two users
src/test/java/com/moviedb/watchlist/   the acceptance tests (read-only)
```

## Additional Information
- When movies are added or removed from the watchlist, entries should be created or deleted in the database.
- The app uses an in-memory H2 database, so restarting it resets the data.
- The tests use their own fresh database, seeded on every run.
- The code repository may intentionally contain other issues that are unrelated to this specific task.
  Please focus only on the described task requirements and address bugs or errors directly associated with them.
