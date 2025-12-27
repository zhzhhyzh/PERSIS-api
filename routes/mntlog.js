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

// @route   POST api/mntlog/create
// @desc    Create Log
// @access  Private
router.post("/create", authenticateRoute, mntlog.create);

// @route   GET api/mntlog/files
// @desc    List Log Files
// @access  Public
router.get("/files", mntlog.getFiles);

// @route   GET api/mntlog/download/:filename
// @desc    Download Log File
// @access  Public
router.get("/download/:filename", mntlog.download);


module.exports = router;