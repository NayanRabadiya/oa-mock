# Amazon SDE Intern OA 2026, Section 2: MovieDB (MERN) User Watchlist

Transcribed from 32 phone photos of the test IDE (`PDF Gallery_20260906_153302.pdf`, not kept in this repo).
The photos are blurry in places. Text marked *[unclear]* couldn't be read, and lines cut off at the screen edge are marked `…`.
The API is also in machine-readable form in [`moviedb-watchlist-api.json`](moviedb-watchlist-api.json).

→ Mock question: `data/amazon/questions/watchlist.json`, built from `tools/amazon/watchlist/`.

---

## The platform

- The test IDE was VS Code-like, with an Amazon logo, a countdown (about 59–60 min shown for this section) and a webcam indicator.
- Sections are listed on the left as **S1** (marked complete) and **S2** (current, question **2**).
- The left pane shows **QUESTION DESCRIPTION**, with `README.md` in a preview tab.
- The right side has an **AI Assistant** panel ("Ask the AI Assistant": explain the problem, clarify errors, answer questions…) and a **Run** button with a test panel ("6 tests ran").

## Question description

> **Question 2**
>
> MovieDB is an app that allows users to explore movies, submit ratings, and share reviews.
>
> The watchlist feature helps users save and manage movies they want to watch later. Currently, this feature is not functioning correctly on the backend, affecting usability and engagement.
>
> **Issue Summary:** Users can add movies to their watchlist, but these movies do not appear on the Watchlist page. Fix the backend of the watchlist feature.
>
> **Steps to Reproduce:**
> - Log in with the following test credentials:
>   ```
>   Email: sam.rivera@email.com
>   Password: Password@123
>   ```
> - Select a movie from the list.
> - Add the selected movie to the watchlist. *(screenshot: movie page for "Interstellar" with an "Add to Watchlist" button highlighted)*
> - Click on the user profile present in the navbar and select watchlist. *(screenshot: home page, profile menu open)*
> - The movie should appear here, but currently, there are none.
> - Users should be able to remove movies from the watchlist by either hovering over a movie on the Watchlist page and clicking the delete icon, or by toggling the "Add to Watchlist" button on the movie detail page. *(screenshot: "My Watchlist" page with one poster and a delete icon)*
>
> **Additional Requirements:**
> To prevent spam or automated activity, the system must apply rate limiting. Each user can only add or remove movies up to 10 times within any 2-minute period.
>
> Refer to the README.md file for more details.
>
> **Note:** The acceptance criteria for this task require that your solution pass all predefined unit tests. Use failing test cases to guide debugging.

## README.md: MovieDB (MERN): User Watchlist

> **Overview**
> MovieDB is an online app that allows users to explore movies, submit ratings, and share reviews.
> The watchlist feature helps users save and manage movies they want to watch later. Currently, this feature is not functioning correctly on the backend and your task is to fix it.

**Expected API Behavior.** See `moviedb-watchlist-api.json` for every route, request body and response. In summary:

| Route | Auth | Success | Errors |
|---|---|---|---|
| `GET /api/watchlist/` | Bearer token | 200, an array of movie documents | n/a |
| `GET /api/watchlist/check/:movieId` | Bearer token | 200 `{"inWatchlist": true}` | 400 Invalid movie ID format |
| `POST /api/watchlist/add` | Bearer token + rate limiting | 201 Movie added to watchlist successfully | 400 Movie ID is required · 400 Invalid movie ID format · 404 Movie not found · 400 Movie already in watchlist · 429 rate limit |
| `POST /api/watchlist/remove` | Bearer token + rate limiting | 200 Movie removed from watchlist successfully | 400 Movie ID is required · 400 Invalid movie ID format · 404 Movie not found in watchlist · 429 rate limit |

Rate limiting: "10 add/remove operations per 2 minutes combined". The 429 message starts with *"Too many watchlist operations. You can add or remove movies up to…"* (cut off). The source code completes it as *"…up to 10 times within 2 minutes."*

The README shows the success response of `GET /api/watchlist/check/:movieId` as `{"inWatchlist": true}`. The controller code, in both the original and the candidate's version, returns the key `isInWatchlist`. The mock uses `isInWatchlist`.

**Additional Information**

> - When movies are added/removed from the watchlist, entries should be created/deleted from the database.
> - To manually reset the database, stop the running server and then restart it.
> - Running the test cases will also restore the database to its initial state.
> - The code repository may intentionally contain other issues that are unrelated to this specific task. Please focus only on the described task requirements and address bugs or errors directly associated with them.
> - If you're using Run and Debug mode in the IDE, the frontend server may start before the backend (including database seeding) is ready. In that case, the frontend might not display any data. Please reload the preview once the backend setup is complete.

## Repository layout (file explorer)

```
CHALLENGE/
├── backend/
│   ├── config/
│   ├── controllers/
│   ├── data/
│   ├── middleware/
│   │   ├── admin.js
│   │   ├── auth.js
│   │   └── rateLimiter.js
│   ├── models/
│   ├── node_modules/
│   ├── routes/
│   │   ├── adminMovieRoutes.js
│   │   ├── authRoutes.js
│   │   ├── followRoutes.js
│   │   ├── movieRoutes.js
│   │   ├── notificationRoutes.js
│   │   ├── ratingRoutes.js
│   │   ├── reviewRoutes.js
│   │   └── watchlistRoutes.js
│   ├── test/            (app.spec.js)
│   ├── utils/
│   ├── .env
│   ├── app.js
│   ├── config.json
│   ├── normalize-report.mjs
│   ├── package-lock.json
│   ├── package.json
│   ├── render_report.mjs
│   ├── run_graded.mjs
│   └── test-setup.js
├── frontend/
├── node_modules/
├── output/
├── .gitignore
└── .prettierrc
```

## Original code (as given)

### `backend/routes/adminMovieRoutes.js`

```js
import express from 'express';
import { authMiddleware } from '../middleware/auth.js';
import { adminMiddleware } from '../middleware/admin.js';
import {
  addMovie,
  getUpcoming,
  launchUpcoming
} from '../controllers/adminMovieController.js';

const router = express.Router();

router.use(authMiddleware);
router.use(adminMiddleware);

router.get('/movies/upcoming', getUpcoming);
router.post('/movies', addMovie);
router.post('/movies/:id/launch', launchUpcoming);

export default router;
```

### `backend/routes/watchlistRoutes.js`

No rate limiter is wired in:

```js
import express from 'express';
import { authMiddleware } from '../middleware/auth.js';
import {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  checkWatchlistStatus
} from '../controllers/watchlistController.js';

const router = express.Router();

router.use(authMiddleware);

router.get('/', getWatchlist);
router.get('/check/:movieId', checkWatchlistStatus);
router.post('/add', addToWatchlist);
router.post('/remove', removeFromWatchlist);

export default router;
```

### `backend/controllers/watchlistController.js`

```js
import mongoose from 'mongoose';
import Watchlist from '../models/Watchlist.js';
import Movie from '../models/Movie.js';

export const getWatchlist = async (req, res) => {
  try {
    const userId = req.userId;

    const watchlistItems = await Watchlist.findByUser(userId);

    const movies = watchlistItems
      .filter((item) => item.movie)
      .map((item) => item.movie);

    res.json(movies);
  } catch (error) {
    console.error('Get watchlist error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

export const addToWatchlist = async (req, res) => {
  try {
    const userId = req.userId;
    const { movieId } = req.body;

    if (!movieId) {
      return res.status(400).json({ message: 'Movie ID is required' });
    }

    if (!mongoose.Types.ObjectId.isValid(movieId)) {
      return res.status(400).json({ message: 'Invalid movie ID format' });
    }

    const movie = await Movie.findById(movieId);
    if (!movie) {
      return res.status(404).json({ message: 'Movie not found' });
    }

    res.status(201).json({ message: 'Movie added to watchlist successfully' });
  } catch (error) {
    console.error('Add to watchlist error:', error);

    // Handle duplicate key error (though we check above, this is a safety net)
    if (error.code === 11000) {
      return res.status(400).json({ message: 'Movie already in watchlist' });
    }

    res.status(500).json({ message: 'Server error' });
  }
};

export const removeFromWatchlist = async (req, res) => {
  try {
    const userId = req.userId;
    const { movieId } = req.body;

    if (!movieId) {
      return res.status(400).json({ message: 'Movie ID is required' });
    }

    if (!mongoose.Types.ObjectId.isValid(movieId)) {
      return res.status(400).json({ message: 'Invalid movie ID format' });
    }

    res.json({ message: 'Movie removed from watchlist successfully' });
  } catch (error) {
    console.error('Remove from watchlist error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

export const checkWatchlistStatus = async (req, res) => {
  try {
    const userId = req.userId;
    const { movieId } = req.params;

    if (!mongoose.Types.ObjectId.isValid(movieId)) {
      return res.status(400).json({ message: 'Invalid movie ID format' });
    }

    const isInWatchlist = await Watchlist.find({ user: userId, movie: movieId });

    res.json({ isInWatchlist });
  } catch (error) {
    console.error('Check watchlist status error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};
```

### `backend/middleware/rateLimiter.js`

```js
const rateLimitStore = new Map();

export const rateLimiter = () => {
  return (req, res, next) => {
    const userId = req.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const key = `${userId}-${req.path}`;
    const now = Date.now();

    if (!rateLimitStore.has(key)) {
      rateLimitStore.set(key, []);
    }

    const userRequests = rateLimitStore.get(key);
    const requests = userRequests.filter(
      (timestamp) => now - timestamp >= windowMs
    );

    if (requests) {
      return res.status(429).json({
        message: 'Too many requests. Please try again in 1 minute.'
      });
    }

    validRequests.push(now);
    rateLimitStore.set(key, validRequests);

    if (Math.random() < 0.01) {
      cleanupRateLimitStore(windowMs);
    }

    next();
  };
};

export const watchlistRateLimiter = () => {
  return (req, res, next) => {
    const userId = req.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const key = `${userId}-watchlist-operations`;
    const now = Date.now();

    if (!rateLimitStore.has(key)) {
      rateLimitStore.set(key, []);
    }

    const userRequests = rateLimitStore.get(key);
    const requests = userRequests.filter(
      (timestamp) => now - timestamp >= windowMs
    );

    if (requests) {
      return res.status(429).json({
        message: `Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes.`
      });
    }

    validRequests.push(now);
    rateLimitStore.set(key, validRequests);

    if (Math.random() < 0.01) {
      cleanupRateLimitStore(windowMs);
    }

    next();
  };
};

function cleanupRateLimitStore(windowMs) {
  const now = Date.now();

  for (const [key, timestamps] of rateLimitStore.entries()) {
    const validTimestamps = timestamps.filter(
      (timestamp) => now - timestamp < windowMs
    );

    if (validTimestamps.length === 0) {
      rateLimitStore.delete(key);
    } else {
      rateLimitStore.set(key, validTimestamps);
    }
  }
}

export default rateLimiter;
```

## Bugs this code contains

These are the defects the mock reproduces, worked out by reading the code above:

1. `getWatchlist` calls `Watchlist.findByUser`, which the model doesn't define, so the list request fails. The fix is `Watchlist.find({ user: userId }).populate('movie')`.
2. `addToWatchlist` never creates the watchlist entry, and never checks for a duplicate (expected: 400 *Movie already in watchlist*).
3. `removeFromWatchlist` never deletes anything and never answers 404 *Movie not found in watchlist*.
4. `checkWatchlistStatus` returns the array from `find()` instead of a boolean.
5. Both limiters:
   - `windowMs` is never defined.
   - The filter keeps the *expired* timestamps (`>=` should be `<`).
   - `if (requests)` is always true, because an empty array is truthy.
   - `validRequests` is never declared.
6. The routes don't use any limiter. Wiring `rateLimiter` without calling it, i.e. passing the factory as middleware, makes requests hang.

## What the candidate did (later photos)

1. Wired the limiter as `router.post('/add', rateLimiter, addToWatchlist)` (not called). Every test then failed with
   `Error: Timeout of 20000ms exceeded. For async tests and hooks, ensure "done()" is called; if returning a Promise, ensure it resolves. (/projects/challenge/backend/test/app.spec.js)`
2. In `watchlistRateLimiter` they defined `const windowMs = 2 * 60 * 1000;`, kept `validRequests = userRequests.filter((t) => now - t < windowMs)` and rejected when `validRequests.length >= 10`. They commented out the old filter and `if (requests)` block, and wired `watchlistRateLimiter()` (called) on `/add` and `/remove`.
3. Controller changes:
   - `getWatchlist`: `await Watchlist.find({user: userId}).populate('movie')`, then `res.status(200).json(movies)`.
   - `addToWatchlist`: `const present = await Watchlist.findOne({user: userId, movie: movieId}); if (present) { res.status(404).json({ message: 'Movie already in watchlist' }); }`. Note the **404** and the missing `return`. Then `await Watchlist.create({ user: userId, movie: movieId })`.
   - `removeFromWatchlist`: `const deleted = await Watchlist.findOneAndDelete({ user: userId, movie: movieId }); if (!deleted) return res.status(404).json({ message: 'Movie not found in watchlist' });`.
   - `checkWatchlistStatus`: `const isInWatchlist = await Watchlist.findOne(...)`, then `res.status(200).json({ isInWatchlist: !!isInWatchlist })`.
4. Result: "6 tests ran", with 5 passing and 1 failing. The failing test was about adding duplicate movies:
   `AssertionError: expected Response{ … } to have status … but got 404`, at `Context.<anonymous> (file:///projects/challenge/backend/test/app.spec.js:188:30)`.
   The duplicate case expected **400**, not 404.

## Test names (as far as they could be read)

The test panel listed 6 tests under "User Watchlist API Testing". The names were cut off at the panel edge:

1. … should add movie to watchlist successfully *[approx.]*
2. … remove movie from watchlist s… *[approx.]*
3. … movies and remove spe… *[approx.]*
4. … adding duplicate movies and re… *(the one that failed)*
5. … show whether a movie is in the watchlist
6. … rate limiting if over 10 add/remove…
