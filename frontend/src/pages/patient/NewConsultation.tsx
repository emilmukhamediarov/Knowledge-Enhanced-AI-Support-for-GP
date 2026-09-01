import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./NewConsultation.css";

interface Consultation {
    id: number;
    created_at: string;
}

function NewConsultation() {
    const navigate = useNavigate();

    const [relatedToPrevious, setRelatedToPrevious] =
        useState<boolean | null>(null);

    const [consultations, setConsultations] =
        useState<Consultation[]>([]);

    const [selectedConsultation, setSelectedConsultation] =
        useState("");

    const [loadingConsultations, setLoadingConsultations] =
        useState(false);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // Temporary until authentication is properly connected
    const storedUserId = localStorage.getItem("userId");
    const userId = storedUserId
        ? Number(storedUserId)
        : null;

    useEffect(() => {
        const loadConsultations = async () => {
            if (
                userId === null ||
                Number.isNaN(userId)
            ) {
                setError(
                    "Unable to identify the current user."
                );
                return;
            }

            setLoadingConsultations(true);
            setError("");

            try {
                const data = await apiFetch(
                    `/consultations/users/${userId}/consultations`
                );

                setConsultations(data.consultations);
            } catch (error) {
                console.error(
                    "Failed to load consultations:",
                    error
                );

                setError(
                    "Failed to load previous consultations."
                );
            } finally {
                setLoadingConsultations(false);
            }
        };

        if (relatedToPrevious === true) {
            void loadConsultations();
        }
    }, [relatedToPrevious, userId]);

    const startConsultation = async () => {
        if (
            userId === null ||
            Number.isNaN(userId)
        ) {
            setError(
                "Unable to identify the current user."
            );
            return;
        }

        if (
            relatedToPrevious === true &&
            !selectedConsultation
        ) {
            setError(
                "Please select a previous consultation."
            );
            return;
        }

        setLoading(true);
        setError("");

        try {
            const data = await apiFetch(
                "/consultations",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        previous_consultation_id:
                            relatedToPrevious
                                ? Number(
                                    selectedConsultation
                                )
                                : null,
                    }),
                }
            );

            navigate(`/chat/${data.consultation_id}`);
        } catch (error) {
            console.error(
                "Failed to create consultation:",
                error
            );

            setError(
                "Failed to start consultation."
            );
        } finally {
            setLoading(false);
        }
    };

    const canStart =
        relatedToPrevious === false ||
        (
            relatedToPrevious === true &&
            selectedConsultation !== ""
        );

    return (
        <main className="new-consultation">
            <div className="new-consultation-container">

                <header className="consultation-header">
                    <h1>Start a New Consultation</h1>

                    <p>
                        Is this consultation related to a
                        previous issue?
                    </p>
                </header>

                <section className="consultation-section">
                    <div className="consultation-options">

                        <button
                            type="button"
                            className={`consultation-option ${
                                relatedToPrevious === false
                                    ? "selected"
                                    : ""
                            }`}
                            onClick={() => {
                                setRelatedToPrevious(false);
                                setSelectedConsultation("");
                                setError("");
                            }}
                        >
                            <span className="option-title">
                                No
                            </span>

                            <span className="option-description">
                                This is a new issue
                            </span>
                        </button>

                        <button
                            type="button"
                            className={`consultation-option ${
                                relatedToPrevious === true
                                    ? "selected"
                                    : ""
                            }`}
                            onClick={() => {
                                setRelatedToPrevious(true);
                                setError("");
                            }}
                        >
                            <span className="option-title">
                                Yes
                            </span>

                            <span className="option-description">
                                This is related to a
                                previous issue
                            </span>
                        </button>

                    </div>
                </section>

                {relatedToPrevious === true && (
                    <section className="consultation-section previous-consultation">
                        <div className="section-heading">
                            <h2>
                                Previous consultation
                            </h2>

                            <p>
                                Select the consultation you
                                would like to continue from.
                            </p>
                        </div>

                        {loadingConsultations ? (
                            <p className="no-consultations">
                                Loading previous
                                consultations...
                            </p>
                        ) : consultations.length === 0 ? (
                            <p className="no-consultations">
                                You have no previous
                                consultations.
                            </p>
                        ) : (
                            <>
                                <label htmlFor="previous-consultation">
                                    Consultation
                                </label>

                                <select
                                    id="previous-consultation"
                                    value={
                                        selectedConsultation
                                    }
                                    onChange={(event) => {
                                        setSelectedConsultation(
                                            event.target.value
                                        );
                                        setError("");
                                    }}
                                >
                                    <option value="">
                                        Select a consultation
                                    </option>

                                    {consultations.map(
                                        (consultation) => (
                                            <option
                                                key={
                                                    consultation.id
                                                }
                                                value={String(
                                                    consultation.id
                                                )}
                                            >
                                                Consultation #
                                                {
                                                    consultation.id
                                                }{" "}
                                                —{" "}
                                                {new Date(
                                                    consultation.created_at
                                                ).toLocaleDateString()}
                                            </option>
                                        )
                                    )}
                                </select>
                            </>
                        )}
                    </section>
                )}

                {error && (
                    <div
                        className="consultation-error"
                        role="alert"
                    >
                        {error}
                    </div>
                )}

                {relatedToPrevious !== null && (
                    <button
                        type="button"
                        className="start-consultation-button"
                        onClick={startConsultation}
                        disabled={
                            loading ||
                            !canStart ||
                            userId === null
                        }
                    >
                        {loading
                            ? "Starting..."
                            : "Start Consultation"}
                    </button>
                )}

            </div>
        </main>
    );
}

export default NewConsultation;