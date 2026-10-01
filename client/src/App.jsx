import { useState } from "react";

function App() {
    const [task, setTask] = useState("");
    const [result, setResult] = useState(null);

    async function analyseTask() {
        try {
            console.log("clicked the analyse button")

            const response = await fetch("http://127.0.0.1:3000/api/analyse", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    task_text: task
                })
            });

            const data = await response.json();

            setResult(data);
            console.log("done processing")

        } catch (error) {
            console.error("Error:", error);
        }
    }

    return (
        <div>
            <h1>AI Task Assistant</h1>

            <input
                type="text"
                value={task}
                onChange={(event) => setTask(event.target.value)}
                placeholder="Enter a task"
            />

            <button onClick={analyseTask}>
                Analyse Task
            </button>

            {result && (
                <div>
                    <h2>Analysis</h2>

                    <p>
                        <strong>Task:</strong> {result.task}
                    </p>

                    <p>
                        <strong>Priority:</strong> {result.priority}
                    </p>

                    <p>
                        <strong>Category:</strong> {result.category}
                    </p>

                    <p>
                        <strong>Suggestion:</strong> {result.suggestion}
                    </p>
                </div>
            )}
        </div>
    );
}

export default App;