const { Sequelize } = require("sequelize");

// Initialize Sequelize
const sequelize = new Sequelize('persis', 'root', null, {
    host: "127.0.0.1",
    dialect: "mysql",
    logging: true,
});

// Define models
const db = {};
db.Sequelize = Sequelize;
db.sequelize = sequelize;

db.user = require("./user.js")(sequelize, Sequelize);

// Sync models (optional, remove `force: true` in production)
sequelize.sync()
    .then(() => console.log("Database synced successfully"))
    .catch((err) => console.error("Error syncing database:", err));

module.exports = db;
