import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import "./Consultations.css";
import { apiFetch } from "../../api/client";

type ConsultationStatus =
    | "in-progress"
    | "ready"
    | "closed";

interface Consultation {
    id: number;
    patientId: number;
    patientName: string;
    createdAt: string;
    date: string;
    status: ConsultationStatus;
}

interface ConsultationResponse {
    consultations: {
        consultation_id: number;
        patient_id: number;
        patient_name: string;
        status: string;
        created_at: string;
        closed_at: string | null;
    }[];
}

function Consultations() {
    const [filter, setFilter] =
        useState<"All" | ConsultationStatus>("All");

    const [search, setSearch] = useState("");

    const [consultations, setConsultations] =
        useState<Consultation[]>([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [currentPage, setCurrentPage] = useState(1);

    const consultationsPerPage = 10;

    useEffect(() => {
        const fetchConsultations = async () => {
            try {
                setLoading(true);
                setError("");

                const data =
                    await apiFetch(
                        "/consultations/doctor"
                    ) as ConsultationResponse;

                const formattedConsultations =
                    data.consultations.map((consultation) => ({
                        id: consultation.consultation_id,
                        patientId: consultation.patient_id,
                        patientName: consultation.patient_name,
                        createdAt: consultation.created_at,
                        date: formatDate(
                            consultation.created_at
                        ),
                        status:
                            consultation.status as ConsultationStatus,
                    }));

                setConsultations(formattedConsultations);
            } catch (err) {
                console.error(
                    "Failed to fetch consultations:",
                    err
                );

                setError(
                    "Unable to load consultations."
                );
            } finally {
                setLoading(false);
            }
        };

        fetchConsultations();
    }, []);

    // Filter by status and search
    const filteredConsultations =
        consultations.filter((consultation) => {
            const matchesFilter =
                filter === "All" ||
                consultation.status === filter;

            const searchTerm =
                search.trim().toLowerCase();

            const matchesSearch =
                searchTerm === "" ||
                consultation.patientName
                    .toLowerCase()
                    .includes(searchTerm) ||
                consultation.id
                    .toString()
                    .includes(searchTerm);

            return matchesFilter && matchesSearch;
        });

    const sortedConsultations =
        [...filteredConsultations].sort(
            (a, b) => {
                const statusPriority: Record<
                    ConsultationStatus,
                    number
                > = {
                    ready: 1,
                    "in-progress": 2,
                    closed: 3,
                };

                const statusDifference =
                    statusPriority[a.status] -
                    statusPriority[b.status];

                if (statusDifference !== 0) {
                    return statusDifference;
                }

                return (
                    new Date(b.createdAt).getTime() -
                    new Date(a.createdAt).getTime()
                );
            }
        );

    // Pagination
    const totalPages = Math.ceil(
        sortedConsultations.length /
        consultationsPerPage
    );

    const startIndex =
        (currentPage - 1) *
        consultationsPerPage;

    const paginatedConsultations =
        sortedConsultations.slice(
            startIndex,
            startIndex + consultationsPerPage
        );

    const handleFilterChange = (
        newFilter: "All" | ConsultationStatus
    ) => {
        setFilter(newFilter);
        setCurrentPage(1);
    };

    const handleSearchChange = (
        value: string
    ) => {
        setSearch(value);
        setCurrentPage(1);
    };

    const handlePreviousPage = () => {
        setCurrentPage((page) =>
            Math.max(page - 1, 1)
        );
    };

    const handleNextPage = () => {
        setCurrentPage((page) =>
            Math.min(page + 1, totalPages)
        );
    };

    const getStatusLabel = (
        status: ConsultationStatus
    ) => {
        switch (status) {
            case "in-progress":
                return "In-progress";

            case "ready":
                return "Ready";

            case "closed":
                return "Closed";

            default:
                return status;
        }
    };

    return (
        <main className="doctor-page">
            <div className="doctor-page-header">
                <div>
                    <h1>Consultations</h1>

                    <p>
                        Review and manage patient consultations.
                    </p>
                </div>
            </div>

            <div className="consultation-toolbar">
                <div className="consultation-filters">
                    {(
                        [
                            "All",
                            "in-progress",
                            "ready",
                            "closed",
                        ] as const
                    ).map((status) => (
                        <button
                            key={status}
                            type="button"
                            className={
                                filter === status
                                    ? "active"
                                    : ""
                            }
                            onClick={() =>
                                handleFilterChange(status)
                            }
                        >
                            {status === "All"
                                ? "All"
                                : getStatusLabel(status)}
                        </button>
                    ))}
                </div>

                <div className="consultation-search">
                    <input
                        type="text"
                        value={search}
                        onChange={(event) =>
                            handleSearchChange(
                                event.target.value
                            )
                        }
                        placeholder="Search by patient or consultation #"
                        aria-label="Search consultations"
                    />
                </div>
            </div>

            {error && (
                <div className="consultations-empty">
                    {error}
                </div>
            )}

            <div className="consultations-card">
                <div className="consultations-table-header">
                    <span>Patient</span>
                    <span>Consultation</span>
                    <span>Date</span>
                    <span>Status</span>
                    <span></span>
                </div>

                {loading ? (
                    <div className="consultations-empty">
                        Loading consultations...
                    </div>
                ) : paginatedConsultations.length > 0 ? (
                    paginatedConsultations.map(
                        (consultation, index) => (
                            <NavLink
                                to={`/doctor/consultations/${consultation.id}`}
                                className="consultation-row"
                                key={consultation.id}
                                style={{
                                    animationDelay: `${index * 0.06}s`,
                                }}
                            >
                                <span className="consultation-patient">
                                    {consultation.patientName}
                                </span>

                                <span className="consultation-id">
                                    #{consultation.id}
                                </span>

                                <span className="consultation-date">
                                    {consultation.date}
                                </span>

                                <span
                                    className={`consultation-status ${consultation.status}`}
                                >
                                    {getStatusLabel(consultation.status)}
                                </span>

                                <span className="consultation-view">
                                    View
                                </span>
                            </NavLink>
                        )
                    )
                ) : (
                    <div className="consultations-empty">
                        {search.trim()
                            ? `No consultations found for "${search}".`
                            : filter === "All"
                                ? "No consultations yet."
                                : `No ${getStatusLabel(
                                    filter
                                ).toLowerCase()} consultations.`}
                    </div>
                )}
            </div>

            {totalPages > 1 && (
                <div className="consultations-pagination">
                    <button
                        type="button"
                        className="pagination-button"
                        onClick={handlePreviousPage}
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
                        onClick={handleNextPage}
                        disabled={
                            currentPage === totalPages
                        }
                    >
                        Next →
                    </button>
                </div>
            )}
        </main>
    );
}

function formatDate(
    dateString: string
): string {
    return new Date(dateString).toLocaleDateString(
        "en-NZ",
        {
            day: "numeric",
            month: "short",
            year: "numeric",
        }
    );
}

export default Consultations;