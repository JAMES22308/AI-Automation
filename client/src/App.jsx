import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./App.css";



function App() {

    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);


    async function sendMessage() {

        if (!message.trim() || loading) {
            return;
        }

        const userMessage = message.trim();


        // Show user's message immediately
        setMessages((previousMessages) => [
            ...previousMessages,
            {
                role: "user",
                content: userMessage
            }
        ]);


        setMessage("");
        setLoading(true);


        try {

            const response = await fetch(
                "https://ai-task-assistant-api.onrender.com//chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        message: userMessage
                    })
                }
            );


            const data = await response.json();


            if (!response.ok) {
                throw new Error(
                    data.detail || "Something went wrong."
                );
            }


            // Show AI response
            setMessages((previousMessages) => [
                ...previousMessages,
                {
                    role: "assistant",
                    content: data.response
                }
            ]);


        } catch (error) {

            console.error("Error:", error);


            setMessages((previousMessages) => [
                ...previousMessages,
                {
                    role: "assistant",
                    content:
                        "Sorry, I couldn't process your request."
                }
            ]);


        } finally {

            setLoading(false);

        }
    }


    function handleKeyDown(event) {

        if (event.key === "Enter" && !event.shiftKey) {

            event.preventDefault();

            sendMessage();
        }
    }


    return (

        <div className="app">

            <div className="chat-container">


                <header className="chat-header">

                    <div className="logo">
                        ✦
                    </div>

                    <div>

                        <h1>
                            Lexia
                        </h1>

                        <p>
                            Ask me anything
                        </p>

                    </div>

                </header>


                <main className="messages">


                    {messages.length === 0 && (

                        <div className="welcome">

                            <div className="welcome-icon">
                                ✦
                            </div>

                            <h2>
                                How can I help you?
                            </h2>

                            <p>
                                Ask me a question, write some code,
                                debug an error, or get help with a task.
                            </p>


                            <div className="examples">


                                <button
                                    onClick={() =>
                                        setMessage(
                                            "Write a Python function that checks if a number is prime."
                                        )
                                    }
                                >
                                    💻 Write some code
                                </button>


                                <button
                                    onClick={() =>
                                        setMessage(
                                            "Explain what a REST API is."
                                        )
                                    }
                                >
                                    📚 Explain something
                                </button>


                                <button
                                    onClick={() =>
                                        setMessage(
                                            "Help me plan my programming assignment."
                                        )
                                    }
                                >
                                    📋 Plan a task
                                </button>


                            </div>

                        </div>

                    )}


                    {messages.map((item, index) => (

                        <div
                            className={`message ${
                                item.role === "user"
                                    ? "user-message"
                                    : "assistant-message"
                            }`}
                            key={index}
                        >


                            <div className="message-avatar">

                                {item.role === "user"
                                    ? "You"
                                    : "✦"}

                            </div>


                            <div className="message-content">


                                <div className="message-role">

                                    {item.role === "user"
                                        ? "You"
                                        : "AI Assistant"}

                                </div>


                                <div className="message-text">

                                    <ReactMarkdown
                                        remarkPlugins={[remarkGfm]}
                                    >
                                        {item.content}
                                    </ReactMarkdown>

                                </div>


                            </div>

                        </div>

                    ))}


                    {loading && (

                        <div className="message assistant-message">

                            <div className="message-avatar">
                                ✦
                            </div>


                            <div className="message-content">

                                <div className="message-role">
                                    AI Assistant
                                </div>


                                <div className="typing">
                                    Thinking...
                                </div>

                            </div>

                        </div>

                    )}

                </main>


                <div className="input-area">


                    <textarea
                        value={message}

                        onChange={(event) =>
                            setMessage(event.target.value)
                        }

                        onKeyDown={handleKeyDown}

                        placeholder="Ask anything..."

                        rows="1"

                        disabled={loading}
                    />


                    <button
                        onClick={sendMessage}
                        disabled={
                            !message.trim() || loading
                        }
                    >
                        ➤
                    </button>

                </div>


               <footer>
                AI responses may not always be accurate.
                <br />
                Created by Michael James Soria
            </footer>

            </div>

        </div>
    );
}


export default App;