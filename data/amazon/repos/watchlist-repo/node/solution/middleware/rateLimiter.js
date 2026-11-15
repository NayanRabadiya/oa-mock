const rateLimitStore = new Map();

// The limiters read the time from here, so the tests can move it.
const clock = { now: () => Date.now() };

// General-purpose limiter used by other routers (reviews, ratings)
const rateLimiter = (windowMs = 60 * 1000, max = 30) => {
  return (req, res, next) => {
    const userId = req.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const key = `${userId}-${req.path}`;
    const now = clock.now();

    if (!rateLimitStore.has(key)) {
      rateLimitStore.set(key, []);
    }

    const userRequests = rateLimitStore.get(key);
    const validRequests = userRequests.filter((timestamp) => now - timestamp < windowMs);

    if (validRequests.length >= max) {
      return res.status(429).json({
        message: 'Too many requests. Please try again in 1 minute.'
      });
    }

    validRequests.push(now);
    rateLimitStore.set(key, validRequests);
    next();
  };
};

// Watchlist add/remove: 10 operations per user per 2 minutes, add and remove combined
const watchlistRateLimiter = () => {
  return (req, res, next) => {
    const userId = req.userId;

    if (!userId) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const key = `${userId}-watchlist-operations`;
    const now = clock.now();

    if (!rateLimitStore.has(key)) {
      rateLimitStore.set(key, []);
    }

    const windowMs = 2 * 60 * 1000;
    const userRequests = rateLimitStore.get(key);
    const validRequests = userRequests.filter(
      (timestamp) => now - timestamp < windowMs
    );

    if (validRequests.length >= 10) {
      return res.status(429).json({
        message: 'Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes.'
      });
    }

    validRequests.push(now);
    rateLimitStore.set(key, validRequests);

    next();
  };
};

module.exports = { rateLimiter, watchlistRateLimiter, rateLimitStore, clock };
