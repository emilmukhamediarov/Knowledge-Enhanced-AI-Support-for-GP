import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import "./FirstTimeSettingsModal.css";
import bitwiseLogo from "../assets/BitwiseLogo.svg";

interface FirstTimeSettingsModalProps {
    onComplete: () => void;
}

interface UserDetails {
    id: number;
    username: string;
    name: string;
    email: string;
    date_of_birth: string;
    age: number;
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

const TOTAL_SETUP_STEPS = 4;

export function FirstTimeSettingsModal({
                                           onComplete,
                                       }: FirstTimeSettingsModalProps) {
    // Step 1 = welcome
    // Steps 2–5 = actual setup steps
    const [step, setStep] = useState(1);

    const [user, setUser] = useState<UserDetails | null>(null);
    const [doctors, setDoctors] = useState<Doctor[]>([]);

    const [name, setName] = useState("");
    const [dateOfBirth, setDateOfBirth] = useState("");
    const [preferredLanguage, setPreferredLanguage] =
        useState("en-NZ");
    const [ethnicity, setEthnicity] = useState("");
    const [medicalHistory, setMedicalHistory] = useState("");
    const [allergies, setAllergies] = useState("");
    const [medications, setMedications] = useState("");
    const [selectedDoctor, setSelectedDoctor] = useState("");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadProfile = async () => {
            try {
                const [
                    userData,
                    doctorData,
                    myDoctorData,
                ] = await Promise.all([
                    apiFetch("/users/me"),
                    apiFetch("/users/doctors"),
                    apiFetch("/users/me/doctor"),
                ]);

                const profile = userData as UserDetails;

                setUser(profile);

                setDoctors(
                    Array.isArray(doctorData?.doctors)
                        ? doctorData.doctors
                        : []
                );

                const myDoctor =
                    myDoctorData as MyDoctorResponse;

                setSelectedDoctor(
                    myDoctor?.doctor?.id != null
                        ? String(myDoctor.doctor.id)
                        : ""
                );

                setName(profile.name || "");

                setDateOfBirth(
                    profile.date_of_birth || ""
                );

                setPreferredLanguage(
                    profile.preferred_language || "en-NZ"
                );

                setEthnicity(
                    profile.ethnicity || ""
                );

                setMedicalHistory(
                    profile.medical_history || ""
                );

                setAllergies(
                    Array.isArray(profile.allergies)
                        ? profile.allergies.join(", ")
                        : ""
                );

                setMedications(
                    Array.isArray(profile.medications)
                        ? profile.medications.join(", ")
                        : ""
                );
            } catch (err) {
                console.error(
                    "Failed to load setup information:",
                    err
                );

                setError(
                    "We couldn't load your profile. Please try again."
                );
            } finally {
                setLoading(false);
            }
        };

        void loadProfile();
    }, []);

    const calculateAge = (date: string) => {
        if (!date) {
            return null;
        }

        const today = new Date();
        const birthDate = new Date(date);

        if (Number.isNaN(birthDate.getTime())) {
            return null;
        }

        let age =
            today.getFullYear() -
            birthDate.getFullYear();

        const monthDifference =
            today.getMonth() -
            birthDate.getMonth();

        if (
            monthDifference < 0 ||
            (monthDifference === 0 &&
                today.getDate() <
                birthDate.getDate())
        ) {
            age--;
        }

        return age;
    };

    const saveProfileDetails = async () => {
        const allergyList = allergies
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean);

        const medicationList = medications
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean);

        await apiFetch("/users/me", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                name,
                date_of_birth: dateOfBirth,
                preferred_language: preferredLanguage,
                ethnicity: ethnicity || null,
                medical_history: medicalHistory || null,
                allergies: allergyList,
                medications: medicationList,
            }),
        });

        if (user) {
            setUser({
                ...user,
                name,
                date_of_birth: dateOfBirth,
                preferred_language: preferredLanguage,
                ethnicity: ethnicity || null,
                medical_history: medicalHistory || null,
                allergies: allergyList,
                medications: medicationList,
            });
        }

        localStorage.setItem("userName", name);
    };

    const handleContinue = async () => {
        setError("");

        // Welcome
        if (step === 1) {
            setStep(2);
            return;
        }

        // Personal details
        if (step === 2) {
            if (!name.trim()) {
                setError("Please enter your name.");
                return;
            }

            if (!dateOfBirth) {
                setError(
                    "Please enter your date of birth."
                );
                return;
            }

            setSaving(true);

            try {
                await saveProfileDetails();
                setStep(3);
            } catch (err) {
                console.error(
                    "Failed to save personal details:",
                    err
                );

                setError(
                    "Failed to save your details. Please try again."
                );
            } finally {
                setSaving(false);
            }

            return;
        }

        // Preferences
        if (step === 3) {
            setSaving(true);

            try {
                await saveProfileDetails();
                setStep(4);
            } catch (err) {
                console.error(
                    "Failed to save preferences:",
                    err
                );

                setError(
                    "Failed to save your preferences. Please try again."
                );
            } finally {
                setSaving(false);
            }

            return;
        }

        // Medical information
        if (step === 4) {
            setSaving(true);

            try {
                await saveProfileDetails();
                setStep(5);
            } catch (err) {
                console.error(
                    "Failed to save medical information:",
                    err
                );

                setError(
                    "Failed to save your medical information. Please try again."
                );
            } finally {
                setSaving(false);
            }

            return;
        }

        // Choose doctor
        if (step === 5) {
            if (!selectedDoctor) {
                setError(
                    "Please select a doctor before completing setup."
                );
                return;
            }

            setSaving(true);

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

                onComplete();
            } catch (err) {
                console.error(
                    "Failed to assign doctor:",
                    err
                );

                setError(
                    "Failed to assign your doctor. Please try again."
                );
            } finally {
                setSaving(false);
            }
        }
    };

    const handleBack = () => {
        if (saving || step <= 2) {
            return;
        }

        setError("");
        setStep(
            (currentStep) => currentStep - 1
        );
    };

    const renderStepIndicator = () => {
        return (
            <div
                className="setup-progress"
                aria-label={`Step ${
                    step - 1
                } of ${TOTAL_SETUP_STEPS}`}
            >
                {Array.from(
                    {
                        length: TOTAL_SETUP_STEPS,
                    },
                    (_, index) => {
                        const stepNumber =
                            index + 1;

                        const actualStep =
                            stepNumber + 1;

                        const isActive =
                            actualStep === step;

                        const isComplete =
                            actualStep < step;

                        return (
                            <div
                                key={stepNumber}
                                className={`setup-progress-item ${
                                    isActive
                                        ? "active"
                                        : ""
                                } ${
                                    isComplete
                                        ? "complete"
                                        : ""
                                }`}
                            >
                                <span className="setup-progress-dot">
                                    {isComplete
                                        ? "✓"
                                        : stepNumber}
                                </span>

                                {stepNumber <
                                    TOTAL_SETUP_STEPS && (
                                        <span className="setup-progress-line" />
                                    )}
                            </div>
                        );
                    }
                )}
            </div>
        );
    };

    const renderStepContent = () => {
        // Step 2: Personal details
        if (step === 2) {
            const age =
                calculateAge(dateOfBirth);

            return (
                <div className="setup-step-content">
                    <div className="setup-step-heading">
                        <span>Step 1 of 4</span>

                        <h2>Personal details</h2>

                        <p>
                            Tell us a little about
                            yourself.
                        </p>
                    </div>

                    <div className="setup-fields">
                        <div className="setup-field">
                            <label htmlFor="setup-name">
                                Name
                            </label>

                            <input
                                id="setup-name"
                                type="text"
                                value={name}
                                onChange={(event) =>
                                    setName(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter your name"
                                autoFocus
                            />
                        </div>

                        <div className="setup-field">
                            <label htmlFor="setup-dob">
                                Date of birth
                            </label>

                            <input
                                id="setup-dob"
                                type="date"
                                value={dateOfBirth}
                                onChange={(event) =>
                                    setDateOfBirth(
                                        event.target.value
                                    )
                                }
                            />

                            <span className="setup-field-note">
                                Age:{" "}
                                {age ?? "—"}
                            </span>
                        </div>

                        <div className="setup-field">
                            <label htmlFor="setup-email">
                                Email
                            </label>

                            <input
                                id="setup-email"
                                type="email"
                                value={
                                    user?.email || ""
                                }
                                disabled
                            />

                            <span className="setup-field-note">
                                Email cannot be changed.
                            </span>
                        </div>

                        <div className="setup-field">
                            <label htmlFor="setup-username">
                                Username
                            </label>

                            <input
                                id="setup-username"
                                type="text"
                                value={
                                    user?.username || ""
                                }
                                disabled
                            />

                            <span className="setup-field-note">
                                Username cannot be changed.
                            </span>
                        </div>
                    </div>
                </div>
            );
        }

        // Step 3: Preferences
        if (step === 3) {
            return (
                <div className="setup-step-content">
                    <div className="setup-step-heading">
                        <span>Step 2 of 4</span>

                        <h2>Your preferences</h2>

                        <p>
                            Personalise how the GP Support system communicates with you.
                        </p>
                    </div>

                    <div className="setup-fields">
                        <div className="setup-field">
                            <label htmlFor="setup-language">
                                Chatbot language
                            </label>

                            <select
                                id="setup-language"
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

                        <div className="setup-field">
                            <label htmlFor="setup-ethnicity">
                                Ethnicity
                            </label>

                            <input
                                id="setup-ethnicity"
                                type="text"
                                value={ethnicity}
                                onChange={(event) =>
                                    setEthnicity(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter your ethnicity"
                            />

                            <span className="setup-field-note">
                                This information helps
                                personalise your care.
                            </span>
                        </div>
                    </div>
                </div>
            );
        }

        // Step 4: Medical information
        if (step === 4) {
            return (
                <div className="setup-step-content">
                    <div className="setup-step-heading">
                        <span>Step 3 of 4</span>

                        <h2>Medical information</h2>

                        <p>
                            This information can help
                            your doctor understand your
                            consultations.
                        </p>
                    </div>

                    <div className="setup-fields">
                        <div className="setup-field">
                            <label htmlFor="setup-medical-history">
                                Medical history
                            </label>

                            <textarea
                                id="setup-medical-history"
                                value={medicalHistory}
                                onChange={(event) =>
                                    setMedicalHistory(
                                        event.target.value
                                    )
                                }
                                placeholder="Enter any relevant medical history"
                                rows={4}
                            />
                        </div>

                        <div className="setup-field">
                            <label htmlFor="setup-allergies">
                                Allergies
                            </label>

                            <textarea
                                id="setup-allergies"
                                value={allergies}
                                onChange={(event) =>
                                    setAllergies(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. Penicillin, peanuts"
                                rows={2}
                            />

                            <span className="setup-field-note">
                                Separate multiple
                                allergies with commas.
                            </span>
                        </div>

                        <div className="setup-field">
                            <label htmlFor="setup-medications">
                                Medications
                            </label>

                            <textarea
                                id="setup-medications"
                                value={medications}
                                onChange={(event) =>
                                    setMedications(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. Paracetamol, Ibuprofen"
                                rows={2}
                            />

                            <span className="setup-field-note">
                                Separate multiple
                                medications with commas.
                            </span>
                        </div>
                    </div>
                </div>
            );
        }

        // Step 5: Choose doctor
        return (
            <div className="setup-step-content">
                <div className="setup-step-heading">
                    <span>Step 4 of 4</span>

                    <h2>Choose your doctor</h2>

                    <p>
                        Select the doctor assigned to
                        your consultations.
                    </p>
                </div>

                <div className="setup-doctor-content">
                    <div className="setup-doctor-icon">
                        +
                    </div>

                    <div>
                        <h3>
                            Who is your doctor?
                        </h3>

                        <p>
                            Your selected doctor will
                            receive consultations you
                            submit through GP Support.
                        </p>
                    </div>
                </div>

                <div className="setup-fields">
                    <div className="setup-field">
                        <label htmlFor="setup-doctor">
                            Select doctor
                        </label>

                        <select
                            id="setup-doctor"
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

                            {doctors.map(
                                (doctor) => (
                                    <option
                                        key={doctor.id}
                                        value={String(
                                            doctor.id
                                        )}
                                    >
                                        {doctor.name}
                                    </option>
                                )
                            )}
                        </select>
                    </div>
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <div
                className="setup-modal-overlay"
                role="dialog"
                aria-modal="true"
            >
                <div className="setup-modal setup-loading">
                    <div className="setup-spinner" />

                    <p>
                        Setting things up...
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div
            className="setup-modal-overlay"
            role="dialog"
            aria-modal="true"
            aria-labelledby="setup-title"
        >
            <div className="setup-modal">
                {step === 1 ? (
                    <>
                        <div className="setup-welcome-content">
                            <div className="setup-welcome-icon">
                                +
                            </div>

                            <h1 id="setup-title">
                                Welcome to Bitwise GP Support
                            </h1>

                            <img
                                src={bitwiseLogo}
                                alt="Bitwise Logo"
                                className="scaled-svg"
                            />

                            <p>
                                Let's get your profile ready before you get started.
                            </p>

                            <span>
                                It only takes a few minutes.
                            </span>
                        </div>

                        <div className="setup-actions">
                            <button
                                type="button"
                                className="setup-continue-button"
                                onClick={() =>
                                    void handleContinue()
                                }
                                disabled={saving}
                            >
                                {saving
                                    ? "Loading..."
                                    : "Get started →"}
                            </button>
                        </div>
                    </>
                ) : (
                    <>
                        <div className="setup-top-row">
                            <span className="setup-step-count">
                                {step - 1} of{" "}
                                {TOTAL_SETUP_STEPS}
                            </span>
                        </div>

                        {renderStepIndicator()}

                        <div id="setup-title">
                            {renderStepContent()}
                        </div>

                        {error && (
                            <p
                                className="setup-error"
                                role="alert"
                            >
                                {error}
                            </p>
                        )}

                        <div className="setup-actions">
                            <button
                                type="button"
                                className="setup-back-button"
                                onClick={handleBack}
                                disabled={saving}
                            >
                                Back
                            </button>

                            <button
                                type="button"
                                className="setup-continue-button"
                                onClick={() =>
                                    void handleContinue()
                                }
                                disabled={saving}
                            >
                                {saving
                                    ? "Saving..."
                                    : step === 5
                                        ? "Complete setup"
                                        : "Continue"}
                            </button>
                        </div>

                        <p className="setup-footer">
                            You can update these details later
                            in Settings.
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}