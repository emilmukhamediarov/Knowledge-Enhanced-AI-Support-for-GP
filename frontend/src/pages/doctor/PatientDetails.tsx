import { useEffect, useState } from "react";
import { NavLink, useParams } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./PatientDetails.css";

interface PatientDetails {
    id: number;
    username: string;
    name: string;
    email: string;
    date_of_birth: string | null;
    age: number;
    preferred_language: string | null;
    ethnicity: string | null;
    medical_history: string | null;
    allergies?: string[] | null;
    medications?: string[] | null;
}

interface Consultation {
    consultation_id: number;
    status: string;
    created_at: string;
    closed_at: string | null;
}

interface ConsultationResponse {
    user_id: number;
    consultations: Consultation[];
}

function PatientDetails() {
    const { patientId } = useParams<{ patientId: string }>();

    const [patient, setPatient] = useState<PatientDetails | null>(null);
    const [consultations, setConsultations] = useState<Consultation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [editingMedical, setEditingMedical] = useState(false);
    const [medicalHistory, setMedicalHistory] = useState("");
    const [allergies, setAllergies] = useState("");
    const [medications, setMedications] = useState("");
    const [savingMedical, setSavingMedical] = useState(false);
    const [medicalError, setMedicalError] = useState("");

    useEffect(() => {
        const fetchPatient = async () => {
            if (!patientId) {
                setError("Invalid patient.");
                setLoading(false);
                return;
            }

            try {
                setLoading(true);
                setError("");

                const foundPatient =
                    await apiFetch(
                        `/users/patients/${patientId}`
                    ) as PatientDetails;

                setPatient(foundPatient);

                setMedicalHistory(foundPatient.medical_history || "");

                setAllergies(
                    Array.isArray(foundPatient.allergies)
                        ? foundPatient.allergies.join("\n")
                        : ""
                );

                setMedications(
                    Array.isArray(foundPatient.medications)
                        ? foundPatient.medications.join("\n")
                        : ""
                );

                try {
                    const consultationData =
                        await apiFetch(
                            `/consultations/user/${patientId}`
                        ) as ConsultationResponse;

                    setConsultations(consultationData.consultations);
                } catch (err) {
                    console.error(
                        "Failed to fetch patient consultations:",
                        err
                    );
                }
            } catch (err) {
                console.error("Failed to fetch patient:", err);
                setError("Unable to load patient.");
            } finally {
                setLoading(false);
            }
        };

        fetchPatient();
    }, [patientId]);

    const startEditingMedical = () => {
        if (!patient) {
            return;
        }

        setMedicalHistory(patient.medical_history || "");

        setAllergies(
            Array.isArray(patient.allergies)
                ? patient.allergies.join("\n")
                : ""
        );

        setMedications(
            Array.isArray(patient.medications)
                ? patient.medications.join("\n")
                : ""
        );

        setMedicalError("");
        setEditingMedical(true);
    };

    const cancelEditingMedical = () => {
        if (!patient) {
            return;
        }

        setMedicalHistory(patient.medical_history || "");

        setAllergies(
            Array.isArray(patient.allergies)
                ? patient.allergies.join("\n")
                : ""
        );

        setMedications(
            Array.isArray(patient.medications)
                ? patient.medications.join("\n")
                : ""
        );

        setMedicalError("");
        setEditingMedical(false);
    };

    const saveMedicalInformation = async () => {
        if (!patientId || !patient) {
            return;
        }

        try {
            setSavingMedical(true);
            setMedicalError("");

            const updatedMedicalInformation = {
                medical_history: medicalHistory.trim(),
                allergies: allergies
                    .split("\n")
                    .map((item) => item.trim())
                    .filter((item) => item.length > 0),
                medications: medications
                    .split("\n")
                    .map((item) => item.trim())
                    .filter((item) => item.length > 0),
            };

            await apiFetch(
                `/users/patients/${patientId}`,
                {
                    method: "PATCH",
                    body: JSON.stringify(updatedMedicalInformation),
                }
            );

            setPatient({
                ...patient,
                medical_history:
                    updatedMedicalInformation.medical_history || null,
                allergies: updatedMedicalInformation.allergies,
                medications: updatedMedicalInformation.medications,
            });

            setEditingMedical(false);
        } catch (err) {
            console.error(
                "Failed to update patient medical information:",
                err
            );

            setMedicalError(
                "Unable to save medical information. Please try again."
            );
        } finally {
            setSavingMedical(false);
        }
    };

    if (loading) {
        return (
            <main className="doctor-page patient-details-page">
                <div className="patient-details-empty">
                    Loading patient...
                </div>
            </main>
        );
    }

    if (error || !patient) {
        return (
            <main className="doctor-page patient-details-page">
                <NavLink
                    to="/doctor/patients"
                    className="patient-back"
                >
                    ← Patients
                </NavLink>

                <div className="patient-details-empty">
                    {error || "Patient not found."}
                </div>
            </main>
        );
    }

    const latestConsultation =
        consultations.length > 0
            ? consultations.reduce((latest, current) =>
                new Date(current.created_at) >
                new Date(latest.created_at)
                    ? current
                    : latest
            )
            : null;

    return (
        <main className="doctor-page patient-details-page">
            <div className="patient-details-header">
                <div>
                    <NavLink
                        to="/doctor/patients"
                        className="patient-back"
                    >
                        ← Patients
                    </NavLink>

                    <div className="patient-title-row">
                        <div className="patient-avatar">
                            {patient.name.charAt(0).toUpperCase()}
                        </div>

                        <div>
                            <h1>{patient.name}</h1>
                            <p>Patient #{patient.id}</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="patient-details-grid">
                <section className="patient-details-card">
                    <div className="patient-card-header">
                        <h2>Patient Information</h2>
                    </div>

                    <div className="patient-info-grid">
                        <div className="patient-info-item">
                            <span>Date of Birth</span>
                            <strong>
                                {patient.date_of_birth
                                    ? formatDate(patient.date_of_birth)
                                    : "Not provided"}
                            </strong>
                        </div>

                        <div className="patient-info-item">
                            <span>Ethnicity</span>
                            <strong>
                                {patient.ethnicity || "Not provided"}
                            </strong>
                        </div>

                        <div className="patient-info-item">
                            <span>Preferred Language</span>
                            <strong>
                                {patient.preferred_language ||
                                    "Not provided"}
                            </strong>
                        </div>

                        <div className="patient-info-item">
                            <span>Patient ID</span>
                            <strong>#{patient.id}</strong>
                        </div>
                    </div>
                </section>

                <section className="patient-details-card">
                    <div className="patient-card-header">
                        <h2>Consultation Summary</h2>
                    </div>

                    <div className="patient-summary-grid">
                        <div className="patient-summary-item">
                            <span>Total Consultations</span>
                            <strong>{consultations.length}</strong>
                        </div>

                        <div className="patient-summary-item">
                            <span>Last Consultation</span>
                            <strong>
                                {latestConsultation
                                    ? formatDate(
                                        latestConsultation.created_at
                                    )
                                    : "None"}
                            </strong>
                        </div>
                    </div>
                </section>
            </div>

            <section className="patient-details-card medical-card">
                <div className="patient-card-header">
                    <h2>Medical Information</h2>

                    {!editingMedical ? (
                        <button
                            type="button"
                            className="medical-edit-button"
                            onClick={startEditingMedical}
                        >
                            Edit
                        </button>
                    ) : (
                        <div className="medical-actions">
                            <button
                                type="button"
                                className="medical-cancel-button"
                                onClick={cancelEditingMedical}
                                disabled={savingMedical}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="medical-save-button"
                                onClick={saveMedicalInformation}
                                disabled={savingMedical}
                            >
                                {savingMedical ? "Saving..." : "Save"}
                            </button>
                        </div>
                    )}
                </div>

                {medicalError && (
                    <div className="medical-error">
                        {medicalError}
                    </div>
                )}

                <div className="medical-info">
                    <div className="medical-info-section">
                        <span>Medical History</span>

                        {editingMedical ? (
                            <textarea
                                value={medicalHistory}
                                onChange={(e) =>
                                    setMedicalHistory(e.target.value)
                                }
                                placeholder="Enter medical history"
                            />
                        ) : (
                            <p>
                                {patient.medical_history ||
                                    "No medical history provided."}
                            </p>
                        )}
                    </div>

                    <div className="medical-info-section">
                        <span>Allergies</span>

                        {editingMedical ? (
                            <textarea
                                value={allergies}
                                onChange={(e) =>
                                    setAllergies(e.target.value)
                                }
                                placeholder="Enter one allergy per line"
                            />
                        ) : (
                            <p>
                                {Array.isArray(patient.allergies) &&
                                patient.allergies.length > 0
                                    ? patient.allergies.join(", ")
                                    : "No allergies provided."}
                            </p>
                        )}
                    </div>

                    <div className="medical-info-section">
                        <span>Medications</span>

                        {editingMedical ? (
                            <textarea
                                value={medications}
                                onChange={(e) =>
                                    setMedications(e.target.value)
                                }
                                placeholder="Enter one medication per line"
                            />
                        ) : (
                            <p>
                                {Array.isArray(patient.medications) &&
                                patient.medications.length > 0
                                    ? patient.medications.join(", ")
                                    : "No medications provided."}
                            </p>
                        )}
                    </div>
                </div>
            </section>

            <section className="patient-details-card consultations-card">
                <div className="patient-card-header">
                    <h2>Consultation History</h2>
                </div>

                {consultations.length === 0 ? (
                    <div className="patient-details-empty">
                        No consultations yet.
                    </div>
                ) : (
                    <div className="patient-consultations-list">
                        {consultations
                            .sort(
                                (a, b) =>
                                    new Date(b.created_at).getTime() -
                                    new Date(a.created_at).getTime()
                            )
                            .map((consultation) => (
                                <NavLink
                                    to={`/doctor/consultations/${consultation.consultation_id}`}
                                    className="patient-consultation-row"
                                    key={consultation.consultation_id}
                                >
                                    <div className="consultation-main">
                                        <strong>
                                            #{consultation.consultation_id}
                                        </strong>

                                        <span>
                                            {formatDate(
                                                consultation.created_at
                                            )}
                                        </span>
                                    </div>

                                    <span
                                        className={`consultation-status ${consultation.status.toLowerCase()}`}
                                    >
                                        {consultation.status}
                                    </span>
                                </NavLink>
                            ))}
                    </div>
                )}
            </section>
        </main>
    );
}

function formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString("en-NZ", {
        day: "numeric",
        month: "short",
        year: "numeric",
    });
}

export default PatientDetails;