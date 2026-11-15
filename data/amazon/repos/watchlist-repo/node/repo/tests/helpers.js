// Shared setup for the watchlist tests: an in-memory MongoDB with the sample movies and two users.
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const request = require('supertest');
const { MongoMemoryServer } = require('mongodb-memory-server');

const app = require('../app');
const Movie = require('../models/Movie');
const User = require('../models/User');
const Watchlist = require('../models/Watchlist');
const { JWT_SECRET } = require('../middleware/auth');
const { rateLimitStore, clock } = require('../middleware/rateLimiter');

const M = (i) => '65f0a1b2c3d4e5f6' + String(i).padStart(8, '0');
const TITLES = ['The Shawshank Redemption', 'Interstellar', 'The Dark Knight', 'Spirited Away', 'Parasite', 'Inception'];
const START = 1_700_000_000_000;

let mongo;
const ctx = { sam: null, alex: null, now: START };

function setupDatabase() {
  beforeAll(async () => {
    mongo = await MongoMemoryServer.create();
    await mongoose.connect(mongo.getUri());
    await Watchlist.init();
  });
  afterAll(async () => {
    await mongoose.disconnect();
    if (mongo) await mongo.stop();
  });
  beforeEach(async () => {
    await Promise.all(Object.values(mongoose.connection.collections).map((c) => c.deleteMany({})));
    rateLimitStore.clear();
    ctx.now = START;
    clock.now = () => ctx.now;
    await Movie.insertMany(TITLES.map((title, i) => ({ _id: M(i + 1), title, year: 2001 + i, genre: 'Drama' })));
    ctx.sam = await User.create({ name: 'Sam Rivera', email: 'sam.rivera@email.com', password: 'x' });
    ctx.alex = await User.create({ name: 'Alex Chen', email: 'alex.chen@email.com', password: 'x' });
  });
}

// Moves the clock the rate limiter sees to `seconds` after the start of the test.
const at = (seconds) => { ctx.now = START + seconds * 1000; };

const token = (user) => 'Bearer ' + jwt.sign({ userId: user._id.toString() }, JWT_SECRET);
const as = (user) => ({
  get: (url) => (user ? request(app).get(url).set('Authorization', token(user)) : request(app).get(url)),
  post: (url, body) => (user ? request(app).post(url).set('Authorization', token(user)) : request(app).post(url)).send(body),
});
const add = (user, movieId) => as(user).post('/api/watchlist/add', movieId === undefined ? {} : { movieId });
const remove = (user, movieId) => as(user).post('/api/watchlist/remove', movieId === undefined ? {} : { movieId });
const titles = async (user) => {
  const res = await as(user).get('/api/watchlist/');
  expect(res.status).toBe(200);
  return res.body.map((m) => m.title);
};

module.exports = { setupDatabase, ctx, at, as, add, remove, titles, M, Watchlist };
