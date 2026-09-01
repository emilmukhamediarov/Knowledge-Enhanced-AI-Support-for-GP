import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";
import { apiFetch } from "../api/client";
import ThemeToggle from "../components/ThemeToggle";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();

        setError("");

        if (!username.trim() || !password) {
            setError("Please enter your username and password.");
            return;
        }

        // ====================================================================================
        // TEMPORARY HARD-CODED TEST ACCOUNTS
        if (username === "admin" && password === "password123") {
            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("role", "admin");
            navigate("/home");
            return;
        }
        if (username === "doctor" && password === "password123") {
            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("role", "doctor");
            navigate("/doctorhome");
            return;
        }
        if (username === "patient" && password === "password123") {
            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("role", "patient");
            navigate("/patienthome");
            return;
        }

        // ====================================================================================
        // REAL BACKEND LOGIN -- registered users are patients for now

        setLoading(true);

        try {
            const data = await apiFetch("/auth/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    username,
                    password,
                }),
            });

            localStorage.setItem("loggedIn", "true");
            localStorage.setItem(
                "access_token",
                data.access_token
            );
            localStorage.setItem(
                "userId",
                String(data.user_id)
            );

            // TEMPORARY:
            // All normally registered users are patients
            localStorage.setItem("role", "patient");

            navigate("/patienthome");

        } catch (error) {
            console.error("Login error:", error);
            setError("Invalid username or password.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <div className="login-form">
                <h1>Login</h1>

                <form onSubmit={handleLogin}>

                    <label>Username</label>
                    <input
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="username-form"
                        disabled={loading}
                    />

                    <label>Password</label>
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="password-form"
                        disabled={loading}
                    />

                    <button
                        type="submit"
                        className="login-button"
                        disabled={loading}
                    >
                        {loading ? "Logging in..." : "Login"}
                    </button>

                    {error && <p>{error}</p>}

                </form>

                <div className="register-prompt">
                    <span>Don't have an account?</span>
                    <button
                        type="button"
                        onClick={() => navigate("/register")}
                        className="register-link"
                    >
                        Register
                    </button>
                </div>
            </div>
            <div className="login-theme-toggle">
                <ThemeToggle />
            </div>
        </div>
    );
}

export default Login;