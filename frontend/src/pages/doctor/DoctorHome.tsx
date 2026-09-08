import { useEffect, useMemo, useState } from "react";
import { NavLink } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./DoctorHome.css";

interface Consultation {
    consultation_id: number;
    patient_id: number;
    patient_name: string;
    status: string;
    created_at: string;
    closed_at: string | null;
}

function DoctorHome() {
    const today = new Date();

    const [consultations, setConsultations] =
        useState<Consultation[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [currentMonth, setCurrentMonth] = useState(
        new Date(today.getFullYear(), today.getMonth(), 1)
    );

    const [selectedDate, setSelectedDate] = useState(
        today.toISOString().split("T")[0]
    );

    useEffect(() => {
        const fetchConsultations = async () => {
            try {
                setLoading(true);
                setError("");

                const response = await apiFetch(
                    "/consultations/doctor"
                ) as {
                    consultations: Consultation[];
                };

                setConsultations(response.consultations || []);
            } catch (err) {
                console.error(
                    "Failed to fetch consultations:",
                    err
                );

                setError("Unable to load consultations.");
            } finally {
                setLoading(false);
            }
        };

        fetchConsultations();
    }, []);

    const monthName = currentMonth.toLocaleString("default", {
        month: "long",
    });

    const year = currentMonth.getFullYear();

    const daysInMonth = new Date(
        year,
        currentMonth.getMonth() + 1,
        0
    ).getDate();

    const firstDay = new Date(
        year,
        currentMonth.getMonth(),
        1
    ).getDay();

    const calendarDays = useMemo(() => {
        const days: (number | null)[] = [];

        // Monday-first calendar
        const leadingDays = firstDay === 0 ? 6 : firstDay - 1;

        for (let i = 0; i < leadingDays; i++) {
            days.push(null);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            days.push(day);
        }

        return days;
    }, [firstDay, daysInMonth]);

    const formatDateKey = (day: number) => {
        const month = String(
            currentMonth.getMonth() + 1
        ).padStart(2, "0");

        const date = String(day).padStart(2, "0");

        return `${year}-${month}-${date}`;
    };

    const getDateKey = (date: string) => {
        return date.split("T")[0];
    };

    const getTime = (date: string) => {
        return new Date(date).toLocaleTimeString("default", {
            hour: "2-digit",
            minute: "2-digit",
            hour12: false,
        });
    };

    const selectedConsultations = consultations.filter(
        (consultation) =>
            getDateKey(consultation.created_at) === selectedDate
    );

    /*
     * Keep status handling consistent with the Consultations page.
     *
     * Backend may return:
     * - active
     * - in-progress
     * - pending
     * - closed
     *
     * The frontend displays:
     * - Active
     * - Pending
     * - Closed
     */
    const formatStatus = (status: string) => {
        switch (status.toLowerCase()) {
            case "closed":
                return "Closed";

            case "pending":
                return "Pending";

            case "active":
            case "in-progress":
                return "Active";

            default:
                return "Active";
        }
    };

    const activeConsultations = consultations.filter(
        (consultation) =>
            formatStatus(consultation.status) === "Active"
    );

    const waitingConsultations = consultations.filter(
        (consultation) =>
            formatStatus(consultation.status) === "Pending"
    );

    const closedConsultations = consultations.filter(
        (consultation) =>
            formatStatus(consultation.status) === "Closed"
    );

    const recentlyClosed = [...closedConsultations]
        .sort(
            (a, b) =>
                new Date(
                    b.closed_at || b.created_at
                ).getTime() -
                new Date(
                    a.closed_at || a.created_at
                ).getTime()
        )
        .slice(0, 5);

    const previousMonth = () => {
        setCurrentMonth(
            new Date(
                currentMonth.getFullYear(),
                currentMonth.getMonth() - 1,
                1
            )
        );
    };

    const nextMonth = () => {
        setCurrentMonth(
            new Date(
                currentMonth.getFullYear(),
                currentMonth.getMonth() + 1,
                1
            )
        );
    };

    const selectedDateLabel = new Date(
        `${selectedDate}T00:00:00`
    ).toLocaleDateString("default", {
        day: "numeric",
        month: "long",
        year: "numeric",
    });

    if (loading) {
        return (
            <main className="doctor-dashboard">
                <div className="dashboard-message">
                    Loading dashboard...
                </div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="doctor-dashboard">
                <div className="dashboard-message error">
                    {error}
                </div>
            </main>
        );
    }

    return (
        <main className="doctor-dashboard">

            <div className="doctor-dashboard-main">

                <section className="dashboard-card calendar-card">

                    <div className="calendar-header">

                        <div>
                            <h2>{monthName}</h2>
                            <span>{year}</span>
                        </div>

                        <div className="calendar-navigation">

                            <button
                                type="button"
                                onClick={previousMonth}
                                aria-label="Previous month"
                            >
                                ‹
                            </button>

                            <button
                                type="button"
                                onClick={nextMonth}
                                aria-label="Next month"
                            >
                                ›
                            </button>

                        </div>

                    </div>

                    <div className="calendar-weekdays">
                        <span>Mon</span>
                        <span>Tue</span>
                        <span>Wed</span>
                        <span>Thu</span>
                        <span>Fri</span>
                        <span>Sat</span>
                        <span>Sun</span>
                    </div>

                    <div className="calendar-grid">

                        {calendarDays.map((day, index) => {

                            if (day === null) {
                                return (
                                    <span
                                        key={`empty-${index}`}
                                        className="calendar-day empty"
                                    />
                                );
                            }

                            const dateKey = formatDateKey(day);

                            const hasConsultations =
                                consultations.some(
                                    (consultation) =>
                                        getDateKey(
                                            consultation.created_at
                                        ) === dateKey
                                );

                            const isSelected =
                                selectedDate === dateKey;

                            const isToday =
                                dateKey ===
                                today
                                    .toISOString()
                                    .split("T")[0];

                            return (
                                <button
                                    key={dateKey}
                                    type="button"
                                    className={`calendar-day ${
                                        isSelected
                                            ? "selected"
                                            : ""
                                    } ${
                                        isToday
                                            ? "today"
                                            : ""
                                    }`}
                                    onClick={() =>
                                        setSelectedDate(dateKey)
                                    }
                                >
                                    <span>{day}</span>

                                    {hasConsultations && (
                                        <span className="appointment-dot" />
                                    )}
                                </button>
                            );
                        })}

                    </div>

                </section>

                <section className="dashboard-card appointments-card">

                    <div className="appointments-header">

                        <div>
                            <h2>Consultations</h2>

                            <span>
                                {selectedDateLabel}
                            </span>
                        </div>

                        <span className="appointment-count">
                            {selectedConsultations.length}
                        </span>

                    </div>

                    <div className="appointment-list">

                        {selectedConsultations.length === 0 ? (
                            <div className="no-appointments">
                                No consultations on this date
                            </div>
                        ) : (
                            selectedConsultations.map(
                                (consultation) => (
                                    <div
                                        key={
                                            consultation.consultation_id
                                        }
                                        className="appointment-item"
                                    >

                                        <div className="appointment-time">
                                            {getTime(
                                                consultation.created_at
                                            )}
                                        </div>

                                        <div className="appointment-info">
                                            <span className="appointment-patient">
                                                {consultation.patient_name}

                                                <span className="appointment-number">
                                                    #{consultation.consultation_id}
                                                </span>
                                            </span>
                                        </div>

                                        <span
                                            className={`appointment-status ${formatStatus(
                                                consultation.status
                                            ).toLowerCase()}`}
                                        >
                                            {formatStatus(
                                                consultation.status
                                            )}
                                        </span>

                                        <NavLink
                                            to={`/doctor/consultations/${consultation.consultation_id}`}
                                            className="appointment-open"
                                        >
                                            Open
                                        </NavLink>

                                    </div>
                                )
                            )
                        )}

                    </div>

                </section>

            </div>

            <section className="dashboard-stats">

                <div className="dashboard-stat waiting">
                    <span>Waiting for response</span>

                    <strong>
                        {waitingConsultations.length}
                    </strong>
                </div>

                <div className="dashboard-stat upcoming">
                    <span>Total consultations</span>

                    <strong>
                        {consultations.length}
                    </strong>
                </div>

                <div className="dashboard-stat active">
                    <span>Active consultations</span>

                    <strong>
                        {activeConsultations.length}
                    </strong>
                </div>

            </section>

            {/* Recently closed */}

            <section className="dashboard-card recently-closed">

                <div className="recently-closed-header">

                    <h2>Recently Closed Consultations</h2>

                    <NavLink to="/doctor/consultations">
                        View all
                    </NavLink>

                </div>

                <div className="closed-list">

                    {recentlyClosed.length === 0 ? (
                        <div className="no-appointments">
                            No recently closed consultations
                        </div>
                    ) : (
                        recentlyClosed.map(
                            (consultation) => (
                                <div
                                    key={
                                        consultation.consultation_id
                                    }
                                    className="closed-item"
                                >

                                    <div className="closed-patient">

                                        <span>
                                            {
                                                consultation.patient_name
                                            }
                                        </span>

                                        <small>
                                            Consultation #
                                            {
                                                consultation.consultation_id
                                            }
                                        </small>

                                    </div>

                                    <span className="closed-date">

                                        {new Date(
                                            consultation.closed_at ||
                                            consultation.created_at
                                        ).toLocaleDateString(
                                            "default",
                                            {
                                                day: "numeric",
                                                month: "short",
                                                year: "numeric",
                                            }
                                        )}

                                    </span>

                                    <NavLink
                                        to={`/doctor/consultations/${consultation.consultation_id}`}
                                        className="closed-view"
                                    >
                                        View
                                    </NavLink>

                                </div>
                            )
                        )
                    )}

                </div>

            </section>

        </main>
    );
}

export default DoctorHome;