const express = require('express');
const router = express.Router();
const _ = require("lodash");

// -- Load Common Authentication -- //
const authenticateRoute = require('../common/authenticate');
// -- Load Controller -- //
const invoke = require("../controllers/question-only-controller");





// @route   POST api/invoke/runPythonProcess
// @desc    Run Python Process
// @access  Private
router.post('/runPythonProcess', authenticateRoute, invoke.runPythonProcess);


module.exports = router;