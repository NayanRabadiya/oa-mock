const app = require('./app');
const store = require('./data/store');

const PORT = process.env.PORT || 5000;

store.reset(require('./data/seed.json'));
app.listen(PORT, () => console.log(`Return/risk service running on port ${PORT}`));
