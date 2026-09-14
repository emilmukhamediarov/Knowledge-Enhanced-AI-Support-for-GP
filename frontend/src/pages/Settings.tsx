import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import "./Settings.css";

interface FirstTimeSettingsModalProps {
    onComplete: () => void;
}

const languages = [
    {
        value: "en-US",
        label: "English (United States)",
    },
    {
        value: "zh-CN",
        label: "Chinese (Simplified)",
    },
    {
        value: "th-TH",
        label: "Thai",
    },
    {
        value: "ru-RU",
        label: "Russian",
    },
    {
        value: "es-US",
        label: "Spanish",
    },
];

function getToday(): string {
    return new Date().toISOString().split("T")[0];
}

export function FirstTimeSettingsModal({
                                           onComplete,
                                       }: FirstTimeSettingsModalProps) {
    const [preferredLanguage, setPreferredLanguage] =
        useState("en-US");

    const [dateOfBirth, setDateOfBirth] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const saveSettings = async () => {
        if (!dateOfBirth) {
            setError("Please enter your date of birth.");
            return;
        }

        if (!preferredLanguage) {
            setError("Please select your preferred language.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            await apiFetch("/users/me", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    preferred_language: preferredLanguage,
                    date_of_birth: dateOfBirth,
                }),
            });

            onComplete();
        } catch (error) {
            console.error(
                "Failed to save user settings:",
                error
            );

            setError(
                "Failed to save your settings. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="settings-modal-overlay">
            <div className="settings-modal">
                <div className="settings-modal-header">
                    <h2>Welcome!</h2>

                    <p>
                        Before you start your first consultation,
                        please tell us a little about yourself.
                    </p>
                </div>

                <div className="settings-form">
                    <div className="settings-field">
                        <label htmlFor="setup-date-of-birth">
                            Date of birth
                        </label>

                        <input
                            id="setup-date-of-birth"
                            type="date"
                            value={dateOfBirth}
                            onChange={(event) => {
                                setDateOfBirth(
                                    event.target.value
                                );
                                setError("");
                            }}
                            max={getToday()}
                        />
                    </div>

                    <div className="settings-field">
                        <label htmlFor="setup-language">
                            Preferred language
                        </label>

                        <select
                            id="setup-language"
                            value={preferredLanguage}
                            onChange={(event) => {
                                setPreferredLanguage(
                                    event.target.value
                                );
                                setError("");
                            }}
                        >
                            {languages.map((language) => (
                                <option
                                    key={language.value}
                                    value={language.value}
                                >
                                    {language.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {error && (
                        <p className="settings-error">
                            {error}
                        </p>
                    )}

                    <button
                        type="button"
                        className="settings-save-button"
                        onClick={() => void saveSettings()}
                        disabled={loading}
                    >
                        {loading
                            ? "Saving..."
                            : "Save and continue"}
                    </button>
                </div>
            </div>
        </div>
    );
}

function Settings() {
    const [preferredLanguage, setPreferredLanguage] =
        useState("en-US");

    const [dateOfBirth, setDateOfBirth] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        const loadSettings = async () => {
            try {
                setError("");

                const data = await apiFetch("/users/me");

                if (data.preferred_language) {
                    setPreferredLanguage(
                        data.preferred_language
                    );
                }

                if (data.date_of_birth) {
                    setDateOfBirth(
                        data.date_of_birth
                    );
                }
            } catch (error) {
                console.error(
                    "Failed to load settings:",
                    error
                );

                setError(
                    "Failed to load your settings."
                );
            } finally {
                setLoading(false);
            }
        };

        void loadSettings();
    }, []);

    const saveSettings = async () => {
        if (!dateOfBirth) {
            setError("Please enter your date of birth.");
            return;
        }

        if (!preferredLanguage) {
            setError("Please select your preferred language.");
            return;
        }

        setSaving(true);
        setError("");
        setSuccess(false);

        try {
            await apiFetch("/users/me", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    preferred_language: preferredLanguage,
                    date_of_birth: dateOfBirth,
                }),
            });

            setSuccess(true);
        } catch (error) {
            console.error(
                "Failed to save settings:",
                error
            );

            setError(
                "Failed to save your settings. Please try again."
            );
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <main className="settings-page">
                <div className="settings-container">
                    <h1>Settings</h1>

                    <p className="settings-loading">
                        Loading...
                    </p>
                </div>
            </main>
        );
    }

    return (
        <main className="settings-page">
            <div className="settings-container">
                <div className="settings-heading">
                    <h1>Settings</h1>

                    <p>
                        Manage your personal information and
                        consultation preferences.
                    </p>
                </div>

                <section className="settings-section">
                    <div className="settings-section-header">
                        <h2>Personal information</h2>

                        <p>
                            This information helps us provide
                            a more personalised experience.
                        </p>
                    </div>

                    <div className="settings-form">
                        <div className="settings-field">
                            <label htmlFor="date-of-birth">
                                Date of birth
                            </label>

                            <input
                                id="date-of-birth"
                                type="date"
                                value={dateOfBirth}
                                onChange={(event) => {
                                    setDateOfBirth(
                                        event.target.value
                                    );
                                    setSuccess(false);
                                    setError("");
                                }}
                                max={getToday()}
                            />
                        </div>
                    </div>
                </section>

                <section className="settings-section">
                    <div className="settings-section-header">
                        <h2>Preferences</h2>

                        <p>
                            Choose how you would like to
                            communicate with the assistant.
                        </p>
                    </div>

                    <div className="settings-form">
                        <div className="settings-field">
                            <label htmlFor="preferred-language">
                                Preferred language
                            </label>

                            <select
                                id="preferred-language"
                                value={preferredLanguage}
                                onChange={(event) => {
                                    setPreferredLanguage(
                                        event.target.value
                                    );
                                    setSuccess(false);
                                    setError("");
                                }}
                            >
                                {languages.map((language) => (
                                    <option
                                        key={language.value}
                                        value={language.value}
                                    >
                                        {language.label}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </section>

                {error && (
                    <p className="settings-error">
                        {error}
                    </p>
                )}

                {success && (
                    <p className="settings-success">
                        Settings saved successfully.
                    </p>
                )}

                <div className="settings-actions">
                    <button
                        type="button"
                        className="settings-save-button"
                        onClick={() => void saveSettings()}
                        disabled={saving}
                    >
                        {saving
                            ? "Saving..."
                            : "Save changes"}
                    </button>
                </div>
            </div>
        </main>
    );
}

export default Settings;
