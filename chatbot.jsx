import React, { useState } from "react";
import axios from "axios";

const Chatbot = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    // Function to send message to the Flask API
    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = { text: input, sender: "user" };
        setMessages([...messages, userMessage]);
        setLoading(true);
        setInput(""); // Clear the input field

        try {
            const response = await axios.post("http://127.0.0.1:5000/get_response", {
                query: input,
            });

            const botMessage = {
                text: response.data.response || response.data.disease_info || "Sorry, I couldn't understand that.",
                sender: "bot",
            };

            setMessages([...messages, userMessage, botMessage]);
        } catch (error) {
            console.error("Error fetching response:", error);
            setMessages([
                ...messages,
                { text: "Sorry, something went wrong.", sender: "bot" },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chatbot-container">
            <div className="chatbox">
                {messages.map((message, index) => (
                    <div key={index} className={message.sender}>
                        <p>{message.text}</p>
                    </div>
                ))}
            </div>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && sendMessage()}
            />
            <button onClick={sendMessage} disabled={loading}>
                {loading ? "Loading..." : "Send"}
            </button>
        </div>
    );
};

export default Chatbot;
