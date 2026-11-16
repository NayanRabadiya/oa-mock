const express = require('express');
const returnRoutes = require('./routes/returnRoutes');

const app = express();

app.use(express.json());
app.use('/api/returns', returnRoutes);
app.use((req, res) => res.status(404).json({ message: 'Not found' }));

module.exports = app;
