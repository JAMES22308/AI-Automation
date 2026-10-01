const mysql = require("mysql2");

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "",
    database: "ai_tasks"
});

db.connect((error) => {
    if (error) {
        console.error("Database connection failed:", error);
        return;
    }

    console.log("MySQL connected!");
});

module.exports = db;