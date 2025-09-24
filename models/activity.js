// Activity

module.exports = (sequelize, Sequelize) => {
    const activity = sequelize.define("activity", {
        uuid: {
            type: Sequelize.STRING(36),
            allowNull: false
            //Username
        },
        aType: {
            type: Sequelize.STRING(10),
            allowNull: false,
            //Response Type
        },
        username: {
            type: Sequelize.STRING(255),
            allowNull: false
            //Link to user file
        },
        rDate: {
            type: Sequelize.DATE,
            allowNull: false,
            defaultValue: new Date(),
            // Response made date
        },
        distance: {
            type: Sequelize.DECIMAL(10, 2),
            allowNull: false
            // Distance in KM 
        },
        duration_sec: {
            type: Sequelize.INTEGER,
            defaultValue: 0,
            // validate: {
            //     min: 0,
            //     max: 59
            // }
            //-838:59:59 to 838:59:59
        },

        duration_min: {
            type: Sequelize.INTEGER,
            defaultValue: 0,
            // validate: {
            //     min: 0,
            //     max: 59
            // }
            //-838:59:59 to 838:59:59
        },
        duration_hour: {
            type: Sequelize.INTEGER,
            defaultValue: 0,
            // validate: {
            //     min: 0,
            //     max: 838
            // }
            //-838:59:59 to 838:59:59
        },
        openq1: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq2: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq3: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq4: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq5: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq6: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq7: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },
        openq8: {
            type: Sequelize.STRING(255),
            default: "",
            //Any open question
        },

    }, { freezeTableName: true },
        {
            indexes: [
                {
                    unique: true,
                    fields: ['uuid']
                }
            ]
        });

    return activity;
};