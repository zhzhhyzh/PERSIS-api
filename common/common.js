const db = require("../models");
const _ = require("lodash");
const { v4: uuidv4 } = require("uuid");
const moment = require("moment");
const fs = require('fs');
const path = require('path');


const mntlog = db.mntlog;

async function formatDate(value, separator) {
  return new Promise((resolve, reject) => {
    try {
      let date = new Date(value);
      if (date && !isNaN(date.getTime()))
        return resolve(
          _.padStart(
            _.padStart(date.getDate(), 2, "0") +
            separator +
            _.padStart(date.getMonth() + 1, 2, "0") +
            separator +
            date.getFullYear(),
            2,
            "0"
          )
        );
      else return resolve("");
    } catch (err) {
      return resolve(value);
    }
  });
}

async function formatDateTime(value, type, dateformat) {
  return new Promise((resolve, reject) => {
    try {
      let date = new Date(value);
      if (date && !isNaN(date.getTime())) {
        let format = "DD-MM-YYYY ";
        if (type == "12") format += "hh";
        else format += "HH";
        format += ":mm:ss A";

        if (dateformat && dateformat !== "") {
          format = dateformat;
        }
        return resolve(moment(value).format(format));
      } else return resolve("");
    } catch (err) {
      return resolve(value);
    }
  });
}

async function formatDecimal(value) {
  return new Promise(async (resolve, reject) => {
    try {
      value = value.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
      return resolve(value);
    } catch (err) {
      return reject(err);
    }
  });
}

async function writeLog(username, description) {
  try {
    const now = new Date();
    const localISOTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString();

    await mntlog.create({
      actDate: localISOTime,
      username,
      description
    });

    // Auto store log to CSV
    const logDir = path.join(__dirname, '../documents/mntlogs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }

    const csvFile = path.join(logDir, `${username}.csv`);
    const csvLine = `"${localISOTime}","${username}","${description}"\n`;

    if (!fs.existsSync(csvFile)) {
        fs.writeFileSync(csvFile, 'actDate,username,description\n');
    }
    fs.appendFileSync(csvFile, csvLine);

  } catch (e) {
    console.error(e);
    console.log("username:", username);
    console.log("description:", description);
  }
}

module.exports = {
  formatDate,
  formatDateTime,
  formatDecimal,
  writeLog,
}
