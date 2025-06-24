const express = require('express');
const router = express.Router();
const _ = require("lodash");

// -- Load Common Authentication -- //
const authenticateRoute = require('../common/authenticate');
// -- Load Controller -- //
const download = require("../controllers/download-controller");





// @route   POST api/download/download
// @desc    Run Python Process
// @access  Public
router.get('/download', authenticateRoute, download.download);


// @route   POST api/download/download
// @desc    Run Python Process
// @access  Public
router.get('/downloadZip', download.downloadZip);


module.exports = router;