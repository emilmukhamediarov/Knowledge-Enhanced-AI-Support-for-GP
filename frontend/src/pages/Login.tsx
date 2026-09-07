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
        console.log("LOGIN BUTTON PRESSED");
        setError("");

        if (!username.trim() || !password) {
            setError("Please enter your username and password.");
            return;
        }

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

            console.log("Login response:", data);

            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("userId", String(data.user_id));
            localStorage.setItem("role", data.role);
            localStorage.setItem("userName", data.name);

            if (data.role === "doctor") {
                navigate("/doctorhome");
            } else if (data.role === "patient") {
                navigate("/patienthome");
            } else if (data.role === "admin") {
                navigate("/home");
            } else {
                setError(`Unknown user role: ${data.role}`);
            }
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