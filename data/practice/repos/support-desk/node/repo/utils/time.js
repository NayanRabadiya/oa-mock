// Times are ISO 8601 strings in UTC, like 2026-11-15T09:30:00Z.
const ISO_TIME = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?Z$/;

const isIsoTime = (value) => typeof value === 'string' && ISO_TIME.test(value) && !Number.isNaN(Date.parse(value));

const now = () => new Date().toISOString().replace(/\.\d+Z$/, 'Z');

const MS_PER_HOUR = 1000 * 60 * 60;

module.exports = { isIsoTime, now, MS_PER_HOUR };
