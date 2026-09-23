import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Register.css";
import { apiFetch } from "../api/client";
import ThemeToggle from "../components/ThemeToggle";

function Register() {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [verificationEmail, setVerificationEmail] = useState("");
    const [verificationCode, setVerificationCode] = useState("");

    const [showVerification, setShowVerification] = useState(false);
    const [codeSent, setCodeSent] = useState(false);

    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const [loading, setLoading] = useState(false);
    const [verificationLoading, setVerificationLoading] = useState(false);

    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();

        setError("");
        setSuccess("");

        if (!name.trim()) {
            setError("Please enter your name.");
            return;
        }

        if (!email.trim()) {
            setError("Please enter your email address.");
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

        try {
            // Send the verification code.
            await apiFetch("/auth/send-code", {
                method: "POST",
                body: JSON.stringify({
                    email: email.trim(),
                    username: username.trim(),
                }),
            });

            // Open the verification popup directly.
            setVerificationEmail(email.trim());
            setVerificationCode("");
            setCodeSent(true);
            setShowVerification(true);

        } catch (error) {
            console.error("Registration error:", error);

            if (error instanceof Error) {
                setError(error.message);
            } else {
                setError("Unable to create account.");
            }
        } finally {
            setLoading(false);
        }
    };


    const handleSendVerificationCode = async () => {
        setError("");
        setSuccess("");

        const emailToVerify = verificationEmail.trim();

        if (!emailToVerify) {
            setError("Please enter your email address.");
            return;
        }

        setVerificationLoading(true);

        try {
            await apiFetch("/auth/send-code", {
                method: "POST",
                body: JSON.stringify({
                    email: emailToVerify,
                }),
            });

            setVerificationCode("");
            setCodeSent(true);

        } catch (error) {
            console.error("Send verification code error:", error);

            if (error instanceof Error) {
                setError(error.message);
            } else {
                setError("Unable to send verification code.");
            }
        } finally {
            setVerificationLoading(false);
        }
    };

    const handleVerifyCode = async () => {
        setError("");
        setSuccess("");

        const emailToVerify = verificationEmail.trim();
        const code = verificationCode.trim();

        if (!emailToVerify) {
            setError("Please enter your email address.");
            return;
        }

        if (code.length !== 6) {
            setError("Please enter the 6-digit verification code.");
            return;
        }

        setVerificationLoading(true);

        try {
            // Call the register endpoint with the verification code to complete registration
            await apiFetch("/auth/register", {
                method: "POST",
                body: JSON.stringify({
                    name: name.trim(),
                    email: emailToVerify,
                    username: username.trim(),
                    password,
                    validation_code: code,
                }),
            });
            setShowVerification(false);
            setCodeSent(false);
            setVerificationCode("");
            setVerificationEmail("");

            setSuccess(
                "Account created successfully! You can now log in."
            );

        } catch (error) {
            console.error("Email verification error:", error);

            if (error instanceof Error) {
                setError(error.message);
            } else {
                setError("Unable to verify email.");
            }
        } finally {
            setVerificationLoading(false);
        }
    };

    const handleCloseVerification = () => {
        if (verificationLoading) {
            return;
        }

        setShowVerification(false);
        setVerificationCode("");
        setVerificationEmail("");
        setCodeSent(false);
        setError("");
    };

    return (
        <div className="register-page">

            <div className="register-form">

                <h1>Register</h1>

                <form onSubmit={handleRegister}>

                    <label htmlFor="name">Name</label>
                    <input
                        id="name"
                        type="text"
                        placeholder="Name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        disabled={loading}
                    />

                    <label htmlFor="email">Email</label>
                    <input
                        id="email"
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        disabled={loading}
                    />

                    <label htmlFor="username">Username</label>
                    <input
                        id="username"
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        disabled={loading}
                    />

                    <label htmlFor="password">Password</label>
                    <input
                        id="password"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        disabled={loading}
                    />

                    <label htmlFor="confirm-password">
                        Confirm Password
                    </label>

                    <input
                        id="confirm-password"
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
                        {loading ? "Creating account..." : "Register"}
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
                    disabled={loading}
                >
                    Already have an account? Login
                </button>



            </div>

            <div className="login-theme-toggle">
                <ThemeToggle />
            </div>


            {/* Email verification popup */}
            {showVerification && (
                <div className="verification-overlay">

                    <div className="verification-modal">

                        {!codeSent ? (
                            <>
                                <h2>Verify your email</h2>

                                <p className="verification-description">
                                    Enter the email address you registered
                                    with and we'll send you a verification
                                    code.
                                </p>

                                <label htmlFor="verification-email">
                                    Email
                                </label>

                                <input
                                    id="verification-email"
                                    type="email"
                                    placeholder="Email"
                                    value={verificationEmail}
                                    onChange={(e) =>
                                        setVerificationEmail(
                                            e.target.value
                                        )
                                    }
                                    disabled={verificationLoading}
                                    autoFocus
                                />

                                {error && (
                                    <p className="register-error">
                                        {error}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="register-button verification-button"
                                    onClick={handleSendVerificationCode}
                                    disabled={verificationLoading}
                                >
                                    {verificationLoading
                                        ? "Sending..."
                                        : "Send Verification Code"}
                                </button>

                                <button
                                    type="button"
                                    className="back-to-login verification-cancel"
                                    onClick={handleCloseVerification}
                                    disabled={verificationLoading}
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <>
                                <h2>Verify your email</h2>

                                <p className="verification-description">
                                    We've sent a 6-digit verification code
                                    to:
                                </p>

                                <p className="verification-email">
                                    {verificationEmail}
                                </p>

                                <label htmlFor="verification-code">
                                    Verification Code
                                </label>

                                <input
                                    id="verification-code"
                                    className="verification-input"
                                    type="text"
                                    inputMode="numeric"
                                    autoComplete="one-time-code"
                                    maxLength={6}
                                    placeholder="000000"
                                    value={verificationCode}
                                    onChange={(e) =>
                                        setVerificationCode(
                                            e.target.value
                                                .replace(/\D/g, "")
                                                .slice(0, 6)
                                        )
                                    }
                                    disabled={verificationLoading}
                                    autoFocus
                                />

                                {error && (
                                    <p className="register-error">
                                        {error}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="register-button verification-button"
                                    onClick={handleVerifyCode}
                                    disabled={
                                        verificationLoading ||
                                        verificationCode.length !== 6
                                    }
                                >
                                    {verificationLoading
                                        ? "Verifying..."
                                        : "Verify Email"}
                                </button>

                                <button
                                    type="button"
                                    className="resend-code-button"
                                    onClick={handleSendVerificationCode}
                                    disabled={verificationLoading}
                                >
                                    Resend Code
                                </button>

                                <button
                                    type="button"
                                    className="back-to-login verification-cancel"
                                    onClick={handleCloseVerification}
                                    disabled={verificationLoading}
                                >
                                    Cancel
                                </button>
                            </>
                        )}

                    </div>

                </div>
            )}

        </div>
    );
}

export default Register;