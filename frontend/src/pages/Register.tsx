import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";
import { apiFetch } from "../api/client";

function Register() {
    const [name, setName] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        if (!name.trim()) {
            setError("Please enter your name.");
            return;
        }

        if (!username.trim()) {
            setError("Please enter a username.");
            return;
        }

        if (!password) {
            setError("Please enter a password.");
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        setLoading(true);

        //TEMPORARILY HARDCODED TO 2, BUT SHOULD BE UPDATED TO BE INCREMENTED IN DB AUTOMATICALLY, NOT SENT IN JSON
        try {
            await apiFetch("/auth/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    id: 2,
                    name,
                    username,
                    password,
                }),
            });

            setSuccess("Account created successfully!");

            setTimeout(() => {
                navigate("/login");
            }, 2000);

        } catch (error) {
            console.error("Registration error:", error);
            setError("Unable to create account.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="register-page">
            <div className="register-form">

                <h1>Register</h1>

                <form onSubmit={handleRegister}>

                    <label>Name</label>
                    <input
                        type="text"
                        placeholder="Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        disabled={loading}
                    />

                    <label>Username</label>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={loading}
                    />

                    <label>Password</label>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={loading}
                    />

                    <label>Confirm Password</label>
                    <input
                        type="password"
                        placeholder="Confirm password"
                        value={confirmPassword}
                        onChange={(e) =>
                            setConfirmPassword(e.target.value)
                        }
                        disabled={loading}
                    />

                    <button
                        type="submit"
                        className="register-button"
                        disabled={loading}
                    >
                        {loading ? "Registering..." : "Register"}
                    </button>

                    {error && (
                        <p className="register-error">
                            {error}
                        </p>
                    )}

                    {success && (
                        <p className="register-success">
                            {success}
                        </p>
                    )}

                </form>

                <button
                    type="button"
                    onClick={() => navigate("/login")}
                    className="back-to-login"
                >
                    Already have an account? Login
                </button>

            </div>
        </div>
    );
}

export default Register;