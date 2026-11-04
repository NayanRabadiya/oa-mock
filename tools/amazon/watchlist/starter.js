// ---- file: controllers/watchlistController.js ---------------------------
const getWatchlist = async (req, res) => {
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

const addToWatchlist = async (req, res) => {
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

const removeFromWatchlist = async (req, res) => {
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

const checkWatchlistStatus = async (req, res) => {
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

// ---- file: middleware/rateLimiter.js ------------------------------------
const rateLimitStore = new Map();

// General-purpose limiter used by other routers (reviews, ratings)
const rateLimiter = (windowMs = 60 * 1000, max = 30) => {
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
        message: 'Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes.'
      });
    }

    validRequests.push(now);
    rateLimitStore.set(key, validRequests);

    next();
  };
};

// ---- file: routes/watchlistRoutes.js ------------------------------------
const watchlistRouter = express.Router();

watchlistRouter.use(authMiddleware);

watchlistRouter.get('/', getWatchlist);
watchlistRouter.get('/check/:movieId', checkWatchlistStatus);
watchlistRouter.post('/add', addToWatchlist);
watchlistRouter.post('/remove', removeFromWatchlist);
