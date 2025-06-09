// User Profile

module.exports = (sequelize, Sequelize) => {
    const user = sequelize.define("user", {
        username: {
            type: Sequelize.STRING(255),
            allowNull: false
            //Username
        },
        name: {
            type: Sequelize.STRING(255),
            allowNull: false,
            //Real Name
        },
        password: {
            type: Sequelize.STRING(255),
            allowNull: false
        },
        age: {
            type: Sequelize.INTEGER,
            allowNull: false
        },
        gender: {
            type: Sequelize.STRING(1),
            allowNull: false
            //Only Allow M - Male, F - Female
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
                    fields: ['username']
                }
            ]
        });

    return user;
};