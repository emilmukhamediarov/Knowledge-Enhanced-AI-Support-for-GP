import "./Chat.css";
import { useState, useEffect, useRef } from "react";
import { apiFetch } from "../../api/client";
import { useParams } from "react-router-dom";

interface Message {
    role: "user" | "assistant";
    content: string;
}

function Chat() {
    const { consultationId } = useParams<{
        consultationId: string;
    }>();

    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    // Audio recording state
    const [isRecording, setIsRecording] = useState(false);
    const mediaRecorderRef =
        useRef<MediaRecorder | null>(null);
    const mediaStreamRef =
        useRef<MediaStream | null>(null);
    const audioChunksRef =
        useRef<Blob[]>([]);

    // Used to automatically scroll to the newest message
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Used to automatically focus the input after the AI finishes
    const inputRef = useRef<HTMLInputElement>(null);

    // Load messages for this consultation
    useEffect(() => {
        if (!consultationId) {
            setError("Unable to identify the consultation.");
            return;
        }

        const loadMessages = async () => {
            try {
                setError("");

                const data = await apiFetch(
                    `/consultations/${consultationId}/messages`
                );

                setMessages(
                    data.messages.map(
                        (msg: {
                            role: "user" | "assistant";
                            content: string;
                        }) => ({
                            role: msg.role,
                            content: msg.content,
                        })
                    )
                );
            } catch (error) {
                console.error(
                    "Failed to load messages:",
                    error
                );

                setError(
                    "Failed to load conversation."
                );
            }
        };

        void loadMessages();
    }, [consultationId]);

    const sendMessage = async () => {
        if (!message.trim() || loading) return;

        if (!consultationId) {
            setError(
                "Unable to identify the consultation."
            );
            return;
        }

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

                    updatedMessages[
                    updatedMessages.length - 1
                        ] = {
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

    // Added by James and Codex. Just to test voice input.
    // ---------------------------------------------------
    // ---------------------------------------------------
    // ---------------------------------------------------

    const uploadAudio = async (
        audioBlob: Blob,
        extension: string,
    ) => {
        if (!consultationId) {
            setError(
                "Unable to identify the consultation."
            );
            return;
        }

        const formData = new FormData();

        formData.append(
            "audio",
            audioBlob,
            `recording.${extension}`,
        );

        setLoading(true);
        setError("");

        try {
            const data = await apiFetch(
                `/consultations/${consultationId}/audio-chat`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            // Display the transcript as the user's message
            setMessages((previous) => [
                ...previous,
                {
                    role: "user",
                    content: data.transcript,
                },
            ]);

            // Display an empty assistant message
            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: "",
                },
            ]);

            // Preserve the existing typing effect
            for (let i = 0; i < data.reply.length; i++) {
                await new Promise((resolve) =>
                    setTimeout(resolve, 15)
                );

                setMessages((previous) => {
                    const updatedMessages = [...previous];

                    updatedMessages[
                    updatedMessages.length - 1
                        ] = {
                        role: "assistant",
                        content: data.reply.slice(0, i + 1),
                    };

                    return updatedMessages;
                });
            }
        } catch (error) {
            console.error("Audio chat error:", error);
            setError("Failed to process the recording.");
        } finally {
            setLoading(false);

            setTimeout(() => {
                inputRef.current?.focus();
            }, 0);
        }
    };


    const startRecording = async () => {
        if (loading || isRecording) {
            return;
        }

        setError("");

        if (
            !navigator.mediaDevices?.getUserMedia ||
            typeof MediaRecorder === "undefined"
        ) {
            setError(
                "Audio recording is not supported by this browser."
            );
            return;
        }

        try {
            const stream =
                await navigator.mediaDevices.getUserMedia({
                    audio: true,
                });

            mediaStreamRef.current = stream;

            const supportedMimeTypes = [
                "audio/webm;codecs=opus",
                "audio/mp4",
                "audio/webm",
            ];

            const mimeType = supportedMimeTypes.find(
                (type) =>
                    MediaRecorder.isTypeSupported(type)
            );

            const recorder = mimeType
                ? new MediaRecorder(stream, { mimeType })
                : new MediaRecorder(stream);

            mediaRecorderRef.current = recorder;
            audioChunksRef.current = [];

            recorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            recorder.onstop = () => {
                const recordedType =
                    recorder.mimeType ||
                    mimeType ||
                    "audio/webm";

                const extension =
                    recordedType.includes("mp4")
                        ? "m4a"
                        : recordedType.includes("ogg")
                            ? "ogg"
                            : "webm";

                const audioBlob = new Blob(
                    audioChunksRef.current,
                    {
                        type: recordedType,
                    }
                );

                stream
                    .getTracks()
                    .forEach((track) => track.stop());

                mediaStreamRef.current = null;
                mediaRecorderRef.current = null;

                setIsRecording(false);

                void uploadAudio(
                    audioBlob,
                    extension,
                );
            };

            recorder.start();
            setIsRecording(true);
        } catch (error) {
            console.error("Microphone error:", error);

            setError(
                "Microphone permission was denied or unavailable."
            );
        }
    };


    const stopRecording = () => {
        const recorder = mediaRecorderRef.current;

        if (
            recorder &&
            recorder.state !== "inactive"
        ) {
            recorder.stop();
        }
    };

    // ---------------------------------------------------
    // ---------------------------------------------------
    // ---------------------------------------------------

    const handleKeyDown = (
        e: React.KeyboardEvent<HTMLInputElement>
    ) => {
        if (e.key === "Enter") {
            void sendMessage();
        }
    };

    // New chat functionality
    const resetChat = async () => {
        if (!consultationId) {
            setError(
                "Unable to identify the consultation."
            );
            return;
        }

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
                    className={
                        isRecording
                            ? "record-button recording"
                            : "record-button"
                    }
                    onClick={
                        isRecording
                            ? stopRecording
                            : startRecording
                    }
                    disabled={loading}
                    aria-pressed={isRecording}
                >
                    {isRecording ? "Stop" : "🎤 Voice"}
                </button>

                <button
                    type="button"
                    onClick={() => void sendMessage()}
                    disabled={loading}
                >
                    {loading ? "Sending..." : "Send"}
                </button>
            </div>

            <button
                type="button"
                onClick={() => void resetChat()}
                className="reset-button"
            >
                New Chat
            </button>
        </main>
    );
}

export default Chat;