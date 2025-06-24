// Import
const db = require("../models");
const fs = require("fs");

//Table import
const usrlgnpf = db.usrlgnpf;
const user = db.user;


//Common Function
const Op = db.Sequelize.Op;
const returnError = require('../common/error');
const returnSuccess = require('../common/success');
const returnSuccessMessage = require('../common/successMessage');

exports.download = async (req, res) => {
   try{
     let username = req.query.username ? req.query.username : '';
    if (!username || username == '') return returnError(req, 500, "RECORDIDISREQUIRED", res);


    let path = './documents/userPath/';
    let file = `${path}${username}-user.csv`;
    res.setHeader('Content-type', 'text/csv');
    res.download(file, username);


   }catch(err){
    console.log(err);
    return returnError(req,500, "UNEXPECTEDERROR", res);
   }

}

const path = require('path');
const archiver = require('archiver');

exports.downloadZip = async (req, res) => {
  try {
    // const username = req.query.username || '';
    // if (!username) return returnError(req, 500, "RECORDIDISREQUIRED", res);

    const folderPath = `./documents/userPath/`;
    const archiveName = `files.zip`;

    // Check if folder exists
    if (!fs.existsSync(folderPath)) {
      return returnError(req, 404, "DIRECTORYNOTFOUND", res);
    }

    res.setHeader('Content-Disposition', `attachment; filename=${archiveName}`);
    res.setHeader('Content-Type', 'application/zip');

    const archive = archiver('zip', {
      zlib: { level: 9 } // Best compression
    });

    archive.on('error', (err) => {
      throw err;
    });

    // Pipe the archive data to the response
    archive.pipe(res);

    // Append all files in the directory
    archive.directory(folderPath, false); // false = no subfolder in zip

    // Finalize archive
    archive.finalize();
  } catch (err) {
    console.error(err);
    return returnError(req, 500, "UNEXPECTEDERROR", res);
  }
};