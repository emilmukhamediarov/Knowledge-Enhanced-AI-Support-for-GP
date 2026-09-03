import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SessionExpiredModal.css";

function SessionExpiredModal() {
    const navigate = useNavigate();
    const [open, setOpen] = useState(false);

    useEffect(() => {
        const handleSessionExpired = () => {
            setOpen(true);
        };

        window.addEventListener(
            "session-expired",
            handleSessionExpired
        );

        return () => {
            window.removeEventListener(
                "session-expired",
                handleSessionExpired
            );
        };
    }, []);

    const handleLogin = () => {
        setOpen(false);
        navigate("/login");
    };

    if (!open) {
        return null;
    }

    return (
        <div className="session-modal-overlay">
            <div
                className="session-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="session-expired-title"
            >
                <div className="session-modal-icon">
                    !
                </div>

                <h2 id="session-expired-title">
                    Session expired
                </h2>

                <p>
                    Your session has expired. Please log in again
                    to continue.
                </p>

                <button
                    type="button"
                    className="session-modal-button"
                    onClick={handleLogin}
                >
                    Log in
                </button>
            </div>
        </div>
    );
}

export default SessionExpiredModal;
