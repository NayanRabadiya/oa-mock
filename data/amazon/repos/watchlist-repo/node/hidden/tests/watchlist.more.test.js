// More acceptance tests (hidden in the test: they run when you submit).
const { setupDatabase, ctx, at, as, add, remove, titles, M, Watchlist } = require('./helpers');

setupDatabase();

describe('MoreWatchlistTests', () => {
  test('add validation errors', async () => {
    for (const [body, code, message] of [[{}, 400, 'Movie ID is required'], [{ movieId: '123' }, 400, 'Invalid movie ID format'],
      [{ movieId: M(999) }, 404, 'Movie not found']]) {
      const res = await as(ctx.sam).post('/api/watchlist/add', body);
      expect([res.status, res.body]).toEqual([code, { message }]);
    }
    expect(await Watchlist.countDocuments()).toBe(0);
  });

  test('remove and check validation errors', async () => {
    expect((await remove(ctx.sam)).body).toEqual({ message: 'Movie ID is required' });
    const bad = await remove(ctx.sam, 'not-an-id');
    expect([bad.status, bad.body]).toEqual([400, { message: 'Invalid movie ID format' }]);
    const check = await as(ctx.sam).get('/api/watchlist/check/xyz');
    expect([check.status, check.body]).toEqual([400, { message: 'Invalid movie ID format' }]);
  });

  test('every route needs a token', async () => {
    for (const res of [await as(null).get('/api/watchlist/'), await as(null).get('/api/watchlist/check/' + M(1)),
      await add(null, M(1)), await remove(null, M(1))]) {
      expect([res.status, res.body]).toEqual([401, { message: 'Unauthorized' }]);
    }
  });

  test('watchlists are per user', async () => {
    await add(ctx.sam, M(1)); await add(ctx.sam, M(3)); await add(ctx.alex, M(4));
    expect(await titles(ctx.sam)).toEqual(['The Shawshank Redemption', 'The Dark Knight']);
    expect(await titles(ctx.alex)).toEqual(['Spirited Away']);
    expect((await remove(ctx.alex, M(1))).status).toBe(404);       // alex can't remove sam's movie
    expect((await as(ctx.alex).get('/api/watchlist/check/' + M(1))).body.isInWatchlist).toBe(false);
  });

  test('add remove and add again', async () => {
    expect((await add(ctx.sam, M(5))).status).toBe(201);
    expect((await remove(ctx.sam, M(5))).status).toBe(200);
    expect(await titles(ctx.sam)).toEqual([]);
    expect((await add(ctx.sam, M(5))).status).toBe(201);
    expect((await add(ctx.sam, M(2))).status).toBe(201);
    expect(await titles(ctx.sam)).toEqual(['Parasite', 'Interstellar']);
  });

  test('failed requests count toward the limit', async () => {
    for (let i = 0; i < 10; i++) {
      at(i);
      expect((await add(ctx.sam, 'bad' + i)).status).toBe(400);
    }
    at(10);
    expect((await add(ctx.sam, M(2))).status).toBe(429);
    expect(await titles(ctx.sam)).toEqual([]);
  });

  test('rejected requests do not count', async () => {
    for (let i = 0; i < 10; i++) {
      at(i);
      if (i % 2 === 0) await add(ctx.sam, M(1)); else await remove(ctx.sam, M(1));
    }
    for (const t of [30, 60, 90, 119]) {
      at(t);
      expect((await add(ctx.sam, M(2))).status).toBe(429);
    }
    at(120);
    expect((await add(ctx.sam, M(2))).status).toBe(201);    // 429 responses must not extend the window
  });

  test('reads are not rate limited', async () => {
    for (let i = 0; i < 10; i++) {
      at(i);
      if (i % 2 === 0) await add(ctx.sam, M(1)); else await remove(ctx.sam, M(1));
    }
    at(11);
    for (let i = 0; i < 15; i++) {
      expect((await as(ctx.sam).get('/api/watchlist/')).status).toBe(200);
      expect((await as(ctx.sam).get('/api/watchlist/check/' + M(1))).status).toBe(200);
    }
  });
});
