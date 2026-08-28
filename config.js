// Set this to the deployed Python API origin, without a trailing slash.
// Local server leaves it blank and serves /api from the same origin.
window.MARKET_NOTE_API_BASE = window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost'
  ? ''
  : 'https://market-note-api.onrender.com';
