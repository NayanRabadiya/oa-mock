// ---- file: framework (read-only) ----------------------------------------
// Small stand-ins for express and mongoose so the repo runs in the browser.
// import/export lines are removed; every file shares one scope.
const __out = [];
const __log = (...a) => __out.push("[log] " + a.map(x => x instanceof Error ? (x.name + ": " + x.message) : typeof x === "string" ? x : JSON.stringify(x)).join(" "));
console = Object.assign({}, console, {log: __log, info: __log, warn: __log, error: __log});

const mongoose = { Types: { ObjectId: { isValid: id => typeof id === "string" && /^[0-9a-f]{24}$/i.test(id) } } };

const express = {
  Router() {
    const r = { stack: [] };
    r.use = fn => { r.stack.push({ all: true, h: [fn] }); return r; };
    for (const m of ["get", "post", "put", "delete"]) r[m] = (path, ...h) => { r.stack.push({ method: m.toUpperCase(), path, h }); return r; };
    return r;
  }
};

// ---- file: models/Movie.js (read-only) ----------------------------------
const MOVIES = [
  { _id: "65f0a1b2c3d4e5f600000001", title: "The Shawshank Redemption", year: 1994, rating: 9.3, genre: ["Drama", "Crime"] },
  { _id: "65f0a1b2c3d4e5f600000002", title: "Interstellar", year: 2014, rating: 8.7, genre: ["Sci-Fi", "Drama"] },
  { _id: "65f0a1b2c3d4e5f600000003", title: "The Dark Knight", year: 2008, rating: 9.0, genre: ["Action", "Crime"] },
  { _id: "65f0a1b2c3d4e5f600000004", title: "Spirited Away", year: 2001, rating: 8.6, genre: ["Animation", "Fantasy"] },
  { _id: "65f0a1b2c3d4e5f600000005", title: "Parasite", year: 2019, rating: 8.5, genre: ["Thriller", "Drama"] },
  { _id: "65f0a1b2c3d4e5f600000006", title: "Inception", year: 2010, rating: 8.8, genre: ["Sci-Fi", "Action"] }
];
const Movie = {
  async findById(id) { const m = MOVIES.find(x => x._id === String(id)); return m ? { ...m } : null; },
  async find() { return MOVIES.map(m => ({ ...m })); }
};

// ---- file: models/Watchlist.js (read-only) ------------------------------
// Schema: { user: ObjectId, movie: ObjectId -> Movie }, unique index on (user, movie).
// Supported: create, find(filter) [+ .populate("movie")], findOne(filter), findOneAndDelete(filter), deleteOne(filter)
const __rows = []; let __seq = 0;
const __match = (row, f) => Object.keys(f || {}).every(k => String(row[k]) === String(f[k]));
const __copy = r => ({ ...r });
const Watchlist = {
  async create(doc) {
    if (__rows.some(r => r.user === String(doc.user) && r.movie === String(doc.movie))) {
      const e = new Error("E11000 duplicate key error collection: watchlists index: user_1_movie_1"); e.code = 11000; throw e;
    }
    const row = { _id: "77aa00000000000000" + String(++__seq).padStart(6, "0"), user: String(doc.user), movie: String(doc.movie), createdAt: new Date(Date.now()).toISOString() };
    __rows.push(row); return __copy(row);
  },
  find(filter) {
    let pop = false;
    const q = {
      populate(field) { if (field === "movie") pop = true; return q; },
      then(ok, bad) {
        return (async () => {
          const rows = __rows.filter(r => __match(r, filter)).map(__copy);
          if (pop) for (const r of rows) r.movie = await Movie.findById(r.movie);
          return rows;
        })().then(ok, bad);
      }
    };
    return q;
  },
  async findOne(filter) { const r = __rows.find(x => __match(x, filter)); return r ? __copy(r) : null; },
  async findOneAndDelete(filter) { const i = __rows.findIndex(x => __match(x, filter)); return i < 0 ? null : __copy(__rows.splice(i, 1)[0]); },
  async deleteOne(filter) { const i = __rows.findIndex(x => __match(x, filter)); if (i >= 0) __rows.splice(i, 1); return { deletedCount: i < 0 ? 0 : 1 }; }
};

// ---- file: middleware/auth.js (read-only) -------------------------------
const USERS = { "token-sam": "64aa0000000000000000a001", "token-alex": "64aa0000000000000000a002" };
const authMiddleware = (req, res, next) => {
  const h = req.headers.authorization || "";
  const userId = USERS[h.replace(/^Bearer /, "")];
  if (!userId) return res.status(401).json({ message: "No token, authorization denied" });
  req.userId = userId;
  next();
};

// ======================= files you can edit start here =====================
