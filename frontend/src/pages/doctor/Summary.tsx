import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import "./Summary.css";

interface Information {
    status: string;
    items: string[];
}

interface SummaryData {
    consultation_id: number;
    reason_for_visit: string;
    symptoms: string[];
    symptom_location: string | null;
    onset: string | null;
    duration: string | null;
    severity: string | null;
    medical_history: Information;
    current_medications: Information;
    allergies: Information;
    additional_concerns: string | null;
    missing_information: string[];
    conversation_complete: boolean;
    summary: string;
}

function Summary() {
    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    // TEMPORARY: HARD-CODED CONSULTATION ID
    const consultationId = 1;

    useEffect(() => {
        const getSummary = async () => {
            // Check if we already have this consultation's summary
            const savedSummary = localStorage.getItem(
                `summary_${consultationId}`
            );

            if (savedSummary) {
                try {
                    const parsedSummary: SummaryData =
                        JSON.parse(savedSummary);

                    setSummary(parsedSummary);
                    setLoading(false);

                    return;
                } catch {
                    // If saved data is invalid, remove it
                    localStorage.removeItem(
                        `summary_${consultationId}`
                    );
                }
            }

            // No cached summary, so get it from the backend
            try {
                const data = await apiFetch(
                    `/consultations/${consultationId}/summary`
                );

                setSummary(data);

                // Save it for future visits
                localStorage.setItem(
                    `summary_${consultationId}`,
                    JSON.stringify(data)
                );
            } catch (error) {
                console.error("Summary error:", error);
                setError("Failed to load summary.");
            } finally {
                setLoading(false);
            }
        };

        getSummary();
    }, []);

    if (loading) {
        return <p>Loading summary...</p>;
    }

    if (error) {
        return <p>{error}</p>;
    }

    if (!summary) {
        return <p>No summary available.</p>;
    }

    return (
        <main>
            <h1>Patient Summary</h1>

            <div className="summary-box">

                <section className="summary-section">
                    <h2>Reason for Visit</h2>
                    <p>
                        {summary.reason_for_visit || "None provided"}
                    </p>
                </section>

                <section className="summary-section">
                    <h2>Symptoms</h2>

                    {summary.symptoms.length > 0 ? (
                        <ul>
                            {summary.symptoms.map((symptom, index) => (
                                <li key={index}>{symptom}</li>
                            ))}
                        </ul>
                    ) : (
                        <p>None provided.</p>
                    )}
                </section>

                <section className="summary-section">
                    <h2>Symptom Location</h2>
                    <p>
                        {summary.symptom_location || "None provided"}
                    </p>
                </section>

                <section className="summary-section">
                    <h2>Onset</h2>
                    <p>{summary.onset || "None provided"}</p>
                </section>

                <section className="summary-section">
                    <h2>Duration</h2>
                    <p>{summary.duration || "None provided"}</p>
                </section>

                <section className="summary-section">
                    <h2>Severity</h2>
                    <p>{summary.severity || "None provided"}</p>
                </section>

                <section className="summary-section">
                    <h2>Medical History</h2>

                    {summary.medical_history.items.length > 0 ? (
                        <ul>
                            {summary.medical_history.items.map(
                                (item, index) => (
                                    <li key={index}>{item}</li>
                                )
                            )}
                        </ul>
                    ) : (
                        <p>
                            {summary.medical_history.status ===
                            "confirmed_none"
                                ? "None reported."
                                : "Unknown."}
                        </p>
                    )}
                </section>

                <section className="summary-section">
                    <h2>Current Medications</h2>

                    {summary.current_medications.items.length > 0 ? (
                        <ul>
                            {summary.current_medications.items.map(
                                (medication, index) => (
                                    <li key={index}>{medication}</li>
                                )
                            )}
                        </ul>
                    ) : (
                        <p>
                            {summary.current_medications.status ===
                            "confirmed_none"
                                ? "None reported."
                                : "Unknown."}
                        </p>
                    )}
                </section>

                <section className="summary-section">
                    <h2>Allergies</h2>

                    {summary.allergies.items.length > 0 ? (
                        <ul>
                            {summary.allergies.items.map(
                                (allergy, index) => (
                                    <li key={index}>{allergy}</li>
                                )
                            )}
                        </ul>
                    ) : (
                        <p>
                            {summary.allergies.status ===
                            "confirmed_none"
                                ? "None reported."
                                : "Unknown."}
                        </p>
                    )}
                </section>

                <section className="summary-section">
                    <h2>Additional Concerns</h2>
                    <p>
                        {summary.additional_concerns ||
                            "None provided"}
                    </p>
                </section>

                <section className="summary-section">
                    <h2>Missing Information</h2>

                    {summary.missing_information.length > 0 ? (
                        <ul>
                            {summary.missing_information.map(
                                (item, index) => (
                                    <li key={index}>{item}</li>
                                )
                            )}
                        </ul>
                    ) : (
                        <p>None.</p>
                    )}
                </section>

                <section className="summary-section">
                    <h2>Conversation Status</h2>
                    <p>
                        {summary.conversation_complete
                            ? "Conversation complete"
                            : "Conversation incomplete"}
                    </p>
                </section>

                <section className="summary-section">
                    <h2>Summary</h2>
                    <p>{summary.summary}</p>
                </section>

            </div>
        </main>
    );
}

export default Summary;