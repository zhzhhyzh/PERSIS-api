// User Profile

module.exports = (sequelize, Sequelize) => {
    const user = sequelize.define("user", {
        userId: {
            type: Sequelize.STRING(10),
            allowNull: false
        },
        userName: {
            type: Sequelize.STRING(255),
            allowNull: false,
        },
        // pType1: {
        //     type: Sequelize.STRING(255),
        //     allowNull: false
        //     // Preferencce type 1
        // },
        // pType2: {
        //     type: Sequelize.STRING(255),
        //     allowNull: false
        //     // Preference type 2
        // },
        recordPath: {
            type: Sequelize.STRING(255),
            allowNull: false
            // userId.csv
        }
    }, { freezeTableName: true },
        {
            indexes: [
                {
                    unique: true,
                    fields: ['userId']
                }
            ]
        });

    return user;
};