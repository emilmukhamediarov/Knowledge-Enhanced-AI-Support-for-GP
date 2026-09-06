import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./PatientHome.css";

interface Consultation {
    consultation_id: number;
}

function Home() {
    const [backendConnected, setBackendConnected] = useState(false);
    const [recentConsultations, setRecentConsultations] = useState<Consultation[]>([]);
    const [showHowItWorks, setShowHowItWorks] = useState(false);
    const [showStep1, setShowStep1] = useState(false);
    const [showStep2, setShowStep2] = useState(false);
    const [showStep3, setShowStep3] = useState(false);
    const [showRecent, setShowRecent] = useState(false);
    const [showTryConsultation, setShowTryConsultation] = useState(false);

    const userId = localStorage.getItem("userId");
    const userName = localStorage.getItem("userName")?.trim() || "there";

    useEffect(() => {
        apiFetch("/")
            .then(() => setBackendConnected(true))
            .catch((error) => {
                console.error("Backend error:", error);
                setBackendConnected(false);
            });
    }, []);

    useEffect(() => {
        if (!userId) {
            setRecentConsultations([]);
            return;
        }

        const fetchRecentConsultations = async () => {
            try {
                const data = await apiFetch(
                    `/consultations/user/${userId}`
                );

                const sortedConsultations = [...data.consultations].sort(
                    (a, b) => b.consultation_id - a.consultation_id
                );

                setRecentConsultations(
                    sortedConsultations.slice(0, 5)
                );
            } catch (error) {
                console.error(
                    "Failed to fetch recent consultations:",
                    error
                );

                setRecentConsultations([]);
            }
        };

        void fetchRecentConsultations();
    }, [userId]);

    useEffect(() => {
        const timers = [
            setTimeout(() => setShowHowItWorks(true), 1200),
            setTimeout(() => setShowStep1(true), 1500),
            setTimeout(() => setShowStep2(true), 1800),
            setTimeout(() => setShowStep3(true), 2100),
            setTimeout(() => setShowTryConsultation(true), 2400),
            setTimeout(() => setShowRecent(true), 2800),
        ];

        return () => {
            timers.forEach(clearTimeout);
        };
    }, []);

    return (
        <main className="patient-home">
            <section className="patient-welcome">
                <div className="patient-welcome-title">
                    <h1>Hello, {userName} </h1>
                </div>

                <p>
                    Here's how your consultations work.
                </p>
            </section>

            <section
                className={`how-it-works ${
                    showHowItWorks ? "section-visible" : ""
                }`}
            >
                <h2>How it works</h2>

                <div className="steps">
                    <div
                        className={`step ${
                            showStep1 ? "step-visible" : ""
                        }`}
                    >
                        <div className="step-number">01</div>
                        <h3>Start a consultation</h3>
                        <p>
                            Tell us what's bothering you and what you'd
                            like help with.
                        </p>
                    </div>

                    <div
                        className={`step ${
                            showStep2 ? "step-visible" : ""
                        }`}
                    >
                        <div className="step-number">02</div>
                        <h3>Answer questions</h3>
                        <p>
                            Answer a few questions to help us understand
                            your situation.
                        </p>
                    </div>

                    <div
                        className={`step ${
                            showStep3 ? "step-visible" : ""
                        }`}
                    >
                        <div className="step-number">03</div>
                        <h3>GP review</h3>
                        <p>
                            Your consultation is passed to a GP who can
                            review the information provided.
                        </p>
                    </div>
                </div>
            </section>

            <section
                className={`try-consultation ${
                    showTryConsultation ? "section-visible" : ""
                }`}
            >
                <h2>Ready to get started?</h2>

                <p>
                    Start a new consultation and tell us what's bothering you.
                </p>

                <NavLink
                    to="/new-consultation"
                    className="try-consultation-button"
                >
                    Try it out
                    <span>→</span>
                </NavLink>
            </section>

            <section
                className={`recent-consultations ${
                    showRecent ? "section-visible" : ""
                }`}
            >
                <div className="section-header">
                    <h2>Recent consultations</h2>
                </div>

                {recentConsultations.length === 0 ? (
                    <div className="no-consultations">
                        <p>
                            You don't have any previous consultations yet.
                        </p>
                    </div>
                ) : (
                    <div className="consultation-list">
                        {recentConsultations.map((consultation) => (
                            <NavLink
                                key={consultation.consultation_id}
                                to={`/chat/${consultation.consultation_id}`}
                                className="consultation-row"
                            >
                                <div>
                                    <h3>
                                        Consultation{" "}
                                        {consultation.consultation_id}
                                    </h3>

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
            </section>

            <div className="backend-status">
                <span
                    className={
                        backendConnected
                            ? "status-dot connected"
                            : "status-dot"
                    }
                />
                {backendConnected
                    ? "Connected"
                    : "Backend unavailable"}
            </div>
        </main>
    );
}

export default Home;