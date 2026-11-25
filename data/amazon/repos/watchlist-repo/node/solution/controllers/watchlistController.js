const mongoose = require('mongoose');
const Movie = require('../models/Movie');
const Watchlist = require('../models/Watchlist');

const getWatchlist = async (req, res) => {
  try {
    const userId = req.userId;

    const watchlistItems = await Watchlist.find({ user: userId }).sort({ createdAt: 1, _id: 1 }).populate('movie');

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

    const existing = await Watchlist.findOne({ user: userId, movie: movieId });
    if (existing) {
      return res.status(400).json({ message: 'Movie already in watchlist' });
    }

    await Watchlist.create({ user: userId, movie: movieId });

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

    const deleted = await Watchlist.findOneAndDelete({ user: userId, movie: movieId });
    if (!deleted) {
      return res.status(404).json({ message: 'Movie not found in watchlist' });
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

    const entry = await Watchlist.findOne({ user: userId, movie: movieId });

    res.json({ isInWatchlist: !!entry });
  } catch (error) {
    console.error('Check watchlist status error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

module.exports = { getWatchlist, addToWatchlist, removeFromWatchlist, checkWatchlistStatus };
