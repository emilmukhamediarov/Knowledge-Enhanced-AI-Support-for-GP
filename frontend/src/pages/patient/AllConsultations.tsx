import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./AllConsultations.css";

interface Consultation {
    consultation_id: number;
    title: string | null;
    created_at: string;
}

interface ConsultationResponse {
    user_id: number;
    consultations: Consultation[];
}

function Consultations() {
    const [consultations, setConsultations] = useState<Consultation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    const userId = localStorage.getItem("userId");

    useEffect(() => {
        if (!userId) {
            setConsultations([]);
            setLoading(false);
            return;
        }

        const fetchConsultations = async () => {
            try {
                setLoading(true);
                setError(false);

                const data = await apiFetch(
                    `/consultations/user/${userId}`
                ) as ConsultationResponse;

                console.log("Consultations:", data.consultations);

                const sortedConsultations = [...data.consultations].sort(
                    (a, b) =>
                        new Date(b.created_at).getTime() -
                        new Date(a.created_at).getTime()
                );

                setConsultations(sortedConsultations);
            } catch (error) {
                console.error(
                    "Failed to fetch consultations:",
                    error
                );

                setConsultations([]);
                setError(true);
            } finally {
                setLoading(false);
            }
        };

        void fetchConsultations();
    }, [userId]);

    const formatDateTime = (dateString: string) => {
        const date = new Date(dateString);

        return date.toLocaleString("en-NZ", {
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit",
            hour12: true,
        });
    };

    return (
        <main className="consultations-page">
            <section className="consultations-header">
                <h1>Your consultations</h1>
                <p>
                    View and revisit your previous consultations.
                </p>
            </section>

            {loading && (
                <div className="consultations-message">
                    <p>Loading consultations...</p>
                </div>
            )}

            {error && (
                <div className="consultations-message">
                    <p>
                        Unable to load your consultations.
                        Please try again later.
                    </p>
                </div>
            )}

            {!loading && !error && consultations.length === 0 && (
                <div className="consultations-message">
                    <p>
                        You don't have any previous consultations yet.
                    </p>
                </div>
            )}

            {!loading && !error && consultations.length > 0 && (
                <div className="all-consultations">
                    {consultations.map((consultation) => (
                        <NavLink
                            key={consultation.consultation_id}
                            to={`/chat/${consultation.consultation_id}`}
                            className="consultation-card"
                        >
                            <div className="consultation-info">
                                <h2>
                                    {consultation.title ||
                                        "New Consultation"}
                                </h2>

                                <span className="consultation-number">
                                    Consultation{" "}
                                    {consultation.consultation_id}
                                </span>

                                <p>
                                    {formatDateTime(
                                        consultation.created_at
                                    )}
                                </p>
                            </div>

                            <span className="consultation-arrow">
                                →
                            </span>
                        </NavLink>
                    ))}
                </div>
            )}
        </main>
    );
}

export default Consultations;