const fs = require('fs');
const path = require('path');
const csv = require('csv-parser');

// Get user statistics for dashboard
const getUserStats = async (req, res) => {
    try {
        const username = req.body.username || req.query.username;
        
        if (!username) {
            return res.status(400).json({
                status: 'error',
                message: 'Username is required'
            });
        }

        const filePath = path.join(__dirname, '..', 'documents', 'userPath', `${username}-user.csv`);
        
        // Check if user data file exists
        if (!fs.existsSync(filePath)) {
            return res.json({
                status: 'success',
                data: {
                    totalQuestions: 0,
                    totalAnswered: 0,
                    persuasiveTypeStats: {
                        reward: { total: 0, positive: 0, percentage: 0 },
                        reminder: { total: 0, positive: 0, percentage: 0 },
                        suggestion: { total: 0, positive: 0, percentage: 0 },
                        praise: { total: 0, positive: 0, percentage: 0 }
                    }
                }
            });
        }

        // Read and parse the CSV file
        const userResponses = [];
        
        return new Promise((resolve, reject) => {
            fs.createReadStream(filePath)
                .pipe(csv())
                .on('data', (row) => {
                    userResponses.push(row);
                })
                .on('end', () => {
                    // Calculate statistics
                    const stats = calculateStats(userResponses);
                    
                    res.json({
                        status: 'success',
                        data: stats
                    });
                    resolve();
                })
                .on('error', (error) => {
                    console.error('Error reading CSV:', error);
                    res.status(500).json({
                        status: 'error',
                        message: 'Error reading user data'
                    });
                    reject(error);
                });
        });

    } catch (error) {
        console.error('Error in getUserStats:', error);
        res.status(500).json({
            status: 'error',
            message: 'Internal server error'
        });
    }
};

function calculateStats(userResponses) {
    const stats = {
        totalQuestions: userResponses.length,
        totalAnswered: 0,
        persuasiveTypeStats: {
            reward: { total: 0, positive: 0, percentage: 0 },
            reminder: { total: 0, positive: 0, percentage: 0 },
            suggestion: { total: 0, positive: 0, percentage: 0 },
            praise: { total: 0, positive: 0, percentage: 0 }
        }
    };

    userResponses.forEach(response => {
        const persuasiveType = response.persuasive_type?.toLowerCase();
        const answer = response.yesOrNo?.toUpperCase();
        
        // Skip if no persuasive type or if question not answered
        if (!persuasiveType || !answer || answer === '') {
            return;
        }

        stats.totalAnswered++;

        // Initialize if persuasive type not in stats
        if (!stats.persuasiveTypeStats[persuasiveType]) {
            stats.persuasiveTypeStats[persuasiveType] = { total: 0, positive: 0, percentage: 0 };
        }

        // Count total for this persuasive type
        stats.persuasiveTypeStats[persuasiveType].total++;

        // Count positive responses (Y = Yes)
        if (answer === 'Y') {
            stats.persuasiveTypeStats[persuasiveType].positive++;
        }
    });

    // Calculate percentages
    Object.keys(stats.persuasiveTypeStats).forEach(type => {
        const typeStats = stats.persuasiveTypeStats[type];
        if (typeStats.total > 0) {
            typeStats.percentage = Math.round((typeStats.positive / typeStats.total) * 100);
        }
    });

    return stats;
}

module.exports = {
    getUserStats
};
