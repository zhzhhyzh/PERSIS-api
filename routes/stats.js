const express = require('express');
const router = express.Router();

// -- Load Common Authentication -- //
const authenticateRoute = require('../common/authenticate');
// -- Load Controller -- // 
const stats = require("../controllers/stats-controller");

// @route   POST api/stats/getUserStats
// @desc    Get user statistics for dashboard
// @access  Private
router.post('/getUserStats', authenticateRoute, stats.getUserStats);

// @route   GET api/stats/getUserStats
// @desc    Get user statistics for dashboard (GET version)
// @access  Private
router.get('/getUserStats', authenticateRoute, stats.getUserStats);

module.exports = router;
