import "./Chat.css";
import { useState, useEffect, useRef } from "react";
import { apiFetch } from "../../api/client";
import { useParams } from "react-router-dom";
import micIcon from "../../assets/mic-icon.png";

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
    const mediaStreamRef =
        useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioProcessorRef = useRef<ScriptProcessorNode | null>(null);
    const audioSourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
    const transcriptionSocketRef = useRef<WebSocket | null>(null);
    const partialTranscriptRef = useRef("");
    const finalTranscriptRef = useRef<string[]>([]);

    // Used to automatically scroll to the newest message
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Used to automatically focus the input after the AI finishes
    const inputRef = useRef<HTMLTextAreaElement>(null);

    const [showResetConfirmation, setShowResetConfirmation] = useState(false);

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

    const sendMessage = async (text?: string) => {
        const messageToSend = text ?? message;

        if (!messageToSend.trim() || loading) return;

        if (!consultationId) {
            setError(
                "Unable to identify the consultation."
            );
            return;
        }

        const userMessage = messageToSend.trim();

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

    const downsampleTo16kPcm = (input: Float32Array, inputRate: number) => {
        const ratio = inputRate / 16000;
        const output = new Int16Array(Math.round(input.length / ratio));

        for (let index = 0; index < output.length; index += 1) {
            const start = Math.floor(index * ratio);
            const end = Math.min(Math.floor((index + 1) * ratio), input.length);
            let total = 0;
            for (let sample = start; sample < end; sample += 1) total += input[sample];
            output[index] = Math.max(-1, Math.min(1, total / Math.max(1, end - start))) * 0x7fff;
        }
        return output.buffer;
    };

    const stopAudioResources = () => {
        audioProcessorRef.current?.disconnect();
        audioSourceRef.current?.disconnect();
        void audioContextRef.current?.close();
        mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
        audioProcessorRef.current = null;
        audioSourceRef.current = null;
        audioContextRef.current = null;
        mediaStreamRef.current = null;
    };

    const startRecording = async () => {
        if (loading || isRecording) {
            return;
        }

        setError("");

        if (!navigator.mediaDevices?.getUserMedia) {
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

            const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
            const socketUrl = apiUrl.replace(/^http/, "ws");
            const socket = new WebSocket(
                `${socketUrl}/consultations/${consultationId}/audio-stream`,
            );
            transcriptionSocketRef.current = socket;
            finalTranscriptRef.current = [];
            partialTranscriptRef.current = "";

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.event === "transcript") {
                    if (data.is_final) {
                        finalTranscriptRef.current.push(data.text);
                        partialTranscriptRef.current = "";
                    } else {
                        partialTranscriptRef.current = data.text;
                    }
                    setMessage(
                        [...finalTranscriptRef.current, partialTranscriptRef.current]
                            .filter(Boolean)
                            .join(" "),
                    );
                }
                if (data.event === "complete") {
                    void sendMessage(data.transcript);
                }
                if (data.event === "error") {
                    setError(data.detail || "Live transcription failed.");
                }
            };
            socket.onerror = () => setError("Could not start live transcription.");

            const context = new AudioContext();
            const source = context.createMediaStreamSource(stream);
            const processor = context.createScriptProcessor(4096, 1, 1);
            source.connect(processor);
            processor.connect(context.destination);
            processor.onaudioprocess = (event) => {
                if (socket.readyState !== WebSocket.OPEN) return;
                socket.send(
                    downsampleTo16kPcm(
                        event.inputBuffer.getChannelData(0),
                        context.sampleRate,
                    ),
                );
            };
            audioContextRef.current = context;
            audioSourceRef.current = source;
            audioProcessorRef.current = processor;
            setIsRecording(true);
        } catch (error) {
            console.error("Microphone error:", error);

            setError(
                "Microphone permission was denied or unavailable."
            );
        }
    };


    const stopRecording = () => {
        if (!isRecording) return;
        stopAudioResources();
        transcriptionSocketRef.current?.send(JSON.stringify({ event: "stop" }));
        transcriptionSocketRef.current = null;
        setIsRecording(false);
    };

    // ---------------------------------------------------
    // ---------------------------------------------------
    // ---------------------------------------------------

    const handleKeyDown = (
        e: React.KeyboardEvent<HTMLTextAreaElement>
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
            setShowResetConfirmation(false);

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
            {showResetConfirmation && (
                <div className="reset-confirmation">
                    <div className="reset-confirmation-box">
                        <h3>Reset chat?</h3>

                        <p>
                            Are you sure you want to reset this chat?
                            This will delete all messages and responses.
                        </p>

                        <div className="reset-confirmation-actions">
                            <button
                                type="button"
                                onClick={() => setShowResetConfirmation(false)}
                                className="reset-cancel-button"
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                onClick={() => void resetChat()}
                                className="reset-confirm-button"
                            >
                                Reset Chat
                            </button>
                        </div>
                    </div>
                </div>
            )}
            <div className="messages">
                <button
                    type="button"
                    onClick={() => setShowResetConfirmation(true)}
                    className="reset-button"
                >
                    Reset Chat
                </button>

                {messages.length === 0 && (
                    <div className="chat-welcome">
                        <h1>How can we help you today?</h1>
                        <p>Tell us what’s bothering you, and we’ll help you work out what to do next.</p>
                    </div>
                )}
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
    <textarea
        ref={inputRef}
        value={message}
        onChange={(event) =>
            setMessage(event.target.value)
        }
        onKeyDown={handleKeyDown}
        placeholder="Type your message..."
        disabled={loading}
        rows={1}
    />

                <div className="chat-input-actions">
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
                        <img
                            src={micIcon}
                            alt={
                                isRecording
                                    ? "Stop recording"
                                    : "Start voice recording"
                            }
                        />
                    </button>

                    <button
                        type="button"
                        className="send-button"
                        onClick={() => void sendMessage()}
                        disabled={loading || message.trim() === ""}
                        aria-label="Send message"
                    >
                        ➤
                    </button>
                </div>
            </div>
        </main>
    );
}

export default Chat;