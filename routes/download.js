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
router.get('/download', download.download);

// @route   POST api/download/list
// @desc    Run Python Process
// @access  Public
router.get('/list', download.list);


// @route   POST api/download/download
// @desc    Run Python Process
// @access  Public
router.get('/downloadZip', download.downloadZip);


module.exports = router;