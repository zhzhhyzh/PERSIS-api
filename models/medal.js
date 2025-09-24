// medal

module.exports = (sequelize, Sequelize) => {
    const medal = sequelize.define("medal", {


        username: {
            type: Sequelize.STRING(255),
            allowNull: false
            //Link to user file
        },
        medal1: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Walk 2km
        },
        medal2: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Walk 5km
        },
        medal3: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Walk 10km
        },

        medal4: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Hiking
        },
        medal5: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Swimming 100m
        },
        medal6: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Swimming 200m
        },
        medal7: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Swimming 300m
        },
        medal8: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Climbing
        },
        medal9: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Dancing
        },
        medal10: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Cycling 10km
        },
        medal11: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Cycling 30km
        },
        medal12: {
            type: Sequelize.STRING(1),
            allowNull: false,
            default:"N"
            // Cycling 50km
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

    return medal;
};