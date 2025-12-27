const express = require('express');
const router = express.Router();

// -- Load Common Authentication -- //
const authenticateRoute = require('../common/authenticate');
// -- Load Controller -- //
const mntlog = require("../controllers/mntlog-controller");


// @route   GET api/mntlog/list
// @desc    List OTP Parameter
// @access  Private
router.get("/list", authenticateRoute, mntlog.list);


module.exports = router;