// The acceptance tests for the watchlist feature. Run them with:  npm test
const { setupDatabase, ctx, at, as, add, remove, M, Watchlist } = require('./helpers');

setupDatabase();

const LIMIT = { message: 'Too many watchlist operations. You can add or remove movies up to 10 times within 2 minutes.' };

describe('WatchlistTests', () => {
  test('get watchlist returns movies in order added', async () => {
    await Watchlist.create({ user: ctx.sam._id, movie: M(3) });
    await Watchlist.create({ user: ctx.sam._id, movie: M(1) });
    await Watchlist.create({ user: ctx.alex._id, movie: M(2) });
    const res = await as(ctx.sam).get('/api/watchlist/');
    expect(res.status).toBe(200);
    expect(res.body.map((m) => m.title)).toEqual(['The Dark Knight', 'The Shawshank Redemption']);
    expect(res.body[0]).toHaveProperty('_id', M(3));        // each item is a movie document
    expect(res.body[0]).toHaveProperty('year');
  });

  test('add movie creates entry and rejects duplicates', async () => {
    const first = await add(ctx.sam, M(2));
    expect(first.status).toBe(201);
    expect(first.body).toEqual({ message: 'Movie added to watchlist successfully' });
    expect(await Watchlist.exists({ user: ctx.sam._id, movie: M(2) })).toBeTruthy();   // the entry must be saved
    const again = await add(ctx.sam, M(2));
    expect(again.status).toBe(400);
    expect(again.body).toEqual({ message: 'Movie already in watchlist' });
    expect(await Watchlist.countDocuments({ user: ctx.sam._id })).toBe(1);
  });

  test('remove movie deletes entry and 404 when missing', async () => {
    await Watchlist.create({ user: ctx.sam._id, movie: M(4) });
    const removed = await remove(ctx.sam, M(4));
    expect(removed.status).toBe(200);
    expect(removed.body).toEqual({ message: 'Movie removed from watchlist successfully' });
    expect(await Watchlist.exists({ user: ctx.sam._id, movie: M(4) })).toBeFalsy();    // the entry must be deleted
    const missing = await remove(ctx.sam, M(4));
    expect(missing.status).toBe(404);
    expect(missing.body).toEqual({ message: 'Movie not found in watchlist' });
  });

  test('check status returns boolean', async () => {
    const before = await as(ctx.sam).get('/api/watchlist/check/' + M(5));
    expect(before.status).toBe(200);
    expect(before.body.isInWatchlist).toBe(false);
    await Watchlist.create({ user: ctx.sam._id, movie: M(5) });
    const after = await as(ctx.sam).get('/api/watchlist/check/' + M(5));
    expect(after.body.isInWatchlist).toBe(true);
  });

  test('rate limit blocks eleventh operation combined', async () => {
    for (let i = 0; i < 5; i++) {
      at(i * 2);
      expect((await add(ctx.sam, M(i + 1))).status).toBe(201);
      at(i * 2 + 1);
      expect((await remove(ctx.sam, M(i + 1))).status).toBe(200);
    }
    at(11);
    const blocked = await add(ctx.sam, M(6));
    expect(blocked.status).toBe(429);       // adds and removes share one limit of 10 per 2 minutes
    expect(blocked.body).toEqual(LIMIT);
    expect((await add(ctx.alex, M(6))).status).toBe(201);    // the limit is per user
  });

  test('rate limit window slides after two minutes', async () => {
    for (let i = 0; i < 10; i++) {
      at(i);
      if (i % 2 === 0) await add(ctx.sam, M(1)); else await remove(ctx.sam, M(1));
    }
    at(60);
    expect((await add(ctx.sam, M(2))).status).toBe(429);
    at(120);
    expect((await add(ctx.sam, M(2))).status).toBe(201);    // the request made at 0 s stops counting at 120 s
    expect((await add(ctx.sam, M(3))).status).toBe(429);    // at 120 s the window holds 10 again
    at(121);
    expect((await add(ctx.sam, M(3))).status).toBe(201);
  });
});
