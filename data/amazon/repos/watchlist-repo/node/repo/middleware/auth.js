const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'moviedb-local-development-secret';

// Reads `Authorization: Bearer <token>` and sets req.userId, or answers 401.
const authMiddleware = (req, res, next) => {
  const header = req.headers.authorization || '';
  const [scheme, token] = header.split(' ');
  if (scheme !== 'Bearer' || !token) {
    return res.status(401).json({ message: 'Unauthorized' });
  }
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.userId = payload.userId;
    next();
  } catch (err) {
    return res.status(401).json({ message: 'Unauthorized' });
  }
};

module.exports = { authMiddleware, JWT_SECRET };
