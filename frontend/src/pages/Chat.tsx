import { useState } from "react";
import { apiFetch } from "../api/client";

type Message = {
  role: "user" | "assistant";
  content: string;
};

function Chat() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);

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
            await new Promise((resolve) => setTimeout(resolve, 10));
            setMessages((previous) => {
                const messages = [...previous];
                messages[messages.length-1] = {
                    role: "assistant",
                    content: data.reply.slice(0, i),
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
            } catch (error) {
                console.error("Reset error:", error);
            }
        };

    return (
        <main>
            <h1>Chatbot</h1>

            <div>
                {messages.map((msg, index) => (
                    <div key={index}>
                        <strong>
                            {msg.role === "user" ? "You" : "AI"}:
                        </strong>{" "}
                        {msg.content}
                    </div>
            ))}
            </div>

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
            <button onClick={resetChat}>
                New Chat
            </button>
        </main>
    );

}

export default Chat;