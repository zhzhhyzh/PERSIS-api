const passport = require('passport');
const successMessage = require('../constant/successMessage');

module.exports = function returnSuccessMessage(req, status, code, res, special = null) {
  const success = {};
  if (req.headers['locale'] !== '' && req.headers['locale'] !== undefined && req.headers['locale'] !== null) {
    var locale = req.headers['locale'].toLowerCase();
  } else {
    var locale = 'en';
  }
  if (locale == 'zh') {

    if (special !== '' && special !== undefined && special !== null) {
      message.amount = special;
    }

    success.result = 'success';
    success.message = message;
  } else {
    var message = successMessage[code]

    if (special !== '' && special !== undefined && special !== null) {
      message.amount = special;
    }

    success.result = 'success';
    success.message = message;
  }

  return res.status(status).json(success); // send the error response to client
};
