'use strict';

const fs = require('fs');
const path = require('path');
const Sequelize = require('sequelize');
const dotenv = require("dotenv");
dotenv.config();
const basename = path.basename(__filename);
const env = process.env.NODE_ENV || 'local';
const config = require(__dirname + '/../config/config.json')[env];
const db = {};

let sequelize;
config.freezeTableName = true;
config.logging = true;
sequelize = new Sequelize(config.database, config.username, config.password, { logging: config.logging, host: config.host, dialect: config.dialect });

fs
  .readdirSync(__dirname)
  .filter(file => {
    return (file.indexOf('.') !== 0) && (file !== basename) && (file.slice(-3) === '.js');
  })
  .forEach(file => {
    const model = require(path.join(__dirname, file))(sequelize, Sequelize.DataTypes);
    db[model.name] = model;
  });

Object.keys(db).forEach(modelName => {
  if (db[modelName].associate) {
    db[modelName].associate(db);
  }
});

db.sequelize = sequelize;
db.Sequelize = Sequelize;

module.exports = db;
