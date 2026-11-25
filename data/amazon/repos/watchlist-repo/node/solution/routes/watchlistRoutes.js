const express = require('express');
const { authMiddleware } = require('../middleware/auth');
const { watchlistRateLimiter } = require('../middleware/rateLimiter');
const {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
  checkWatchlistStatus,
} = require('../controllers/watchlistController');

const watchlistRouter = express.Router();

watchlistRouter.use(authMiddleware);

watchlistRouter.get('/', getWatchlist);
watchlistRouter.get('/check/:movieId', checkWatchlistStatus);
watchlistRouter.post('/add', watchlistRateLimiter(), addToWatchlist);
watchlistRouter.post('/remove', watchlistRateLimiter(), removeFromWatchlist);

module.exports = watchlistRouter;
