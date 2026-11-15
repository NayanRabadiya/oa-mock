const mongoose = require('mongoose');
const Movie = require('../models/Movie');
const Watchlist = require('../models/Watchlist');

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

module.exports = { getWatchlist, addToWatchlist, removeFromWatchlist, checkWatchlistStatus };
