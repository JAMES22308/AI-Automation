const express = require("express");
const cors = require("cors");
const db = require("./database");

const app = express();

app.use(cors());
app.use(express.json());

app.get("/", (req, res) => {
    res.send("AI Task API is running");
});

app.get("/api/message", (req, res) => {
    res.json({
        message: "Hello from Node.js!"
    });
});

app.get("/api/tasks", (req, res) => {
    const sql = "SELECT * FROM tasks";

    db.query(sql, (error, results) => {
        if (error) {
            console.error(error);
            return res.status(500).json({
                error: "Database query failed"
            });
        }

        res.json(results);
    });
});


app.post("/api/tasks", (req, res) => {
    const { task_text } = req.body;

    const sql = "INSERT INTO tasks (task_text) VALUES (?)";

    db.query(sql, [task_text], (error, result) => {
        if (error) {
            console.error(error);
            return res.status(500).json({
                error: "Failed to add task"
            });
        }

        res.json({
            message: "Task added successfully",
            id: result.insertId
        });
    });
});

app.post("/api/analyse", async (req, res) => {
    try {
        const response = await fetch("http://127.0.0.1:8000/analyse", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                task_text: req.body.task_text
            })
        });

        const data = await response.json();

        res.json(data);
    } catch (error) {
        console.error(error);

        res.status(500).json({
            error: "Python service unavailable"
        });
    }
});

app.listen(3000, () => {
    console.log("Server running on http://localhost:3000");
});