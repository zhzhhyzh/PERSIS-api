const express = require("express");
const { spawn } = require("child_process");

const app = express();
app.use(express.json());

function runPythonProcess(data, res) {
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
            return res.status(500).json({ error: "Empty response from Python script" });
        }

        try {
            const jsonResponse = JSON.parse(responseData.trim()); // Ensure complete JSON
            res.json(jsonResponse);
        } catch (error) {
            console.error("JSON Parsing Error:", error);
            res.status(500).json({ error: "Invalid JSON response from Python script" });
        }
    });
   
}

app.post("/invoke", (req, res) => {
    runPythonProcess(req.body, res);
});

app.listen(3000, () => {
    console.log("Server running on port 3000");
});
