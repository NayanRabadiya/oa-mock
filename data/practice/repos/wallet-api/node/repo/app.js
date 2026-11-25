const express = require('express');
const walletRoutes = require('./routes/walletRoutes');

const app = express();

app.use(express.json());
app.use('/api', walletRoutes);
app.use((req, res) => res.status(404).json({ message: 'Not found' }));

module.exports = app;
