const express = require('express');
const ticketRoutes = require('./routes/ticketRoutes');

const app = express();

app.use(express.json());
app.use('/api', ticketRoutes);
app.use((req, res) => res.status(404).json({ message: 'Not found' }));

module.exports = app;
