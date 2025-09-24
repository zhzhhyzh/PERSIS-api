const express = require('express');
const router = express.Router();

// -- Load Common Authentication -- //
const authenticateRoute = require('../common/authenticate');
// -- Load Controller -- //
const activity = require("../controllers/activity-controller");

// @route   GET api/activity/find-one
// @desc    Find OTP Parameter
// @access  Private
router.get("/detail", authenticateRoute, activity.findOne);



// @route   GET api/activity/find-one
// @desc    Find OTP Parameter
// @access  Private
router.get("/listMedal", authenticateRoute, activity.listMedal);


// @route   GET api/activity/list
// @desc    List OTP Parameter
// @access  Private
router.get("/list", authenticateRoute, activity.list);

// @route   POST api/activity/create
// @desc    Create OTP Parameter
// @access  Private
router.post("/create",authenticateRoute, activity.create);

// // @route   POST api/activity/delete
// // @desc    Delete OTP Parameter
// // @access  Private
// router.post("/delete", authenticateRoute, activity.delete);

// // @route   POST api/activity/update
// // @desc    Update OTP Parameter
// // @access  Private
// router.post("/update", authenticateRoute, activity.update);

// router.get("/detailMember", authenticateRoute, activity.findOneMember);
module.exports = router;