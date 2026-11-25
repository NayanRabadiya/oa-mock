const express = require('express');
const { authMiddleware } = require('../middleware/auth');
const { rateLimiter } = require('../middleware/rateLimiter');
const { listMovies, getMovie, rateMovie } = require('../controllers/movieController');

const router = express.Router();

router.use(authMiddleware);

router.get('/', listMovies);
router.get('/:movieId', getMovie);
router.post('/:movieId/rate', rateLimiter(), rateMovie);

module.exports = router;
