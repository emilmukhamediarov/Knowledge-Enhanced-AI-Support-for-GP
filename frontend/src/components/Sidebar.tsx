import "./Sidebar.css";
import { useTheme } from "../hooks/useTheme";
import { NavLink, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import { FirstTimeSettingsModal } from "../pages/Settings";

interface Consultation {
    consultation_id: number;
    title: string | null;
}

interface UserSettings {
    preferred_language: string | null;
    date_of_birth: string | null;
}

function Sidebar() {
    const { theme, setTheme } = useTheme();
    const isDark = theme === "dark";

    const role = localStorage.getItem("role");
    const userId = localStorage.getItem("userId");

    const location = useLocation();

    const [recentConsultations, setRecentConsultations] = useState<Consultation[]>([]);
    const [showSetupModal, setShowSetupModal] = useState(false);
    const [isMobileOpen, setIsMobileOpen] = useState(false);

    // Auto-close sidebar when switching pages on mobile
    useEffect(() => {
        setIsMobileOpen(false);
    }, [location.pathname]);

    useEffect(() => {
        if (role !== "patient" || !userId) {
            setRecentConsultations([]);
            return;
        }

        const fetchRecentConsultations = async () => {
            try {
                const data = await apiFetch(`/consultations/user/${userId}`);
                const sortedConsultations = [...data.consultations].sort(
                    (a, b) => b.consultation_id - a.consultation_id
                );
                setRecentConsultations(sortedConsultations.slice(0, 5));
            } catch (error) {
                console.error("Failed to fetch recent consultations:", error);
                setRecentConsultations([]);
            }
        };

        void fetchRecentConsultations();
    }, [role, userId, location.pathname]);

    useEffect(() => {
        if (role !== "patient" || !userId) {
            return;
        }

        const checkFirstTimeSetup = async () => {
            try {
                const user = await apiFetch("/users/me");

                const settings: UserSettings = {
                    preferred_language: user.preferred_language ?? null,
                    date_of_birth: user.date_of_birth ?? null,
                };

                const settingsIncomplete =
                    !settings.preferred_language || !settings.date_of_birth;

                if (!settingsIncomplete) {
                    return;
                }

                const data = await apiFetch(`/consultations/user/${userId}`);
                const consultations = data.consultations ?? [];

                if (consultations.length === 0) {
                    setShowSetupModal(true);
                }
            } catch (error) {
                console.error("Failed to check first-time setup:", error);
            }
        };

        void checkFirstTimeSetup();
    }, [role, userId]);

    const toggleTheme = () => {
        setTheme(isDark ? "light" : "dark");
    };

    return (
        <>
            {/* Mobile Toggle Hamburger Button */}
            <button
                className="sidebar-mobile-toggle"
                onClick={() => setIsMobileOpen(!isMobileOpen)}
                aria-label="Toggle navigation menu"
            >
                {isMobileOpen ? "✕" : "☰"}
            </button>

            {/* Backdrop overlay for mobile drawer */}
            <div
                className={`sidebar-overlay ${isMobileOpen ? "active" : ""}`}
                onClick={() => setIsMobileOpen(false)}
            />

            <aside className={`sidebar ${isMobileOpen ? "open" : ""}`}>
                <div className="sidebar-top">
                    {(role === "patient" || role === "admin") && (
                        <>
                            <NavLink
                                to="/new-consultation"
                                className={({ isActive }) =>
                                    `sidebar-new-chat ${isActive ? "active" : ""}`
                                }
                            >
                                <span className="sidebar-new-chat-content">
                                    <span className="sidebar-new-chat-icon">+</span>
                                    <span>New Chat</span>
                                </span>
                            </NavLink>

                            <div className="sidebar-separator" />

                            <div className="sidebar-recent">
                                <span className="sidebar-section-title">Recent</span>
                                <div className="sidebar-chats">
                                    {recentConsultations.map((consultation) => (
                                        <NavLink
                                            key={consultation.consultation_id}
                                            to={`/chat/${consultation.consultation_id}`}
                                            className={({ isActive }) =>
                                                `sidebar-chat ${isActive ? "active" : ""}`
                                            }
                                        >
                                            {consultation.title ? (
                                                <>
                                                    <span className="sidebar-chat-title">
                                                        {consultation.title}
                                                    </span>
                                                    <span className="sidebar-chat-number">
                                                        (#{consultation.consultation_id})
                                                    </span>
                                                </>
                                            ) : (
                                                <>Chat {consultation.consultation_id}</>
                                            )}
                                        </NavLink>
                                    ))}
                                </div>
                            </div>
                        </>
                    )}

                    {role === "doctor" && (
                        <>
                            <NavLink
                                to="/doctorhome"
                                className={({ isActive }) =>
                                    `sidebar-link ${isActive ? "active" : ""}`
                                }
                            >
                                <span>Dashboard</span>
                            </NavLink>

                            <NavLink
                                to="/doctor/patients"
                                className={({ isActive }) =>
                                    `sidebar-link ${isActive ? "active" : ""}`
                                }
                            >
                                <span>Patients</span>
                            </NavLink>

                            <NavLink
                                to="/doctor/consultations"
                                className={({ isActive }) =>
                                    `sidebar-link ${isActive ? "active" : ""}`
                                }
                            >
                                <span>Consultations</span>
                            </NavLink>
                        </>
                    )}
                </div>

                <div className="sidebar-bottom">
                    <NavLink
                        to="/edit-profile"
                        className={({ isActive }) =>
                            `sidebar-link ${isActive ? "active" : ""}`
                        }
                    >
                        <span>Profile</span>
                    </NavLink>

                    <div className="settings-container">
                        <NavLink
                            to="/settings"
                            className={({ isActive }) =>
                                `sidebar-link sidebar-settings-link ${
                                    isActive ? "active" : ""
                                }`
                            }
                        >
                            <span className="sidebar-settings-icon">⚙</span>
                            <span>Settings</span>
                        </NavLink>
                    </div>

                    <div className="theme-container">
                        <button
                            className={`theme-toggle ${isDark ? "dark" : ""}`}
                            onClick={toggleTheme}
                            aria-label={
                                isDark
                                    ? "Switch to light mode"
                                    : "Switch to dark mode"
                            }
                        >
                            <span className="theme-toggle-icon sun">☀</span>
                            <span className="theme-toggle-icon moon">☾</span>
                            <span className="theme-toggle-thumb" />
                        </button>

                        <span className="theme-label">
                            {isDark ? "Dark mode" : "Light mode"}
                        </span>
                    </div>
                </div>
            </aside>

            {showSetupModal && (
                <FirstTimeSettingsModal
                    onComplete={() => setShowSetupModal(false)}
                />
            )}
        </>
    );
}

export default Sidebar;