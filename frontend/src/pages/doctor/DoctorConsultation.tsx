import { useEffect, useState } from "react";
import { NavLink, useNavigate, useParams } from "react-router-dom";
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
    const navigate = useNavigate();

    const [data, setData] = useState<RagData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [detailsOpen, setDetailsOpen] = useState(false);

    const [subjective, setSubjective] = useState("");
    const [objective, setObjective] = useState("");
    const [assessment, setAssessment] = useState("");
    const [plan, setPlan] = useState("");

    const [saving, setSaving] = useState(false);
    const [saveMessage, setSaveMessage] = useState("");

    const [showCloseConfirmation, setShowCloseConfirmation] =
        useState(false);
    const [closing, setClosing] = useState(false);
    const [closeError, setCloseError] = useState("");

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

                setSubjective(subjectiveResponse.subjective || "");
                setObjective(objectiveResponse.objective || "");
                setAssessment(assessmentResponse.assessment || "");
                setPlan(planResponse.plan || "");
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

    const closeConsultation = async () => {
        if (!consultationId) {
            return;
        }

        try {
            setClosing(true);
            setCloseError("");

            await apiFetch(
                `/consultations/${consultationId}/close`,
                {
                    method: "PATCH",
                }
            );

            setShowCloseConfirmation(false);

            navigate("/doctor/consultations");
        } catch (err) {
            console.error(
                "Failed to close consultation:",
                err
            );

            setCloseError(
                err instanceof Error
                    ? err.message
                    : "Failed to close consultation. Please try again."
            );
        } finally {
            setClosing(false);
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

                    <div className="consultation-header-actions">
                        <button
                            type="button"
                            className="close-button"
                            onClick={() => {
                                setCloseError("");
                                setShowCloseConfirmation(true);
                            }}
                            disabled={closing}
                        >
                            Close consultation
                        </button>
                    </div>
                </div>
            </div>

            <div className="reference-grid">
                <section className="reference-card">
                    <button
                        type="button"
                        className="reference-button"
                        onClick={() =>
                            setDetailsOpen((open) => !open)
                        }
                        aria-expanded={detailsOpen}
                    >
                        <div>
                            <span className="reference-label">
                                CLINICAL INSIGHTS
                            </span>

                            <h2>
                                Clinical Insights / Details
                            </h2>

                            {!detailsOpen && (
                                <p className="reference-preview">
                                    {rag.answer ||
                                        summary.summary ||
                                        "No clinical insights available."}
                                </p>
                            )}
                        </div>

                        <div className="reference-right">
                            <span className="reference-arrow">
                                {detailsOpen ? "" : ""}
                            </span>
                        </div>
                    </button>

                    {detailsOpen && (
                        <div className="reference-content">
                            <div className="summary-main">
                                <span className="field-label">
                                    Clinical insights
                                </span>

                                <p>
                                    {rag.answer ||
                                        "No clinical insights available."}
                                </p>
                            </div>

                            <div className="summary-grid">
                                <div className="summary-item">
                                    <span className="field-label">
                                        Reason for visit
                                    </span>

                                    <p>
                                        {summary.reason_for_visit ||
                                            "Not provided"}
                                    </p>
                                </div>

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
                            </div>
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

            {showCloseConfirmation && (
                <div className="confirmation-overlay">
                    <div
                        className="confirmation-popup"
                        role="dialog"
                        aria-modal="true"
                        aria-labelledby="close-consultation-title"
                    >
                        <div className="confirmation-icon">
                            !
                        </div>

                        <h2 id="close-consultation-title">
                            Close consultation?
                        </h2>

                        <p>
                            Are you sure you want to close this
                            consultation? Once closed, it will be
                            marked as completed.
                        </p>

                        {closeError && (
                            <p className="consultation-message error">
                                {closeError}
                            </p>
                        )}

                        <div className="confirmation-actions">
                            <button
                                type="button"
                                className="confirmation-cancel"
                                onClick={() => {
                                    setShowCloseConfirmation(false);
                                    setCloseError("");
                                }}
                                disabled={closing}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="confirmation-confirm"
                                onClick={closeConsultation}
                                disabled={closing}
                            >
                                {closing
                                    ? "Closing..."
                                    : "Close consultation"}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}

export default DoctorConsultation;