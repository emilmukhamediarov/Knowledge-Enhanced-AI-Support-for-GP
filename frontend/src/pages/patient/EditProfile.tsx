import { useEffect, useState } from "react";
import { useBlocker } from "react-router-dom";
import { apiFetch } from "../../api/client";
import "./EditProfile.css";

interface UserDetails {
    id: number;
    username: string;
    name: string;
    email: string | null;
    date_of_birth: string | null;
    age: number | null;
    preferred_language: string;
    ethnicity: string | null;
    medical_history: string | null;
    allergies: string[] | null;
    medications: string[] | null;
}

interface Doctor {
    id: number;
    name: string;
    username: string;
}

interface MyDoctorResponse {
    doctor: Doctor | null;
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

function EditProfile() {
    // Login.tsx must save the login response role before navigating here.
    // This controls the UI only; the backend still enforces permissions.
    const [role] = useState(() =>
        (localStorage.getItem("role") || localStorage.getItem("userRole") || "")
            .trim()
            .toLowerCase()
    );
    const isPatient = role === "patient";
    const [user, setUser] = useState<UserDetails | null>(null);
    const [doctors, setDoctors] = useState<Doctor[]>([]);

    const [name, setName] = useState("");
    const [dateOfBirth, setDateOfBirth] = useState("");
    const [preferredLanguage, setPreferredLanguage] = useState("");
    const [ethnicity, setEthnicity] = useState("");
    const [medicalHistory, setMedicalHistory] = useState("");
    const [allergies, setAllergies] = useState("");
    const [medications, setMedications] = useState("");
    const [selectedDoctor, setSelectedDoctor] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [savingDoctor, setSavingDoctor] = useState(false);

    const [savedProfile, setSavedProfile] = useState({
        name: "",
        dateOfBirth: "",
        preferredLanguage: "",
        ethnicity: "",
        medicalHistory: "",
        allergies: "",
        medications: "",
        selectedDoctor: "",
    });


    const [message, setMessage] = useState("");
    const [doctorMessage, setDoctorMessage] = useState("");

    const [showPasswordReset, setShowPasswordReset] = useState(false);
    const [_resetEmail, setResetEmail] = useState("");
    const [resetCode, setResetCode] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [resetCodeSent, setResetCodeSent] = useState(false);
    const [resetLoading, setResetLoading] = useState(false);
    const [resetError, setResetError] = useState("");
    const [resetSuccess, setResetSuccess] = useState("");

    const hasUnsavedChanges =
        name !== savedProfile.name ||
        dateOfBirth !== savedProfile.dateOfBirth ||
        preferredLanguage !== savedProfile.preferredLanguage ||
        ethnicity !== savedProfile.ethnicity ||
        medicalHistory !== savedProfile.medicalHistory ||
        allergies !== savedProfile.allergies ||
        medications !== savedProfile.medications ||
        (isPatient && selectedDoctor !== savedProfile.selectedDoctor);

    const blocker = useBlocker(hasUnsavedChanges);

    useEffect(() => {
        let active = true;
        const loadProfile = async () => {
            try {
                const userData: UserDetails = await apiFetch("/users/me");
                if (!active) return;

                let myDoctor: MyDoctorResponse = { doctor: null };
                let availableDoctors: Doctor[] = [];

                // These endpoints are patient-only. GP loading errors should
                // not prevent either role from loading their own profile.
                if (isPatient) {
                    try {
                        const [doctorData, myDoctorData] = await Promise.all([
                            apiFetch("/users/doctors"),
                            apiFetch("/users/me/doctor"),
                        ]);
                        if (!active) return;
                        availableDoctors = Array.isArray(doctorData.doctors)
                            ? doctorData.doctors
                            : [];
                        myDoctor = myDoctorData as MyDoctorResponse;
                    } catch (error) {
                        if (!active) return;
                        console.error("Failed to load GP selection:", error);
                        setDoctorMessage("Unable to load your doctor selection.");
                    }
                }

                if (!active) return;
                setUser(userData);
                setDoctors(availableDoctors);
                setSelectedDoctor(
                    myDoctor.doctor?.id != null
                        ? String(myDoctor.doctor.id)
                        : ""
                );

                const initialName = userData.name || "";
                const initialDateOfBirth =
                    userData.date_of_birth || "";
                const initialPreferredLanguage =
                    userData.preferred_language || "";
                const initialEthnicity =
                    userData.ethnicity || "";
                const initialMedicalHistory =
                    userData.medical_history || "";

                const initialAllergies =
                    Array.isArray(userData.allergies)
                        ? userData.allergies.join(", ")
                        : "";

                const initialMedications =
                    Array.isArray(userData.medications)
                        ? userData.medications.join(", ")
                        : "";

                const initialDoctor =
                    myDoctor?.doctor?.id != null
                        ? String(myDoctor.doctor.id)
                        : "";

                setName(initialName);
                setDateOfBirth(initialDateOfBirth);
                setPreferredLanguage(initialPreferredLanguage);
                setEthnicity(initialEthnicity);
                setMedicalHistory(initialMedicalHistory);
                setAllergies(initialAllergies);
                setMedications(initialMedications);

                setSavedProfile({
                    name: initialName,
                    dateOfBirth: initialDateOfBirth,
                    preferredLanguage: initialPreferredLanguage,
                    ethnicity: initialEthnicity,
                    medicalHistory: initialMedicalHistory,
                    allergies: initialAllergies,
                    medications: initialMedications,
                    selectedDoctor: initialDoctor,
                });
            } catch (error) {
                if (!active) return;
                console.error(
                    "Failed to load profile:",
                    error
                );
                setMessage(
                    "Failed to load your profile."
                );
            } finally {
                if (active) setLoading(false);
            }
        };

        void loadProfile();
        return () => { active = false; };
    }, [isPatient]);

    useEffect(() => {
        const handleBeforeUnload = (
            event: BeforeUnloadEvent
        ) => {
            if (!hasUnsavedChanges) {
                return;
            }

            event.preventDefault();
            event.returnValue = "";
        };

        window.addEventListener(
            "beforeunload",
            handleBeforeUnload
        );

        return () => {
            window.removeEventListener(
                "beforeunload",
                handleBeforeUnload
            );
        };
    }, [hasUnsavedChanges]);

    const handleSaveDetails = async (
        event: React.FormEvent<HTMLFormElement>
    ) => {
        event.preventDefault();

        setSaving(true);
        setMessage("");

        try {
            await apiFetch("/users/me", {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    name,
                    date_of_birth: dateOfBirth || null,
                    preferred_language: preferredLanguage,
                    ethnicity: ethnicity || null,
                    medical_history:
                        medicalHistory || null,
                    allergies: allergies
                        .split(",")
                        .map((item) => item.trim())
                        .filter(Boolean),
                    medications: medications
                        .split(",")
                        .map((item) => item.trim())
                        .filter(Boolean),
                }),
            });

            localStorage.setItem(
                "userName",
                name
            );

            setSavedProfile((current) => ({
                ...current,
                name,
                dateOfBirth,
                preferredLanguage,
                ethnicity,
                medicalHistory,
                allergies,
                medications,
            }));

            setMessage(
                "Your details have been saved."
            );

            setTimeout(() => {
                window.location.reload();
            }, 500);
        } catch (error) {
            console.error(
                "Failed to update profile:",
                error
            );
            setMessage(
                "Failed to save your details."
            );
        } finally {
            setSaving(false);
        }
    };

    const handleAssignDoctor = async () => {
        if (!isPatient) return;

        if (!selectedDoctor) {

            setDoctorMessage(
                "Please select a doctor."
            );
            return;
        }

        setSavingDoctor(true);
        setDoctorMessage("");

        try {
            await apiFetch("/users/me/doctor", {
                method: "PUT",
                headers: {
                    "Content-Type":
                        "application/json",
                },
                body: JSON.stringify({
                    doctor_id:
                        Number(selectedDoctor),
                }),
            });

            setSavedProfile((current) => ({
                ...current,
                selectedDoctor,
            }));
            setDoctorMessage(
                "Your doctor has been updated."
            );
        } catch (error) {
            console.error(
                "Failed to assign doctor:",
                error
            );
            setDoctorMessage(
                "Failed to update your doctor."
            );
        } finally {
            setSavingDoctor(false);
        }
    };

    const handleOpenPasswordReset = () => {
        setResetEmail(user?.email || "");
        setResetCode("");
        setNewPassword("");
        setConfirmPassword("");
        setResetCodeSent(false);
        setResetError("");
        setResetSuccess("");
        setShowPasswordReset(true);
    };

    const handleSendResetCode = async () => {
        setResetError("");
        setResetSuccess("");

        const email =
            user?.email?.trim() || "";

        if (!email) {
            setResetError(
                "Unable to find your account email address."
            );
            return;
        }

        setResetLoading(true);

        try {
            await apiFetch(
                "/auth/forgot-password",
                {
                    method: "POST",
                    body: JSON.stringify({
                        email,
                        username:
                            user?.username || "",
                    }),
                }
            );

            setResetEmail(email);
            setResetCode("");
            setResetCodeSent(true);
        } catch (error) {
            console.error(
                "Forgot password error:",
                error
            );

            if (error instanceof Error) {
                setResetError(error.message);
            } else {
                setResetError(
                    "Unable to send password reset code."
                );
            }
        } finally {
            setResetLoading(false);
        }
    };

    const handleResetPassword = async () => {
        setResetError("");
        setResetSuccess("");

        const email =
            user?.email?.trim() || "";
        const code = resetCode.trim();

        if (!email) {
            setResetError(
                "Unable to find your account email address."
            );
            return;
        }

        if (code.length !== 6) {
            setResetError(
                "Please enter the 6-digit reset code."
            );
            return;
        }

        if (!newPassword) {
            setResetError(
                "Please enter a new password."
            );
            return;
        }

        if (!confirmPassword) {
            setResetError(
                "Please confirm your new password."
            );
            return;
        }

        if (newPassword !== confirmPassword) {
            setResetError(
                "Passwords do not match."
            );
            return;
        }

        setResetLoading(true);

        try {
            await apiFetch(
                "/auth/reset-password",
                {
                    method: "POST",
                    body: JSON.stringify({
                        email,
                        code,
                        new_password:
                        newPassword,
                        confirm_password:
                        confirmPassword,
                    }),
                }
            );

            setResetSuccess(
                "Password reset successfully."
            );

            setResetCode("");
            setNewPassword("");
            setConfirmPassword("");

            setTimeout(() => {
                setShowPasswordReset(false);
                setResetCodeSent(false);
                setResetSuccess("");
                setResetError("");
            }, 1500);
        } catch (error) {
            console.error(
                "Reset password error:",
                error
            );

            if (error instanceof Error) {
                setResetError(error.message);
            } else {
                setResetError(
                    "Unable to reset password."
                );
            }
        } finally {
            setResetLoading(false);
        }
    };

    const handleClosePasswordReset = () => {
        if (resetLoading) {
            return;
        }

        setShowPasswordReset(false);
        setResetEmail("");
        setResetCode("");
        setNewPassword("");
        setConfirmPassword("");
        setResetCodeSent(false);
        setResetError("");
        setResetSuccess("");
    };

    if (loading) {
        return (
            <main>
                <div className="edit-profile">
                    <p className="profile-loading">
                        Loading your profile...
                    </p>
                </div>
            </main>
        );
    }

    if (!user) {
        return (
            <main>
                <div className="edit-profile">
                    <p role="alert">{message || "Unable to load your profile."}</p>
                </div>
            </main>
        );
    }

    return (
        <main>
            <div className="edit-profile">

                <section className="profile-header">
                    <h1>Edit profile</h1>
                    <p>
                        Manage your personal and medical
                        information.
                    </p>
                </section>

                <form
                    className="profile-section"
                    onSubmit={handleSaveDetails}
                >
                    <div className="section-heading">
                        <h2>Personal details</h2>
                        <p>
                            Update the information associated
                            with your account.
                        </p>
                    </div>

                    <div className="profile-grid">

                        <div className="profile-field">
                            <label htmlFor="name">
                                Name
                            </label>

                            <input
                                id="name"
                                type="text"
                                value={name}
                                onChange={(event) =>
                                    setName(
                                        event.target.value
                                    )
                                }
                            />
                        </div>

                        <div className="profile-field">
                            <label htmlFor="date-of-birth">
                                Date of birth
                            </label>

                            <input
                                id="date-of-birth"
                                type="date"
                                value={dateOfBirth}
                                onChange={(event) =>
                                    setDateOfBirth(
                                        event.target.value
                                    )
                                }
                            />

                            <span className="field-note">
                                Age: {user?.age ?? "—"}
                            </span>
                        </div>

                        <div className="profile-field">
                            <label htmlFor="email">
                                Email
                            </label>

                            <input
                                id="email"
                                type="email"
                                value={
                                    user?.email || ""
                                }
                                disabled
                            />

                            <span className="field-note">
                                Email cannot be changed.
                            </span>
                        </div>

                        <div className="profile-field">
                            <label htmlFor="username">
                                Username
                            </label>

                            <input
                                id="username"
                                type="text"
                                value={
                                    user?.username || ""
                                }
                                disabled
                            />

                            <span className="field-note">
                                Username cannot be changed.
                            </span>
                        </div>

                        <div className="profile-field">
                            <label htmlFor="language">
                                Chatbot Language
                            </label>

                            <select
                                id="language"
                                value={
                                    preferredLanguage
                                }
                                onChange={(event) =>
                                    setPreferredLanguage(
                                        event.target.value
                                    )
                                }
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

                        <div className="profile-field">
                            <label htmlFor="ethnicity">
                                Ethnicity
                            </label>

                            <input
                                id="ethnicity"
                                type="text"
                                value={ethnicity}
                                onChange={(event) =>
                                    setEthnicity(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter your ethnicity"
                            />
                        </div>

                    </div>

                    <div className="section-heading medical-heading">
                        <h2>Medical information</h2>
                        <p>
                            Keep your medical information up to
                            date for your consultations.
                        </p>
                    </div>

                    <div className="medical-fields">

                        <div className="profile-field">
                            <label htmlFor="medical-history">
                                Medical history
                            </label>

                            <textarea
                                id="medical-history"
                                value={
                                    medicalHistory
                                }
                                onChange={(event) =>
                                    setMedicalHistory(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter any relevant medical history"
                                rows={5}
                            />
                        </div>

                        <div className="profile-field">
                            <label htmlFor="allergies">
                                Allergies
                            </label>

                            <textarea
                                id="allergies"
                                value={allergies}
                                onChange={(event) =>
                                    setAllergies(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. Penicillin, peanuts"
                                rows={3}
                            />

                            <span className="field-note">
                                Separate multiple allergies
                                with commas.
                            </span>
                        </div>

                        <div className="profile-field">
                            <label htmlFor="medications">
                                Medications
                            </label>

                            <textarea
                                id="medications"
                                value={medications}
                                onChange={(event) =>
                                    setMedications(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. Paracetamol, Ibuprofen"
                                rows={3}
                            />

                            <span className="field-note">
                                Separate multiple medications
                                with commas.
                            </span>
                        </div>

                    </div>

                    <div className="profile-actions">
                        <button
                            type="submit"
                            className="save-button"
                            disabled={saving}
                        >
                            {saving
                                ? "Saving..."
                                : "Save changes"}
                        </button>

                        {message && (
                            <span className="save-message">
                                {message}
                            </span>
                        )}
                    </div>
                </form>

                {isPatient && (
                    <section className="profile-section">
                        <div className="section-heading">
                            <h2>Your doctor</h2>
                            <p>
                                Choose the doctor assigned to your
                                consultations.
                            </p>
                        </div>

                        <div className="doctor-selection">

                            <div className="profile-field">
                                <label htmlFor="doctor">
                                    Select doctor
                                </label>

                                <select
                                    id="doctor"
                                    value={selectedDoctor}
                                    onChange={(event) =>
                                        setSelectedDoctor(
                                            event.target.value
                                        )
                                    }
                                >
                                    <option value="">
                                        Select a doctor
                                    </option>

                                    {doctors.map((doctor) => (
                                        <option
                                            key={doctor.id}
                                            value={String(
                                                doctor.id
                                            )}
                                        >
                                            {doctor.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="doctor-actions">
                                <button
                                    type="button"
                                    className="save-button"
                                    onClick={
                                        handleAssignDoctor
                                    }
                                    disabled={
                                        savingDoctor
                                    }
                                >
                                    {savingDoctor
                                        ? "Updating..."
                                        : "Update doctor"}
                                </button>

                                {doctorMessage && (
                                    <span className="save-message">
                                    {doctorMessage}
                                </span>
                                )}
                            </div>

                        </div>
                    </section>

                )}

                <section className="profile-section password-section">
                    <div className="section-heading">
                        <h2>Password</h2>
                        <p>
                            Update your account password.
                        </p>
                    </div>

                    <button
                        type="button"
                        className="password-change-link"
                        onClick={
                            handleOpenPasswordReset
                        }
                    >
                        Change password
                    </button>
                </section>

            </div>

            {showPasswordReset && (
                <div className="password-reset-overlay">

                    <div className="password-reset-modal">

                        {!resetCodeSent ? (
                            <>
                                <h2>
                                    Change your password
                                </h2>

                                <p className="password-reset-description">
                                    We'll send a verification
                                    code to the email address
                                    associated with your
                                    account:
                                </p>

                                <p className="password-reset-email">
                                    {user?.email}
                                </p>

                                {resetError && (
                                    <p className="password-reset-error">
                                        {resetError}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="password-reset-primary"
                                    onClick={
                                        handleSendResetCode
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                >
                                    {resetLoading
                                        ? "Sending..."
                                        : "Send verification code"}
                                </button>

                                <button
                                    type="button"
                                    className="password-reset-cancel"
                                    onClick={
                                        handleClosePasswordReset
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <>
                                <h2>
                                    Change your password
                                </h2>

                                <p className="password-reset-description">
                                    We've sent a 6-digit
                                    verification code to:
                                </p>

                                <p className="password-reset-email">
                                    {user?.email}
                                </p>

                                <label htmlFor="reset-code">
                                    Verification code
                                </label>

                                <input
                                    id="reset-code"
                                    className="password-reset-code"
                                    type="text"
                                    inputMode="numeric"
                                    autoComplete="one-time-code"
                                    maxLength={6}
                                    placeholder="000000"
                                    value={resetCode}
                                    onChange={(event) =>
                                        setResetCode(
                                            event.target.value
                                                .replace(
                                                    /\D/g,
                                                    ""
                                                )
                                                .slice(
                                                    0,
                                                    6
                                                )
                                        )
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                    autoFocus
                                />

                                <label htmlFor="new-password">
                                    New password
                                </label>

                                <input
                                    id="new-password"
                                    type="password"
                                    placeholder="New password"
                                    value={newPassword}
                                    onChange={(event) =>
                                        setNewPassword(
                                            event.target.value
                                        )
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                />

                                <label htmlFor="confirm-password">
                                    Confirm new password
                                </label>

                                <input
                                    id="confirm-password"
                                    type="password"
                                    placeholder="Confirm new password"
                                    value={
                                        confirmPassword
                                    }
                                    onChange={(event) =>
                                        setConfirmPassword(
                                            event.target.value
                                        )
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                />

                                {resetError && (
                                    <p className="password-reset-error">
                                        {resetError}
                                    </p>
                                )}

                                {resetSuccess && (
                                    <p className="password-reset-success">
                                        {resetSuccess}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="password-reset-primary"
                                    onClick={
                                        handleResetPassword
                                    }
                                    disabled={
                                        resetLoading ||
                                        resetCode.length !==
                                        6 ||
                                        !newPassword ||
                                        !confirmPassword
                                    }
                                >
                                    {resetLoading
                                        ? "Updating..."
                                        : "Update password"}
                                </button>

                                <button
                                    type="button"
                                    className="password-reset-resend"
                                    onClick={
                                        handleSendResetCode
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                >
                                    Resend code
                                </button>

                                <button
                                    type="button"
                                    className="password-reset-cancel"
                                    onClick={
                                        handleClosePasswordReset
                                    }
                                    disabled={
                                        resetLoading
                                    }
                                >
                                    Cancel
                                </button>
                            </>
                        )}

                    </div>

                </div>
            )}

            {blocker.state === "blocked" && (
                <div className="unsaved-changes-overlay">
                    <div className="unsaved-changes-modal">
                        <h2>Unsaved changes</h2>

                        <p>
                            You have unsaved changes to your settings.
                            Please save your settings before leaving.
                        </p>

                        <div className="unsaved-changes-actions">
                            <button
                                type="button"
                                className="unsaved-changes-stay"
                                onClick={() => blocker.reset()}
                            >
                                Stay on page
                            </button>

                            <button
                                type="button"
                                className="unsaved-changes-discard"
                                onClick={() => blocker.proceed()}
                            >
                                Leave without saving
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <section className="credits-section">
                <div className="section-heading">
                    <h2>Credits</h2>
                    <p>Third-party software used in this application.</p>
                </div>

                <p className="credits-text">
                    This application uses{" "}
                    <a
                        href="https://github.com/met4citizen/TalkingHead"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        TalkingHead (3D)
                    </a>{" "}
                    by Mika Suominen for real-time 3D avatar rendering
                    and lip-sync.
                    <br />
                    Copyright (c) 2023-2024 Mika Suominen.
                    Licensed under the MIT License.
                </p>
            </section>
        </main>
    );
}

export default EditProfile;
