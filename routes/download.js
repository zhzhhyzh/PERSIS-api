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

// @route   GET api/download/listLogs
// @desc    List log files
// @access  Public
router.get('/listLogs', download.listLogs);

// @route   GET api/download/downloadLog
// @desc    Download log file
// @access  Public
router.get('/downloadLog', download.downloadLog);

// @route   GET api/download/listMntLogs
// @desc    List mntlog files
// @access  Public
router.get('/listMntLogs', download.listMntLogs);

// @route   GET api/download/downloadMntLog
// @desc    Download mntlog file
// @access  Public
router.get('/downloadMntLog', download.downloadMntLog);


module.exports = router;


module.exports = router;