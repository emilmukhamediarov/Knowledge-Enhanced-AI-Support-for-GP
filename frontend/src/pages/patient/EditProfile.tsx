import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";
import "./EditProfile.css";

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

function EditProfile() {
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

    const [message, setMessage] = useState("");
    const [doctorMessage, setDoctorMessage] = useState("");

    useEffect(() => {
        const loadProfile = async () => {
            try {
                const [userData, doctorData] = await Promise.all([
                    apiFetch("/users/me"),
                    apiFetch("/users/doctors"),
                ]);

                setUser(userData);
                setDoctors(
                    Array.isArray(doctorData.doctors)
                        ? doctorData.doctors
                        : []
                );

                setName(userData.name || "");
                setDateOfBirth(userData.date_of_birth || "");
                setPreferredLanguage(
                    userData.preferred_language || ""
                );
                setEthnicity(userData.ethnicity || "");
                setMedicalHistory(userData.medical_history || "");

                setAllergies(
                    Array.isArray(userData.allergies)
                        ? userData.allergies.join(", ")
                        : ""
                );

                setMedications(
                    Array.isArray(userData.medications)
                        ? userData.medications.join(", ")
                        : ""
                );
            } catch (error) {
                console.error("Failed to load profile:", error);
                setMessage("Failed to load your profile.");
            } finally {
                setLoading(false);
            }
        };

        void loadProfile();
    }, []);

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
                    date_of_birth: dateOfBirth,
                    preferred_language: preferredLanguage,
                    ethnicity: ethnicity || null,
                    medical_history: medicalHistory || null,
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

            localStorage.setItem("userName", name);
            setMessage("Your details have been saved.");
        } catch (error) {
            console.error("Failed to update profile:", error);
            setMessage("Failed to save your details.");
        } finally {
            setSaving(false);
        }
    };

    const handleAssignDoctor = async () => {
        if (!selectedDoctor) {
            setDoctorMessage("Please select a doctor.");
            return;
        }

        setSavingDoctor(true);
        setDoctorMessage("");

        try {
            await apiFetch("/users/me/doctor", {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    doctor_id: Number(selectedDoctor),
                }),
            });

            setDoctorMessage("Your doctor has been updated.");
        } catch (error) {
            console.error("Failed to assign doctor:", error);
            setDoctorMessage("Failed to update your doctor.");
        } finally {
            setSavingDoctor(false);
        }
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

    return (
        <main>
            <div className="edit-profile">

                <section className="profile-header">
                    <h1>Edit profile</h1>
                    <p>
                        Manage your personal and medical information.
                    </p>
                </section>

                <form
                    className="profile-section"
                    onSubmit={handleSaveDetails}
                >
                    <div className="section-heading">
                        <h2>Personal details</h2>
                        <p>
                            Update the information associated with your
                            account.
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
                                    setName(event.target.value)
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
                                    setDateOfBirth(event.target.value)
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
                                value={user?.email || ""}
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
                                value={user?.username || ""}
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
                                value={preferredLanguage}
                                onChange={(event) =>
                                    setPreferredLanguage(
                                        event.target.value
                                    )
                                }
                            >
                                <option value="en-US">
                                    English (US)
                                </option>
                                <option value="en-NZ">
                                    English (New Zealand)
                                </option>
                                <option value="en-GB">
                                    English (UK)
                                </option>
                                <option value="mi-NZ">
                                    Māori
                                </option>
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
                                    setEthnicity(event.target.value)
                                }
                                placeholder="Enter your ethnicity"
                            />
                        </div>

                    </div>

                    <div className="section-heading medical-heading">
                        <h2>Medical information</h2>
                        <p>
                            Keep your medical information up to date
                            for your consultations.
                        </p>
                    </div>

                    <div className="medical-fields">

                        <div className="profile-field">
                            <label htmlFor="medical-history">
                                Medical history
                            </label>

                            <textarea
                                id="medical-history"
                                value={medicalHistory}
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
                                    setAllergies(event.target.value)
                                }
                                placeholder="e.g. Penicillin, peanuts"
                                rows={3}
                            />

                            <span className="field-note">
                                Separate multiple allergies with commas.
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
                                    setMedications(event.target.value)
                                }
                                placeholder="e.g. Paracetamol, Ibuprofen"
                                rows={3}
                            />

                            <span className="field-note">
                                Separate multiple medications with commas.
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
                                        value={doctor.id}
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
                                onClick={handleAssignDoctor}
                                disabled={savingDoctor}
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

            </div>
        </main>
    );
}

export default EditProfile;