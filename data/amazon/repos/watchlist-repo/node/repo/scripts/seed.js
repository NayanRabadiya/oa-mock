// npm run seed: the sample movies and the two test users from the README. Safe to run again.
require('dotenv').config();
const bcrypt = require('bcryptjs');
const mongoose = require('mongoose');
const connectDB = require('../config/db');
const Movie = require('../models/Movie');
const User = require('../models/User');

const M = (i) => '65f0a1b2c3d4e5f6' + String(i).padStart(8, '0');
const MOVIES = [
  [1, 'The Shawshank Redemption', 1994, 'Drama'],
  [2, 'Interstellar', 2014, 'Sci-Fi'],
  [3, 'The Dark Knight', 2008, 'Action'],
  [4, 'Spirited Away', 2001, 'Animation'],
  [5, 'Parasite', 2019, 'Thriller'],
  [6, 'Inception', 2010, 'Sci-Fi'],
];
const USERS = [
  ['Sam Rivera', 'sam.rivera@email.com'],
  ['Alex Chen', 'alex.chen@email.com'],
];

(async () => {
  await connectDB();
  for (const [i, title, year, genre] of MOVIES) {
    await Movie.updateOne({ _id: M(i) }, { title, year, genre }, { upsert: true });
  }
  const password = await bcrypt.hash('Password@123', 10);
  for (const [name, email] of USERS) {
    await User.updateOne({ email }, { name, email, password }, { upsert: true });
  }
  console.log(`Seeded ${MOVIES.length} movies and ${USERS.length} users.`);
  await mongoose.disconnect();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
