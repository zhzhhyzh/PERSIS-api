// Import
const db = require("../models");
const _ = require("lodash");
const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

//Table
const mntlog = db.mntlog;


// Common Function
const Op = db.Sequelize.Op;
const returnError = require("../common/error");
const returnSuccess = require("../common/success");
const returnSuccessMessage = require("../common/successMessage");
const common = require("../common/common");
const connection = require("../common/db");


exports.list = async (req, res) => {
    let user = req.user.username;
    // default 10 records per page
    let limit = 10;
    if (req.query.limit) limit = parseInt(req.query.limit);

    // page offset
    let from = 0;
    if (!req.query.page) from = 0;
    else from = parseInt(req.query.page) * limit;

    // filters (where clause)
    let option = {};

    option.username = user;


    if (req.query.from && !_.isEmpty("" + req.query.from)) {
        let fromDate = new Date(req.query.from);
        fromDate.setHours(0, 0, 0, 0);
        if (!_.isNaN(fromDate.getTime())) {
            if (req.query.to && !_.isEmpty("" + req.query.to)) {
                let toDate = new Date(req.query.to);
                toDate.setHours(23, 59, 59, 999);
                if (!_.isNaN(toDate.getTime())) {
                    option.rDate = {
                        [Op.and]: [{ [Op.gte]: fromDate }, { [Op.lte]: toDate }],
                    };
                } else {
                    option.rDate = {
                        [Op.gte]: fromDate,
                    };
                }
            } else {
                option.rDate = {
                    [Op.gte]: fromDate,
                };
            }
        }
    } else if (req.query.to && !_.isEmpty("" + req.query.to)) {
        let toDate = new Date(req.query.to);
        toDate.setHours(23, 59, 59, 999);
        if (!_.isNaN(toDate.getTime())) {
            option.rDate = {
                [Op.lte]: toDate,
            };
        }
    }

    const { count, rows } = await mntlog.findAndCountAll({
        limit: parseInt(limit),
        offset: from,
        where: option,
        raw: true,
        attributes: [
            ["actDate", "id"],
            "actDate",
            "username",
            "description",

        ],
        order: [["actDate", "desc"]],
    });

    let newRows = [];
    for (var i = 0; i < rows.length; i++) {
        let obj = rows[i];

        obj.actDate = await common.formatDateTime(obj.actDate, "12","DD-MM-YYYY HH:mm:ss A");

        newRows.push(obj);
    }

    if (count > 0) {
        return returnSuccess(
            200,
            {
                total: count,
                data: newRows,
                extra: { file: "mntlog", key: ["actDate"] },
            },
            res
        );
    }
    else {

        return returnSuccess(200, { total: 0, data: [] }, res);
    }
};
