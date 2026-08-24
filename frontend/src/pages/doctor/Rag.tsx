import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import "./Rag.css";

interface PatientSummary {
    consultation_id: number;
    reason_for_visit: string | null;
    symptoms: string[];
    symptom_location: string | null;
    onset: string | null;
    duration: string | null;
    severity: string | null;
    medical_history: {
        status: string;
        items: string[];
    };
    current_medications: {
        status: string;
        items: string[];
    };
    allergies: {
        status: string;
        items: string[];
    };
    additional_concerns: string | null;
    missing_information: string[];
    conversation_complete: boolean;
    summary: string;
}

interface RagResponse {
    answer: string;
    red_flags_identified: string[];
    requires_urgent_attention: boolean;
    sources: string[];
    parse_error: boolean;
}

interface RagData {
    patient_summary: PatientSummary;
    rag_response: RagResponse;
}

function Rag() {
    const [ragData, setRagData] = useState<RagData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // TEMPORARY: hard-coded consultation ID
    const consultationId = 1;

    useEffect(() => {
        const getRag = async () => {
            const cacheKey = `rag_${consultationId}`;

            // Check localStorage first
            const savedRag = localStorage.getItem(cacheKey);

            if (savedRag) {
                try {
                    const parsedRag: RagData = JSON.parse(savedRag);

                    setRagData(parsedRag);
                    setLoading(false);

                    return;
                } catch {
                    // Invalid cached data
                    localStorage.removeItem(cacheKey);
                }
            }

            // No cached RAG, get it from backend
            try {
                const data = await apiFetch(
                    `/consultations/${consultationId}/rag`
                );

                setRagData(data);

                // Save RAG result for future visits
                localStorage.setItem(
                    cacheKey,
                    JSON.stringify(data)
                );
            } catch (error) {
                console.error("RAG error:", error);
                setError("Failed to load RAG.");
            } finally {
                setLoading(false);
            }
        };

        getRag();
    }, []);

    if (loading) {
        return (
            <main className="rag-page">
                <h1>RAG Results</h1>
                <p>Loading...</p>
            </main>
        );
    }

    if (error) {
        return (
            <main className="rag-page">
                <h1>RAG Results</h1>
                <p className="rag-error">{error}</p>
            </main>
        );
    }

    if (!ragData) {
        return (
            <main className="rag-page">
                <h1>RAG Results</h1>
                <p>No RAG results available.</p>
            </main>
        );
    }

    const patient = ragData.patient_summary;
    const rag = ragData.rag_response;

    return (
        <main className="rag-page">
            <h1>RAG Results</h1>

            <div className="rag-columns">

                {/* LEFT: PATIENT SUMMARY */}
                <section className="rag-section">
                    <h2>Patient Summary</h2>

                    <div className="rag-details">

                        <div className="rag-field">
                            <strong>Reason for visit</strong>
                            <p>
                                {patient.reason_for_visit ||
                                    "Not provided"}
                            </p>
                        </div>

                        <div className="rag-field">
                            <strong>Symptoms</strong>

                            {patient.symptoms.length > 0 ? (
                                <ul>
                                    {patient.symptoms.map(
                                        (symptom, index) => (
                                            <li key={index}>
                                                {symptom}
                                            </li>
                                        )
                                    )}
                                </ul>
                            ) : (
                                <p>None reported</p>
                            )}
                        </div>

                        <div className="rag-field">
                            <strong>Symptom location</strong>
                            <p>
                                {patient.symptom_location ||
                                    "Not provided"}
                            </p>
                        </div>

                        <div className="rag-field">
                            <strong>Onset</strong>
                            <p>
                                {patient.onset || "Not provided"}
                            </p>
                        </div>

                        <div className="rag-field">
                            <strong>Duration</strong>
                            <p>
                                {patient.duration || "Not provided"}
                            </p>
                        </div>

                        <div className="rag-field">
                            <strong>Severity</strong>
                            <p>
                                {patient.severity || "Not provided"}
                            </p>
                        </div>

                        <div className="rag-field">
                            <strong>Medical history</strong>

                            <p>
                                Status:{" "}
                                {patient.medical_history.status}
                            </p>

                            {patient.medical_history.items.length > 0 && (
                                <ul>
                                    {patient.medical_history.items.map(
                                        (item, index) => (
                                            <li key={index}>
                                                {item}
                                            </li>
                                        )
                                    )}
                                </ul>
                            )}
                        </div>

                        <div className="rag-field">
                            <strong>Current medications</strong>

                            <p>
                                Status:{" "}
                                {patient.current_medications.status}
                            </p>

                            {patient.current_medications.items.length > 0 && (
                                <ul>
                                    {patient.current_medications.items.map(
                                        (item, index) => (
                                            <li key={index}>
                                                {item}
                                            </li>
                                        )
                                    )}
                                </ul>
                            )}
                        </div>

                        <div className="rag-field">
                            <strong>Allergies</strong>

                            <p>
                                Status: {patient.allergies.status}
                            </p>

                            {patient.allergies.items.length > 0 && (
                                <ul>
                                    {patient.allergies.items.map(
                                        (item, index) => (
                                            <li key={index}>
                                                {item}
                                            </li>
                                        )
                                    )}
                                </ul>
                            )}
                        </div>

                        <div className="rag-field">
                            <strong>Additional concerns</strong>

                            <p>
                                {patient.additional_concerns ||
                                    "None provided"}
                            </p>
                        </div>

                        <div className="rag-field">
                            <strong>Missing information</strong>

                            {patient.missing_information.length > 0 ? (
                                <ul>
                                    {patient.missing_information.map(
                                        (item, index) => (
                                            <li key={index}>
                                                {item}
                                            </li>
                                        )
                                    )}
                                </ul>
                            ) : (
                                <p>None</p>
                            )}
                        </div>

                        <div className="rag-field">
                            <strong>Conversation complete</strong>

                            <p>
                                {patient.conversation_complete
                                    ? "Yes"
                                    : "No"}
                            </p>
                        </div>

                        <div className="rag-field rag-summary">
                            <strong>Summary</strong>
                            <p>{patient.summary}</p>
                        </div>

                    </div>
                </section>


                {/* RIGHT: RAG RESPONSE */}
                <section className="rag-section">
                    <h2>RAG Response</h2>

                    <div className="rag-field">
                        <strong>Answer</strong>
                        <p>{rag.answer}</p>
                    </div>

                    <div className="rag-field">
                        <strong>Red flags identified</strong>

                        {rag.red_flags_identified.length > 0 ? (
                            <ul>
                                {rag.red_flags_identified.map(
                                    (redFlag, index) => (
                                        <li key={index}>
                                            {redFlag}
                                        </li>
                                    )
                                )}
                            </ul>
                        ) : (
                            <p>No red flags identified.</p>
                        )}
                    </div>

                    <div className="rag-field">
                        <strong>Requires urgent attention</strong>

                        <p>
                            {rag.requires_urgent_attention
                                ? "Yes"
                                : "No"}
                        </p>
                    </div>

                </section>

            </div>


            {/* SOURCES */}
            <section className="rag-section rag-sources-section">
                <details className="rag-sources">
                    <summary>Sources</summary>

                    <div className="sources-content">
                        {rag.sources.map((source, index) => (
                            <div
                                key={index}
                                className="source"
                            >
                                <pre>{source}</pre>
                            </div>
                        ))}
                    </div>
                </details>
            </section>

        </main>
    );
}

export default Rag;