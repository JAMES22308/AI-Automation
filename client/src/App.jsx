
import { useState } from "react";
import "./App.css";

function App() {
    const [task, setTask] = useState("");
    const [result, setResult] = useState(null);

    async function analyseTask() {
        try {
            console.log("clicked the analyse button");

            const response = await fetch(
                "https://ai-task-assistant-api.onrender.com/analyse",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        task_text: task
                    })
                }
            );

            const data = await response.json();

            setResult(data);
            console.log("done processing");

        } catch (error) {
            console.error("Error:", error);
        }
    }

    return (
        <div className="app">
            <div className="container">

                <div className="header">
                    <div className="logo">✦</div>
                    <h1>AI Task Assistant</h1>
                    <p>
                        Turn your tasks into clear priorities and actionable suggestions.
                    </p>
                </div>

                <div className="task-card">
                    <label htmlFor="task">What do you need to get done?</label>

                    <input
                        id="task"
                        type="text"
                        value={task}
                        onChange={(event) => setTask(event.target.value)}
                        placeholder="e.g. Finish my programming assignment tomorrow"
                    />

                    <button
                        onClick={analyseTask}
                        disabled={!task.trim()}
                    >
                        ✨ Analyse Task
                    </button>
                </div>

                {result && (
                    <div className="result-card">
                        <div className="result-header">
                            <h2>Analysis</h2>
                            <span className={`priority ${result.priority?.toLowerCase()}`}>
                                {result.priority}
                            </span>
                        </div>

                        <div className="result-section">
                            <span className="result-label">Task</span>
                            <p>{result.task}</p>
                        </div>

                        <div className="result-section">
                            <span className="result-label">Category</span>
                            <p>{result.category}</p>
                        </div>

                        <div className="suggestion">
                            <span className="result-label">💡 Suggestion</span>
                            <p>{result.suggestion}</p>
                        </div>
                    </div>
                )}

                <footer>
                    <p>Powered by AI</p>
                </footer>

            </div>
        </div>
    );
}

export default App