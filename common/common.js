const db = require("../models");
const _ = require("lodash");
const { v4: uuidv4 } = require("uuid");

async function writeLog(hostname, url, caller, party, type, body, header, mode) {
  return new Promise(async (resolve, reject) => {
    let ref = uuidv4();
    try {
      routelog
        .create({
          logrefnm: ref,
          // logapidm: hostname,
          logapinm: url,
          logerrcd: "",
          logerrds: "",
          logheadr: JSON.stringify(header),
          logincom: type == "T" ? JSON.stringify(body) : "",
          logoutgg: type == "T" ? "" : JSON.stringify(body),
          logcallr: caller && !_.isEmpty(caller) ? caller : "",
          logparty: party,
          logctype: type,
          logamode: mode ? mode : "GET",
          logatype: "OUTGOING"
        })
        .then(() => {
          return resolve(ref);
        })
        .catch(async (err) => {
          console.log("Write Log Error", err);
          logging("ERR", err);
          return reject(err);
        });
    } catch (err) {
      return reject(err);
    }
  });
}

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

module.exports = {
formatDate,
formatDateTime,
formatDecimal,
  writeLog,
}
