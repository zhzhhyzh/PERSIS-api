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
module.exports = {

  writeLog,
}
