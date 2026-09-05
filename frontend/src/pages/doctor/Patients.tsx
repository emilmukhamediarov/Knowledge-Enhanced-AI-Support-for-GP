import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import "./Patients.css";
import { apiFetch } from "../../api/client";

interface Patient {
    id: number;
    name: string;
    lastConsultation: string;
    consultationCount: number;
}

interface PatientResponse {
    patients: {
        id: number;
        name: string;
        date_of_birth: string | null;
        nationality: string | null;
    }[];
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

function Patients() {
    const [search, setSearch] = useState("");
    const [patients, setPatients] = useState<Patient[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const patientsPerPage = 10;

    useEffect(() => {
        const fetchPatients = async () => {
            try {
                setLoading(true);
                setError("");

                const patientData =
                    await apiFetch("/users/me/patients") as PatientResponse;

                const patientsWithConsultations = await Promise.all(
                    patientData.patients.map(async (patient) => {
                        try {
                            const consultationData =
                                await apiFetch(
                                    `/consultations/user/${patient.id}`
                                ) as ConsultationResponse;

                            const consultations =
                                consultationData.consultations;

                            const latestConsultation =
                                consultations.length > 0
                                    ? consultations.reduce(
                                        (latest, current) =>
                                            new Date(current.created_at) >
                                            new Date(latest.created_at)
                                                ? current
                                                : latest
                                    )
                                    : null;

                            return {
                                id: patient.id,
                                name: patient.name,
                                lastConsultation: latestConsultation
                                    ? formatDate(
                                        latestConsultation.created_at
                                    )
                                    : "No consultations",
                                consultationCount: consultations.length,
                            };
                        } catch (err) {
                            console.error(
                                `Failed to fetch consultations for patient ${patient.id}:`,
                                err
                            );

                            return {
                                id: patient.id,
                                name: patient.name,
                                lastConsultation: "No consultations",
                                consultationCount: 0,
                            };
                        }
                    })
                );

                setPatients(patientsWithConsultations);
            } catch (err) {
                console.error("Failed to fetch patients:", err);
                setError("Unable to load patients.");
            } finally {
                setLoading(false);
            }
        };

        fetchPatients();
    }, []);

    const filteredPatients = patients.filter((patient) =>
        patient.name.toLowerCase().includes(search.toLowerCase())
    );

    const totalPages = Math.ceil(
        filteredPatients.length / patientsPerPage
    );

    const startIndex = (currentPage - 1) * patientsPerPage;

    const paginatedPatients = filteredPatients.slice(
        startIndex,
        startIndex + patientsPerPage
    );

    return (
        <main className="doctor-page">
            <div className="doctor-page-header">
                <div>
                    <h1>Patients</h1>
                    <p>View and manage your patients.</p>
                </div>
            </div>

            <div className="patients-search">
                <input
                    type="text"
                    placeholder="Search patients..."
                    value={search}
                    onChange={(e) => {
                        setSearch(e.target.value);
                        setCurrentPage(1);
                    }}
                />
            </div>

            {error && (
                <div className="patients-empty">
                    {error}
                </div>
            )}

            <div className="patients-card">
                <div className="patients-table-header">
                    <span>Patient</span>
                    <span>Last Consultation</span>
                    <span>Consultations</span>
                    <span></span>
                </div>

                {loading ? (
                    <div className="patients-empty">
                        Loading patients...
                    </div>
                ) : filteredPatients.length === 0 ? (
                    <div className="patients-empty">
                        {search
                            ? "No patients found."
                            : "No patients yet."}
                    </div>
                ) : (
                    paginatedPatients.map((patient, index) => (
                        <div
                            className="patient-row"
                            key={patient.id}
                            style={{
                                animationDelay: `${index * 0.06}s`,
                            }}
                        >
                            <span className="patient-name">
                                {patient.name}
                            </span>

                            <span className="patient-date">
                                {patient.lastConsultation}
                            </span>

                            <span className="patient-count">
                                {patient.consultationCount}
                            </span>

                            <NavLink
                                to={`/doctor/patients/${patient.id}`}
                                className="patient-view"
                            >
                                View
                            </NavLink>
                        </div>
                    ))
                )}

                {totalPages > 1 && (
                    <div className="patients-pagination">
                        <button
                            type="button"
                            className="pagination-button"
                            onClick={() =>
                                setCurrentPage((page) => Math.max(page - 1, 1))
                            }
                            disabled={currentPage === 1}
                        >
                            ← Previous
                        </button>

                        <span className="pagination-counter">
                            {currentPage} / {totalPages}
                        </span>

                        <button
                            type="button"
                            className="pagination-button"
                            onClick={() =>
                                setCurrentPage((page) =>
                                    Math.min(page + 1, totalPages)
                                )
                            }
                            disabled={currentPage === totalPages}
                        >
                            Next →
                        </button>
                    </div>
                )}

            </div>
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

export default Patients;