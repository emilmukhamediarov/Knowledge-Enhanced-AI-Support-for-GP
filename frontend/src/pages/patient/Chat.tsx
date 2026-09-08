import "./Chat.css";
import { useState, useEffect, useRef } from "react";
import { apiFetch } from "../../api/client";
import { useNavigate, useParams } from "react-router-dom";
import micIcon from "../../assets/mic-icon.png";

import { AvatarSpeaker } from "../../components/Avatar/AvatarSpeaker.tsx";

interface Message {
    role: "user" | "assistant";
    content: string;
}

function Chat() {
    const { consultationId } = useParams<{
        consultationId: string;
    }>();

    const navigate = useNavigate();

    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const sendingRef = useRef(false);

    // Confirmation dialogs
    const [showResetConfirmation, setShowResetConfirmation] =
        useState(false);

    const [showDeleteConfirmation, setShowDeleteConfirmation] =
        useState(false);

    const [showCloseConfirmation, setShowCloseConfirmation] =
        useState(false);

    const [closing, setClosing] = useState(false);

    // Audio recording state
    const [isRecording, setIsRecording] = useState(false);
    const [volumeLevel, setVolumeLevel] = useState(0);

    const mediaStreamRef = useRef<MediaStream | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);
    const audioProcessorRef = useRef<ScriptProcessorNode | null>(null);
    const audioSourceRef =
        useRef<MediaStreamAudioSourceNode | null>(null);

    const transcriptionSocketRef =
        useRef<WebSocket | null>(null);

    const partialTranscriptRef = useRef("");
    const finalTranscriptRef = useRef<string[]>([]);

    // Automatically scroll to newest message
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Automatically focus input after AI finishes
    const inputRef = useRef<HTMLTextAreaElement>(null);

    // Avatar
    const avatarContainerRef = useRef<HTMLDivElement>(null);
    const avatarRef = useRef<AvatarSpeaker | null>(null);

    // Initialize avatar
    useEffect(() => {
        if (!avatarContainerRef.current) {
            return;
        }

        const avatar = new AvatarSpeaker(
            avatarContainerRef.current
        );

        avatarRef.current = avatar;

        void avatar.init().catch((error: any) => {
            console.error(
                "Avatar initialization failed:",
                error
            );
        });

        return () => {
            avatar.dispose();

            if (avatarRef.current === avatar) {
                avatarRef.current = null;
            }
        };
    }, []);

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

                setError("Failed to load conversation.");
            }
        };

        void loadMessages();
    }, [consultationId]);

    // Automatically scroll to newest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages]);

    // Cleanup audio resources when leaving page
    useEffect(() => {
        return () => {
            stopAudioResources();

            if (
                transcriptionSocketRef.current &&
                transcriptionSocketRef.current.readyState ===
                WebSocket.OPEN
            ) {
                transcriptionSocketRef.current.close();
            }
        };
    }, []);

    // Send a message
    const sendMessage = async (text?: string) => {
        if (sendingRef.current) {
            return;
        }

        if (isRecording) {
            stopRecording();
        }

        const messageToSend = text ?? message;

        if (!messageToSend.trim() || loading) {
            return;
        }

        if (!consultationId) {
            setError("Unable to identify the consultation.");
            return;
        }

        sendingRef.current = true;
        setLoading(true);

        const userMessage = messageToSend.trim();

        setError("");
        setMessage("");

        finalTranscriptRef.current = [];
        partialTranscriptRef.current = "";

        setMessages((previous) => [
            ...previous,
            {
                role: "user",
                content: userMessage,
            },
        ]);

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

            // Speak chatbot response using avatar
            void avatarRef.current
                ?.speak(
                    data.reply,
                    data.language_code ?? "en-US"
                )
                .catch((error) => {
                    console.error(
                        "Avatar speech failed:",
                        error
                    );
                });

            // Add empty AI message
            setMessages((previous) => [
                ...previous,
                {
                    role: "assistant",
                    content: "",
                },
            ]);

            // Typing effect
            for (
                let i = 0;
                i < data.reply.length;
                i++
            ) {
                await new Promise((resolve) =>
                    setTimeout(resolve, 15)
                );

                setMessages((previous) => {
                    const updatedMessages = [
                        ...previous,
                    ];

                    updatedMessages[
                    updatedMessages.length - 1
                        ] = {
                        role: "assistant",
                        content: data.reply.slice(
                            0,
                            i + 1
                        ),
                    };

                    return updatedMessages;
                });
            }

            inputRef.current?.focus();
        } catch (error) {
            console.error("Chat error:", error);

            setError("Failed to send message.");
        } finally {
            sendingRef.current = false;
            setLoading(false);

            setTimeout(() => {
                inputRef.current?.focus();
            }, 0);
        }
    };

    // Downsample microphone audio to 16 kHz PCM
    const downsampleTo16kPcm = (
        input: Float32Array,
        inputRate: number
    ) => {
        const ratio = inputRate / 16000;

        const output = new Int16Array(
            Math.round(input.length / ratio)
        );

        for (
            let index = 0;
            index < output.length;
            index += 1
        ) {
            const start = Math.floor(index * ratio);

            const end = Math.min(
                Math.floor((index + 1) * ratio),
                input.length
            );

            let total = 0;

            for (
                let sample = start;
                sample < end;
                sample += 1
            ) {
                total += input[sample];
            }

            output[index] =
                Math.max(
                    -1,
                    Math.min(
                        1,
                        total /
                        Math.max(
                            1,
                            end - start
                        )
                    )
                ) * 0x7fff;
        }

        return output.buffer;
    };

    // Stop and clean up audio resources
    const stopAudioResources = () => {
        audioProcessorRef.current?.disconnect();
        audioSourceRef.current?.disconnect();

        void audioContextRef.current?.close();

        mediaStreamRef.current
            ?.getTracks()
            .forEach((track) => track.stop());

        audioProcessorRef.current = null;
        audioSourceRef.current = null;
        audioContextRef.current = null;
        mediaStreamRef.current = null;

        setVolumeLevel(0);
    };

    // Start voice recording
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

        if (!consultationId) {
            setError(
                "Unable to identify the consultation."
            );

            return;
        }

        try {
            const stream =
                await navigator.mediaDevices.getUserMedia({
                    audio: true,
                });

            mediaStreamRef.current = stream;

            const apiUrl =
                import.meta.env.VITE_API_URL ||
                "http://localhost:8000";

            const socketUrl =
                apiUrl.replace(/^http/, "ws");

            const socket = new WebSocket(
                `${socketUrl}/consultations/${consultationId}/audio-stream`
            );

            transcriptionSocketRef.current = socket;

            finalTranscriptRef.current = [];
            partialTranscriptRef.current = "";

            socket.onmessage = (event) => {
                const data = JSON.parse(event.data);

                if (data.event === "transcript") {
                    if (data.is_final) {
                        finalTranscriptRef.current.push(
                            data.text
                        );

                        partialTranscriptRef.current = "";
                    } else {
                        partialTranscriptRef.current =
                            data.text;
                    }

                    setMessage(
                        [
                            ...finalTranscriptRef.current,
                            partialTranscriptRef.current,
                        ]
                            .filter(Boolean)
                            .join(" ")
                    );
                }

                if (data.event === "complete") {
                    void sendMessage(data.transcript);
                }

                if (data.event === "error") {
                    setError(
                        data.detail ||
                        "Live transcription failed."
                    );
                }
            };

            socket.onerror = () => {
                setError(
                    "Could not start live transcription."
                );
            };

            const context = new AudioContext();

            const source =
                context.createMediaStreamSource(stream);

            const processor =
                context.createScriptProcessor(
                    4096,
                    1,
                    1
                );

            source.connect(processor);
            processor.connect(context.destination);

            processor.onaudioprocess = (event) => {
                const inputData =
                    event.inputBuffer.getChannelData(0);

                // Calculate volume level
                let sum = 0;

                for (
                    let i = 0;
                    i < inputData.length;
                    i++
                ) {
                    sum +=
                        inputData[i] *
                        inputData[i];
                }

                const rms = Math.sqrt(
                    sum / inputData.length
                );

                setVolumeLevel(
                    Math.min(
                        Math.round(rms * 400),
                        100
                    )
                );

                if (
                    socket.readyState !==
                    WebSocket.OPEN
                ) {
                    return;
                }

                socket.send(
                    downsampleTo16kPcm(
                        inputData,
                        context.sampleRate
                    )
                );
            };

            audioContextRef.current = context;
            audioSourceRef.current = source;
            audioProcessorRef.current = processor;

            setIsRecording(true);
        } catch (error) {
            console.error(
                "Microphone error:",
                error
            );

            setError(
                "Microphone permission was denied or unavailable."
            );
        }
    };

    // Stop voice recording
    const stopRecording = () => {
        stopAudioResources();

        if (
            transcriptionSocketRef.current &&
            transcriptionSocketRef.current.readyState ===
            WebSocket.OPEN
        ) {
            transcriptionSocketRef.current.send(
                JSON.stringify({
                    event: "stop",
                })
            );
        }

        transcriptionSocketRef.current = null;

        finalTranscriptRef.current = [];
        partialTranscriptRef.current = "";

        setIsRecording(false);
    };

    // Handle Enter key
    const handleKeyDown = (
        e: React.KeyboardEvent<HTMLTextAreaElement>
    ) => {
        if (e.key === "Enter") {
            e.preventDefault();

            void sendMessage();
        }
    };

    // Reset chat messages
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
            console.error(
                "Reset error:",
                error
            );

            setError(
                "Failed to clear conversation."
            );
        }
    };

    // Delete consultation
    const deleteChat = async () => {
        if (!consultationId) {
            setError(
                "Unable to identify the consultation."
            );

            return;
        }

        try {
            await apiFetch(
                `/consultations/${consultationId}`,
                {
                    method: "DELETE",
                }
            );

            setShowDeleteConfirmation(false);

            window.location.href = "/patienthome";
        } catch (error) {
            console.error(
                "Delete chat error:",
                error
            );

            setError(
                "Failed to delete conversation."
            );
        }
    };

    // Close consultation
    const closeConsultation = async () => {
        if (!consultationId) {
            setError("Unable to identify the consultation.");
            return;
        }

        try {
            setClosing(true);
            setError("");

            await apiFetch(
                `/consultations/${consultationId}/close`,
                {
                    method: "PATCH",
                }
            );

            setShowCloseConfirmation(false);

            // Return to Home after successfully closing
            navigate("/patienthome");
        } catch (error) {
            console.error("Close consultation error:", error);

            setError("Failed to close consultation.");
            setClosing(false);
        }
    };

    return (
        <main className="chat-page">
            {/* Avatar */}
            <div
                ref={avatarContainerRef}
                className="avatar-container"
            />

            {/* Reset confirmation */}
            {showResetConfirmation && (
                <div className="reset-confirmation">
                    <div className="reset-confirmation-box">
                        <h3>Reset chat?</h3>

                        <p>
                            Are you sure you want
                            to reset this chat?
                            This will delete all
                            messages and responses.
                        </p>

                        <div className="reset-confirmation-actions">
                            <button
                                type="button"
                                onClick={() =>
                                    setShowResetConfirmation(
                                        false
                                    )
                                }
                                className="reset-cancel-button"
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                onClick={() =>
                                    void resetChat()
                                }
                                className="reset-confirm-button"
                            >
                                Reset Chat
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete confirmation */}
            {showDeleteConfirmation && (
                <div className="reset-confirmation">
                    <div className="reset-confirmation-box">
                        <h3>Delete chat?</h3>

                        <p>
                            Are you sure you want
                            to delete this chat?
                            This will permanently
                            delete the consultation
                            and all of its messages.
                        </p>

                        <div className="reset-confirmation-actions">
                            <button
                                type="button"
                                onClick={() =>
                                    setShowDeleteConfirmation(
                                        false
                                    )
                                }
                                className="reset-cancel-button"
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                onClick={() =>
                                    void deleteChat()
                                }
                                className="reset-confirm-button"
                            >
                                Delete Chat
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Close consultation confirmation */}
            {showCloseConfirmation && (
                <div className="confirmation-overlay">
                    <div className="confirmation-popup">
                        <div className="confirmation-icon">
                            !
                        </div>

                        <h2>Close consultation?</h2>

                        <p>
                            Are you sure you want
                            to close this
                            consultation? Once
                            closed, you will no
                            longer be able to
                            continue this
                            conversation.
                        </p>

                        <div className="confirmation-actions">
                            <button
                                type="button"
                                className="confirmation-cancel"
                                onClick={() =>
                                    setShowCloseConfirmation(
                                        false
                                    )
                                }
                                disabled={closing}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="confirmation-confirm"
                                onClick={() =>
                                    void closeConsultation()
                                }
                                disabled={closing}
                            >
                                {closing
                                    ? "Closing..."
                                    : "Close Consultation"}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Chat actions */}
            <div className="chat-actions">
                <button
                    type="button"
                    onClick={() =>
                        setShowResetConfirmation(true)
                    }
                    className="reset-button"
                >
                    Reset Chat
                </button>

                <button
                    type="button"
                    onClick={() =>
                        setShowDeleteConfirmation(true)
                    }
                    className="delete-button"
                >
                    Delete Chat
                </button>

                <button
                    type="button"
                    onClick={() =>
                        setShowCloseConfirmation(true)
                    }
                    className="close-button"
                    disabled={closing}
                >
                    Close Consultation
                </button>
            </div>

            {/* Scrollable messages */}
            <div className="messages">
                {messages.length === 0 && (
                    <div className="chat-welcome">
                        <h1>
                            How can we help you
                            today?
                        </h1>

                        <p>
                            Tell us what’s
                            bothering you, and
                            we’ll help you work
                            out what to do next.
                        </p>
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

            {/* Error */}
            {error && (
                <p className="chat-error">
                    {error}
                </p>
            )}

            {/* Voice visualizer */}
            {isRecording && (
                <div className="voice-indicator-container">
                    <span className="voice-status-text">
                        Listening...
                    </span>

                    <div className="audio-wave-bars">
                        <div
                            className="wave-bar"
                            style={{
                                height: `${Math.max(
                                    15,
                                    volumeLevel * 0.8
                                )}%`,
                            }}
                        />

                        <div
                            className="wave-bar"
                            style={{
                                height: `${Math.max(
                                    25,
                                    volumeLevel * 1.2
                                )}%`,
                            }}
                        />

                        <div
                            className="wave-bar"
                            style={{
                                height: `${Math.max(
                                    15,
                                    volumeLevel * 0.9
                                )}%`,
                            }}
                        />
                    </div>
                </div>
            )}

            {/* Chat input */}
            <div className="chat-input">
                <textarea
                    ref={inputRef}
                    value={message}
                    onChange={(event) =>
                        setMessage(
                            event.target.value
                        )
                    }
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message..."
                    disabled={loading}
                    rows={1}
                />

                <div className="chat-input-actions">
                    <button
                        type="button"
                        className={`record-button ${
                            isRecording
                                ? "recording"
                                : ""
                        }`}
                        onClick={
                            isRecording
                                ? stopRecording
                                : startRecording
                        }
                        disabled={loading}
                        aria-pressed={isRecording}
                        style={{
                            transform:
                                isRecording
                                    ? `scale(${
                                        1 +
                                        (volumeLevel /
                                            100) *
                                        0.25
                                    })`
                                    : "scale(1)",
                            boxShadow:
                                isRecording
                                    ? `0 0 ${
                                        8 +
                                        volumeLevel *
                                        0.3
                                    }px rgba(239, 68, 68, 0.8)`
                                    : "none",
                        }}
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
                        onClick={() =>
                            void sendMessage()
                        }
                        disabled={
                            loading ||
                            message.trim() === ""
                        }
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