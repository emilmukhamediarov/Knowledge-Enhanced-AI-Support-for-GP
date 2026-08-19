//TO become patient chat
import "./Chat.css";

import { useState, useEffect } from "react";
import { apiFetch } from "../../api/client";


type Message = {
  role: "user" | "assistant";
  content: string;
};

function Chat() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>(() => {
        const savedMessages = localStorage.getItem("chatMessages");
        if (!savedMessages) {
            return [];
        }
        try {
            return JSON.parse(savedMessages);
        } catch {
            return [];
        }
    });

    useEffect(() => {
        localStorage.setItem("chatMessages", JSON.stringify(messages));
    }, [messages]);

    const sendMessage = async () => {
        if (!message.trim()) return;

        const userMessage: Message = {
            role: "user",
            content: message,
        };

        setMessages((previous) => [...previous, userMessage]);

    // Clear input box
    setMessage("");

    try {
        const data = await apiFetch("/chat", {
            method: "POST",
               headers: {
                    "Content-Type": "application/json",
               },
           body: JSON.stringify({
               message: userMessage.content,
               }),
          });

        const assistantMessage: Message = {
            role: "assistant",
               content: data.reply,
        };

        // AI response loaded here
        setMessages((previous) => [...previous, {role: "assistant", content:"",},]);
        for (let i=0; i<data.reply.length; i++) {
            await new Promise((resolve) => setTimeout(resolve, 15));
            setMessages((previous) => {
                const messages = [...previous];
                messages[messages.length-1] = {
                    role: "assistant",
                    content: data.reply.slice(0, i+1),
                };
                return messages
                });
            }
        } catch (error) {
            console.error("Chat error:", error);
        }
    };

    //Reset chat functionality
    const resetChat = async () => {
            try {await apiFetch("/reset", {method: "POST",});

            setMessages([]);
            localStorage.removeItem("chatMessages");
        } catch (error) {
            console.error("Reset error:", error);
        }
    };

    return (
        <main>
            <h1>Chatbot</h1>

            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index}>
                        <strong>
                            {msg.role === "user" ? "You" : "AI"}:
                        </strong>{" "}
                        {msg.content}
                    </div>
            ))}
            </div>

            <div className="chat-input">
                <input
                type="text"
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                onKeyDown={(event) => {
                    if (event.key === "Enter") {
                        event.preventDefault();
                        sendMessage();
                        }
                    }
                }
                placeholder="Type your message..."
                />
                <button onClick={sendMessage}>
                    Send
                </button>

            </div>

            <button onClick={resetChat} className="reset-button">
                New Chat
            </button>
        </main>
    );

}

export default Chat;