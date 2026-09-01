import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./AllConsultations.css";

interface Consultation {
    id: number;
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
                const data = await apiFetch(
                    `/consultations/users/${userId}/consultations`
);

setConsultations(data.consultations);
} catch (error) {
    console.error(
        "Failed to fetch consultations:",
        error
    );

    setError(true);
} finally {
    setLoading(false);
}
};

void fetchConsultations();
}, [userId]);

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
                        key={consultation.id}
                        to={`/chat/${consultation.id}`}
                        className="consultation-card"
                    >
                        <div>
                            <h2>
                                Consultation {consultation.id}
                            </h2>

                            <p>
                                View consultation
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
