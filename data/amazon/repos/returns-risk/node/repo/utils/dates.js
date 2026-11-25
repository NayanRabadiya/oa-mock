// Dates are calendar days in UTC, written "YYYY-MM-DD".
const DAY_MS = 24 * 60 * 60 * 1000;

const isIsoDate = (value) => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(Date.parse(value));

const toUtcDay = (value) => {
  const [y, m, d] = String(value).slice(0, 10).split('-').map(Number);
  return Date.UTC(y, m - 1, d);
};

// Whole days from `from` to `to` (negative when `to` is earlier).
const daysBetween = (from, to) => Math.round((toUtcDay(to) - toUtcDay(from)) / DAY_MS);

const today = () => new Date().toISOString().slice(0, 10);

module.exports = { isIsoDate, daysBetween, today };
