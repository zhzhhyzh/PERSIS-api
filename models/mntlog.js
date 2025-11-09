// User logs

module.exports = (sequelize, Sequelize) => {
    const mntlog = sequelize.define("mntlog", {
        username: {
            type: Sequelize.STRING(255),
            allowNull: false
            //Username
        },

        actDate: {
            type: Sequelize.DATE,
            allowNull: false,
            default: new Date(),
        },
        description: {
            type: Sequelize.STRING(255),
            allowNull: false
        }
    }, { freezeTableName: true },
        {
            indexes: [
                {
                    unique: true,
                    fields: ['actDate']
                }
            ]
        });

    return mntlog;
};