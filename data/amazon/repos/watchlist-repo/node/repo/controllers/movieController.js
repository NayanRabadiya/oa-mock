const mongoose = require('mongoose');
const Movie = require('../models/Movie');
const Rating = require('../models/Rating');

const listMovies = async (req, res) => {
  try {
    res.json(await Movie.find().sort({ title: 1 }));
  } catch (error) {
    console.error('List movies error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

const getMovie = async (req, res) => {
  try {
    if (!mongoose.Types.ObjectId.isValid(req.params.movieId)) {
      return res.status(400).json({ message: 'Invalid movie ID format' });
    }
    const movie = await Movie.findById(req.params.movieId);
    if (!movie) {
      return res.status(404).json({ message: 'Movie not found' });
    }
    const ratings = await Rating.find({ movie: movie._id });
    const total = ratings.reduce((sum, r) => sum + r.stars, 0);
    res.json({
      ...movie.toJSON(),
      averageRating: ratings.length ? Math.floor(total / ratings.length) : null,
      ratingsCount: ratings.length,
    });
  } catch (error) {
    console.error('Get movie error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

const rateMovie = async (req, res) => {
  try {
    const { stars, review = '' } = req.body;
    if (!Number.isInteger(stars) || stars < 1 || stars > 5) {
      return res.status(400).json({ message: 'Stars must be a whole number from 1 to 5' });
    }
    if (!mongoose.Types.ObjectId.isValid(req.params.movieId) || !(await Movie.exists({ _id: req.params.movieId }))) {
      return res.status(404).json({ message: 'Movie not found' });
    }
    await Rating.findOneAndUpdate(
      { movie: req.params.movieId, user: req.userId },
      { stars, review },
      { upsert: true }
    );
    res.status(201).json({ message: 'Rating saved' });
  } catch (error) {
    console.error('Rate movie error:', error);
    res.status(500).json({ message: 'Server error' });
  }
};

module.exports = { listMovies, getMovie, rateMovie };
