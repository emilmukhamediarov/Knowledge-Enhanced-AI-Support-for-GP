import { useEffect, useState } from "react";
import { NavLink, useParams } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./PatientDetails.css";

interface PatientDetails {
    id: number;
    name: string;
    date_of_birth: string | null;
    nationality: string | null;
    preferred_language: string | null;
    medical_history: string | null;
    allergies: string | null;
    medications: string | null;
}

interface PatientResponse {
    patients: PatientDetails[];
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

                const patientData =
                    await apiFetch("/users/me/patients") as PatientResponse;

                const foundPatient = patientData.patients.find(
                    (patient) => patient.id === Number(patientId)
                );

                if (!foundPatient) {
                    setError("Patient not found.");
                    return;
                }

                setPatient(foundPatient);

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
                            <span>Nationality</span>
                            <strong>
                                {patient.nationality || "Not provided"}
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
                </div>

                <div className="medical-info">
                    <div className="medical-info-section">
                        <span>Medical History</span>
                        <p>
                            {patient.medical_history ||
                                "No medical history provided."}
                        </p>
                    </div>

                    <div className="medical-info-section">
                        <span>Allergies</span>
                        <p>
                            {patient.allergies ||
                                "No allergies provided."}
                        </p>
                    </div>

                    <div className="medical-info-section">
                        <span>Medications</span>
                        <p>
                            {patient.medications ||
                                "No medications provided."}
                        </p>
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
                                <div
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
                                </div>
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