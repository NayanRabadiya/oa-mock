const express = require('express');
const loanRoutes = require('./routes/loanRoutes');

const app = express();

app.use(express.json());
app.use('/api', loanRoutes);
app.use((req, res) => res.status(404).json({ message: 'Not found' }));

module.exports = app;
