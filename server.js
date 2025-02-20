const express = require("express");
const { spawn } = require("child_process");
const db = require("./models")
const _ = require('lodash')
const app = express();
app.use(express.json());

//controller execution
const user = db.user;
async function runPythonProcess(data, res) {
    try {
        // Await the promise for userFind
        const userFind = await user.findOne({
            where: {
                userId: data.userId
            }, 
            raw: true, 
            attributes: ['pType1', 'pType2']
        });

        // Handle user not found scenario
        if (!userFind || _.isEmpty(userFind.pType1) || _.isEmpty(userFind.pType2)) {
            if (data.invoke_type === 1) {
                const preferenceUpdate = {
                    pType1: data.answer[0],
                    pType2: data.answer[1]
                };

                // Update user preferences
                await user.update(preferenceUpdate, {
                    where: {
                        userId: data.userId
                    },
                    returning: true,
                    plain: true
                });
            } else {
                return res.status(404).json({ response_type: 3, response: "usernotfound" });
            }
        } else {
            data.pType1 = userFind.pType1;
            data.pType2 = userFind.pType2;

            const pythonProcess = spawn("python", ["reinforcement.py"]);

            pythonProcess.stdin.write(JSON.stringify(data));
            pythonProcess.stdin.end();

            let responseData = "";

            pythonProcess.stdout.on("data", (chunk) => {
                responseData += chunk.toString(); // Collect data
            });

            pythonProcess.stderr.on("data", (data) => {
                console.error("Python Error:", data.toString());
            });

            pythonProcess.on("close", (code) => {
                if (!responseData.trim()) {
                    console.error("No response received from Python script.");
                    return res.status(500).json({ response_type: 3, response: "UnexpectedError" });
                }

                try {
                    const jsonResponse = JSON.parse(responseData.trim()); // Ensure complete JSON
                    return res.json(jsonResponse);
                } catch (error) {
                    console.error("JSON Parsing Error:", error);
                    return res.status(500).json({ response_type: 3, response: "UnexpectedError" });
                }
            });
        }

    } catch (error) {
        console.error("Error in processing:", error);
        return res.status(500).json({ response_type: 3, response: "UnexpectedError" });
    }
}


app.post("/invoke", (req, res) => {
    runPythonProcess(req.body, res);
});



app.use(function (req, res, next) {
    res.status(404).send("APINOTFOUND, This is an default API");
});



console.log("Server started=====>");
// app.listen(3000, () => {
//     console.log("Server running on port 3000");
// });
db.sequelize.sync() // Ensure database sync
    .then(() => {
        console.log("Database synced successfully");
        app.listen(3000, () => {
            console.log("Server running on http://localhost:3000/");
        });
    })
    .catch((err) => {
        console.error("Error syncing database:", err);
    });
