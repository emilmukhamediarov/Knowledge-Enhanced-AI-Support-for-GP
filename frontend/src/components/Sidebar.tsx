import "./Sidebar.css";
import { useTheme } from "../hooks/useTheme";
import { NavLink, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";

interface Consultation {
    id: number;
    user_id: number;
}

function Sidebar() {
    const { theme, setTheme } = useTheme();

    const isDark = theme === "dark";

    const role = localStorage.getItem("role");
    const userId = localStorage.getItem("userId");

    const location = useLocation();

    const [recentConsultations, setRecentConsultations] =
        useState<Consultation[]>([]);

    useEffect(() => {
        if (!userId) {
            setRecentConsultations([]);
            return;
        }

        const fetchRecentConsultations = async () => {
            try {
                const data = await apiFetch(
                    `/consultations/users/${userId}/consultations`
                );

                setRecentConsultations(
                    data.consultations.slice(0, 5)
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
    }, [userId, location.pathname]);

    const toggleTheme = () => {
        setTheme(isDark ? "light" : "dark");
    };

    return (
        <aside className="sidebar">

            <div className="sidebar-top">

                {(role === "patient" || role === "admin") && (
                    <NavLink
                        to="/new-consultation"
                        className={({ isActive }) =>
                            `sidebar-new-chat ${
                                isActive ? "active" : ""
                            }`
                        }
                    >
                        <span className="sidebar-new-chat-content">

                            <span className="sidebar-new-chat-icon">
                                +
                            </span>

                            <span>
                                New Chat
                            </span>

                        </span>
                    </NavLink>
                )}

                <div className="sidebar-separator" />

                <div className="sidebar-recent">

                    <span className="sidebar-section-title">
                        Recent
                    </span>

                    <div className="sidebar-chats">

                        {recentConsultations.map(
                            (consultation) => (
                                <NavLink
                                    key={consultation.id}
                                    to={`/chat/${consultation.id}`}
                                    className={({ isActive }) =>
                                        `sidebar-chat ${
                                            isActive
                                                ? "active"
                                                : ""
                                        }`
                                    }
                                >
                                    Chat {consultation.id}
                                </NavLink>
                            )
                        )}

                    </div>

                </div>

            </div>

            <div className="sidebar-bottom">

                <div className="theme-container">

                    <button
                        className={`theme-toggle ${
                            isDark ? "dark" : ""
                        }`}
                        onClick={toggleTheme}
                        aria-label={
                            isDark
                                ? "Switch to light mode"
                                : "Switch to dark mode"
                        }
                    >
                        <span className="theme-toggle-icon sun">
                            ☀
                        </span>

                        <span className="theme-toggle-icon moon">
                            ☾
                        </span>

                        <span className="theme-toggle-thumb" />
                    </button>

                    <span className="theme-label">
                        {isDark
                            ? "Dark mode"
                            : "Light mode"}
                    </span>

                </div>

            </div>

        </aside>
    );
}

export default Sidebar;