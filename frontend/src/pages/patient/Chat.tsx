import "./Chat.css";
import { useState, useEffect, useRef } from "react";
import { apiFetch } from "../../api/client";

interface Message {
    role: "user" | "assistant";
    content: string;
}

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

    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    // Used to automatically scroll to the newest message
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Used to automatically focus the input after the AI finishes
    const inputRef = useRef<HTMLInputElement>(null);

    // TEMPORARY: HARD-CODED CONSULTATION ID
    const consultationId = 1;

    // Save chat history
    useEffect(() => {
        localStorage.setItem("chatMessages", JSON.stringify(messages));
    }, [messages]);

    // Automatically scroll to the newest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "auto",
        });
    }, [messages]);

    const sendMessage = async () => {
        if (!message.trim() || loading) return;

        const userMessage = message.trim();

        setError("");
        setMessage("");

        // Add user's message
        setMessages((previous) => [
            ...previous,
            {
                role: "user",
                content: userMessage,
            },
        ]);

        setLoading(true);

        try {
            const data = await apiFetch(
                `/consultations/${consultationId}/chat`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        message: userMessage,
                    }),
                }
            );

            // Add an empty AI message
            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: "",
                },
            ]);

            // Typing effect
            for (let i = 0; i < data.reply.length; i++) {
                await new Promise((resolve) =>
                    setTimeout(resolve, 15)
                );

                setMessages((previous) => {
                    const updatedMessages = [...previous];

                    updatedMessages[updatedMessages.length - 1] = {
                        role: "assistant",
                        content: data.reply.slice(0, i + 1),
                    };

                    return updatedMessages;
                });
            }

            // Focus input after AI finishes
            inputRef.current?.focus();

        } catch (error) {
            console.error("Chat error:", error);
            setError("Failed to send message.");
        } finally {
            setLoading(false);

            // Make sure input receives focus after loading finishes
            setTimeout(() => {
                inputRef.current?.focus();
            }, 0);
        }
    };

    const handleKeyDown = (
        e: React.KeyboardEvent<HTMLInputElement>
    ) => {
        if (e.key === "Enter") {
            sendMessage();
        }
    };

    // New chat functionality
    const resetChat = async () => {
        try {
            await apiFetch(
                `/consultations/${consultationId}/messages`,
                {
                    method: "DELETE",
                }
            );
            setMessages([]);
            setMessage("");
            setError("");

            localStorage.removeItem("chatMessages");

            setTimeout(() => {
                inputRef.current?.focus();
            }, 0);
        } catch (error) {
            console.error("Reset error:", error);
            setError("Failed to clear conversation.");
        }
    };

    return (
        <main>
            <h1>Chatbot</h1>

            <div className="messages">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={
                            msg.role === "user"
                                ? "user-message"
                                : "ai-message"
                        }
                    >
                        {msg.content}
                    </div>
                ))}

                <div
                    ref={messagesEndRef}
                    className="messages-end"
                />
            </div>

            {error && (
                <p className="chat-error">
                    {error}
                </p>
            )}

            <div className="chat-input">
                <input
                    ref={inputRef}
                    type="text"
                    value={message}
                    onChange={(event) =>
                        setMessage(event.target.value)
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    disabled={loading}
                />

                <button
                    type="button"
                    onClick={sendMessage}
                    disabled={loading}
                >
                    {loading ? "Sending..." : "Send"}
                </button>
            </div>

            <button
                onClick={resetChat}
                className="reset-button"
            >
                New Chat
            </button>
        </main>
    );
}

export default Chat;