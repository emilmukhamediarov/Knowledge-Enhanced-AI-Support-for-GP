import { useEffect, useState } from "react";
import { NavLink, useParams } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./DoctorConsultation.css";

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
    summary: string | null;
}

interface RagResponse {
    answer: string;
    red_flags_identified: string[];
    requires_urgent_attention: boolean;
    confidence: string;
    confidence_message: string;
    sources: string[];
    parse_error: boolean;
}

interface RagData {
    patient_summary: PatientSummary;
    rag_response: RagResponse;
}

interface SubjectiveResponse {
    subjective: string | null;
}

interface ObjectiveResponse {
    objective: string | null;
}

interface AssessmentResponse {
    assessment: string | null;
}

interface PlanResponse {
    plan: string | null;
}

function DoctorConsultation() {
    const { consultationId } = useParams();

    const [data, setData] = useState<RagData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [summaryOpen, setSummaryOpen] = useState(false);
    const [ragOpen, setRagOpen] = useState(false);

    const [subjective, setSubjective] = useState("");
    const [objective, setObjective] = useState("");
    const [assessment, setAssessment] = useState("");
    const [plan, setPlan] = useState("");

    const [saving, setSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState("");

    useEffect(() => {
        const fetchConsultation = async () => {
            if (!consultationId) {
                setError("Invalid consultation.");
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError("");

                const ragResponse = await apiFetch(
                    `/consultations/${consultationId}/rag`
                ) as RagData;

                setData(ragResponse);

                const [
                    subjectiveResponse,
                    objectiveResponse,
                    assessmentResponse,
                    planResponse,
                ] = await Promise.all([
                    apiFetch(
                        `/consultations/${consultationId}/subjective`
                    ) as Promise<SubjectiveResponse>,

                    apiFetch(
                        `/consultations/${consultationId}/objective`
                    ) as Promise<ObjectiveResponse>,

                    apiFetch(
                        `/consultations/${consultationId}/assessment`
                    ) as Promise<AssessmentResponse>,

                    apiFetch(
                        `/consultations/${consultationId}/plan`
                    ) as Promise<PlanResponse>,
                ]);

                setSubjective(
                    subjectiveResponse.subjective || ""
                );

                setObjective(
                    objectiveResponse.objective || ""
                );

                setAssessment(
                    assessmentResponse.assessment || ""
                );

                setPlan(
                    planResponse.plan || ""
                );
            } catch (err) {
                console.error(
                    "Failed to fetch consultation:",
                    err
                );

                setError("Unable to load consultation.");
            } finally {
                setLoading(false);
            }
        };

        fetchConsultation();
    }, [consultationId]);

    const saveNotes = async () => {
        if (!consultationId) {
            return;
        }

        try {
            setSaving(true);
            setSaveMessage("");

            await Promise.all([
                apiFetch(
                    `/consultations/${consultationId}/subjective`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            subjective,
                        }),
                    }
                ),

                apiFetch(
                    `/consultations/${consultationId}/objective`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            objective,
                        }),
                    }
                ),

                apiFetch(
                    `/consultations/${consultationId}/assessment`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            assessment,
                        }),
                    }
                ),

                apiFetch(
                    `/consultations/${consultationId}/plan`,
                    {
                        method: "PATCH",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            plan,
                        }),
                    }
                ),
            ]);

            setSaveMessage("Notes saved successfully.");
        } catch (err) {
            console.error(
                "Failed to save clinical notes:",
                err
            );

            setSaveMessage(
                "Failed to save notes. Please try again."
            );
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <main className="doctor-consultation-page">
                <div className="consultation-message">
                    Loading consultation...
                </div>
            </main>
        );
    }

    if (error || !data) {
        return (
            <main className="doctor-consultation-page">
                <div className="consultation-message error">
                    {error || "Consultation not found."}
                </div>
            </main>
        );
    }

    const summary = data.patient_summary;
    const rag = data.rag_response;

    return (
        <main className="doctor-consultation-page">
            <div className="consultation-header">
                <NavLink
                    to="/doctor/consultations"
                    className="back-link"
                >
                    ← Back to consultations
                </NavLink>

                <div className="consultation-header-row">
                    <div>
                        <h1>
                            Consultation #{summary.consultation_id}
                        </h1>
                    </div>

                    <span className="consultation-status">
                        Active
                    </span>
                </div>
            </div>

            <div className="reference-grid">
                <section className="reference-card">
                    <button
                        type="button"
                        className="reference-button"
                        onClick={() =>
                            setSummaryOpen((open) => !open)
                        }
                        aria-expanded={summaryOpen}
                    >
                        <div>
                            <span className="reference-label">
                                CHAT SUMMARY
                            </span>

                            <h2>
                                {summary.reason_for_visit ||
                                    "Patient summary"}
                            </h2>

                            {!summaryOpen && (
                                <p className="reference-preview">
                                    {summary.summary ||
                                        "No summary available."}
                                </p>
                            )}
                        </div>

                        <span className="reference-arrow">
                            {summaryOpen ? "" : ""}
                        </span>
                    </button>

                    {summaryOpen && (
                        <div className="reference-content">
                            <div className="summary-main">
                                <span className="field-label">
                                    Summary
                                </span>

                                <p>
                                    {summary.summary ||
                                        "No summary available."}
                                </p>
                            </div>

                            <div className="summary-grid">
                                <div className="summary-item">
                                    <span className="field-label">
                                        Symptoms
                                    </span>

                                    {summary.symptoms.length > 0 ? (
                                        <ul>
                                            {summary.symptoms.map(
                                                (symptom, index) => (
                                                    <li key={index}>
                                                        {symptom}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    ) : (
                                        <p>None provided</p>
                                    )}
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Location
                                    </span>

                                    <p>
                                        {summary.symptom_location ||
                                            "Not provided"}
                                    </p>
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Onset
                                    </span>

                                    <p>
                                        {summary.onset ||
                                            "Not provided"}
                                    </p>
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Duration
                                    </span>

                                    <p>
                                        {summary.duration ||
                                            "Not provided"}
                                    </p>
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Severity
                                    </span>

                                    <p>
                                        {summary.severity ||
                                            "Not provided"}
                                    </p>
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Additional concerns
                                    </span>

                                    <p>
                                        {summary.additional_concerns ||
                                            "None provided"}
                                    </p>
                                </div>
                            </div>

                            <div className="summary-grid">
                                <div className="summary-item">
                                    <span className="field-label">
                                        Medical history
                                    </span>

                                    {summary.medical_history.items.length >
                                    0 ? (
                                        <ul>
                                            {summary.medical_history.items.map(
                                                (item, index) => (
                                                    <li key={index}>
                                                        {item}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    ) : (
                                        <p>
                                            {
                                                summary.medical_history
                                                    .status
                                            }
                                        </p>
                                    )}
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Medications
                                    </span>

                                    {summary.current_medications.items.length >
                                    0 ? (
                                        <ul>
                                            {summary.current_medications.items.map(
                                                (item, index) => (
                                                    <li key={index}>
                                                        {item}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    ) : (
                                        <p>
                                            {
                                                summary.current_medications
                                                    .status
                                            }
                                        </p>
                                    )}
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Allergies
                                    </span>

                                    {summary.allergies.items.length >
                                    0 ? (
                                        <ul>
                                            {summary.allergies.items.map(
                                                (item, index) => (
                                                    <li key={index}>
                                                        {item}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    ) : (
                                        <p>
                                            {summary.allergies.status}
                                        </p>
                                    )}
                                </div>

                                <div className="summary-item">
                                    <span className="field-label">
                                        Missing information
                                    </span>

                                    {summary.missing_information.length >
                                    0 ? (
                                        <ul>
                                            {summary.missing_information.map(
                                                (item, index) => (
                                                    <li key={index}>
                                                        {item}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    ) : (
                                        <p>
                                            No missing information
                                        </p>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </section>

                <section className="reference-card">
                    <button
                        type="button"
                        className="reference-button"
                        onClick={() =>
                            setRagOpen((open) => !open)
                        }
                        aria-expanded={ragOpen}
                    >
                        <div>
                            <span className="reference-label">
                                RAG
                            </span>

                            <h2>
                                Clinical Insights
                            </h2>

                            {!ragOpen && (
                                <p className="reference-preview">
                                    {rag.answer ||
                                        "No RAG output available."}
                                </p>
                            )}
                        </div>

                        <div className="reference-right">
                            <span className="reference-arrow">
                                {ragOpen ? "" : ""}
                            </span>
                        </div>
                    </button>

                    {ragOpen && (
                        <div className="reference-content">
                            <div className="rag-answer">
                                <span className="field-label">
                                    Clinical summary
                                </span>

                                <p>
                                    {rag.answer ||
                                        "No clinical summary available."}
                                </p>
                            </div>

                            <div className="rag-grid">
                                <div className="rag-item">
                                    <span className="field-label">
                                        Symptoms identified
                                    </span>

                                    {rag.red_flags_identified.length >
                                    0 ? (
                                        <ul className="red-flags">
                                            {rag.red_flags_identified.map(
                                                (flag, index) => (
                                                    <li key={index}>
                                                        {flag}
                                                    </li>
                                                )
                                            )}
                                        </ul>
                                    ) : (
                                        <p>
                                            None identified
                                        </p>
                                    )}
                                </div>

                                <div className="rag-item">
                                    <span className="field-label">
                                        Confidence
                                    </span>

                                    <p>
                                        {rag.confidence}
                                    </p>
                                </div>
                            </div>

                            {rag.confidence_message && (
                                <div className="rag-confidence">
                                    <span className="field-label">
                                        Confidence explanation
                                    </span>

                                    <p>
                                        {rag.confidence_message}
                                    </p>
                                </div>
                            )}

                            {rag.sources.length > 0 && (
                                <details className="rag-sources">
                                    <summary>
                                        Sources
                                    </summary>

                                    <div>
                                        {rag.sources.map(
                                            (source, index) => (
                                                <pre key={index}>
                                                    {source}
                                                </pre>
                                            )
                                        )}
                                    </div>
                                </details>
                            )}
                        </div>
                    )}
                </section>
            </div>

            <section className="clinical-notes">
                <div className="section-heading">
                    <div>
                        <span className="section-label">
                            CLINICAL NOTES
                        </span>

                        <h2>
                            Clinical Documentation
                        </h2>

                        <p>
                            Record your findings, assessment,
                            and treatment plan.
                        </p>
                    </div>
                </div>

                <div className="soap-grid">
                    <div className="soap-section">
                        <div className="soap-title">
                            <span>S</span>

                            <div>
                                <h3>Subjective</h3>
                                <p>
                                    Patient-reported information
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={subjective}
                            onChange={(event) =>
                                setSubjective(event.target.value)
                            }
                            placeholder="Document the patient's symptoms, concerns, and relevant history..."
                        />
                    </div>

                    <div className="soap-section">
                        <div className="soap-title">
                            <span>O</span>

                            <div>
                                <h3>Objective</h3>
                                <p>
                                    Findings and measurements
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={objective}
                            onChange={(event) =>
                                setObjective(event.target.value)
                            }
                            placeholder="Document observations, examination findings, and vital signs..."
                        />
                    </div>

                    <div className="soap-section">
                        <div className="soap-title">
                            <span>A</span>

                            <div>
                                <h3>Assessment</h3>
                                <p>
                                    Clinical assessment
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={assessment}
                            onChange={(event) =>
                                setAssessment(event.target.value)
                            }
                            placeholder="Document your clinical assessment and diagnosis..."
                        />
                    </div>

                    <div className="soap-section">
                        <div className="soap-title">
                            <span>P</span>

                            <div>
                                <h3>Plan</h3>
                                <p>
                                    Treatment and follow-up
                                </p>
                            </div>
                        </div>

                        <textarea
                            value={plan}
                            onChange={(event) =>
                                setPlan(event.target.value)
                            }
                            placeholder="Document treatment, medications, follow-up, and patient instructions..."
                        />
                    </div>
                </div>
            </section>

            <div className="consultation-footer">
                {saveMessage && (
                    <span className="save-message">
                        {saveMessage}
                    </span>
                )}

                <button
                    type="button"
                    className="save-button"
                    onClick={saveNotes}
                    disabled={saving}
                >
                    {saving ? "Saving..." : "Save notes"}
                </button>
            </div>
        </main>
    );
}

export default DoctorConsultation;