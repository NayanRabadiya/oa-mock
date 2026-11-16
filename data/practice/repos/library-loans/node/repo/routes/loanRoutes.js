const express = require('express');
const { listBooks, borrowBook, returnBook } = require('../controllers/loanController');

const router = express.Router();

router.get('/books', listBooks);
router.post('/loans', borrowBook);
router.post('/loans/:loanId/return', returnBook);

module.exports = router;
