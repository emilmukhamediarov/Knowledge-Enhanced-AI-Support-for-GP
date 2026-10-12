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

    // Email verification
    const [showVerification, setShowVerification] = useState(false);
    const [verificationEmail, setVerificationEmail] = useState("");
    const [verificationCode, setVerificationCode] = useState("");
    const [codeSent, setCodeSent] = useState(false);
    const [verificationLoading, setVerificationLoading] = useState(false);

    // Password reset
    const [showResetPassword, setShowResetPassword] = useState(false);
    const [resetUsername, setResetUsername] = useState("");
    const [resetEmail, setResetEmail] = useState("");
    const [resetCode, setResetCode] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [resetCodeSent, setResetCodeSent] = useState(false);
    const [resetLoading, setResetLoading] = useState(false);
    const [resetError, setResetError] = useState("");
    const [resetSuccess, setResetSuccess] = useState("");

    const navigate = useNavigate();

    const completeLogin = (data: any) => {
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
    };

    const loginUser = async () => {
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

        completeLogin(data);
    };

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
            await loginUser();

        } catch (error) {
            console.error("Login error:", error);

            if (error instanceof Error) {
                const message = error.message.toLowerCase();

                /*
                 * The backend returns 403 when the user's email
                 * has not been verified.
                 */
                if (
                    message.includes("verify your email") ||
                    message.includes("verify email") ||
                    message.includes("email not verified")
                ) {
                    setVerificationEmail("");
                    setVerificationCode("");
                    setCodeSent(false);
                    setShowVerification(true);
                    setError("");
                } else {
                    setError(error.message);
                }
            } else {
                setError("Invalid username or password.");
            }
        } finally {
            setLoading(false);
        }
    };

    // --------------------------------------------------
    // Email verification
    // --------------------------------------------------

    const handleSendVerificationCode = async () => {
        setError("");

        const email = verificationEmail.trim();

        if (!email) {
            setError("Please enter your email address.");
            return;
        }

        setVerificationLoading(true);

        try {
            await apiFetch("/auth/send-code", {
                method: "POST",
                body: JSON.stringify({
                    email,
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

        const email = verificationEmail.trim();
        const code = verificationCode.trim();

        if (!email) {
            setError("Please enter your email address.");
            return;
        }

        if (code.length !== 6) {
            setError("Please enter the 6-digit verification code.");
            return;
        }

        setVerificationLoading(true);

        try {
            await apiFetch("/auth/verify-code", {
                method: "POST",
                body: JSON.stringify({
                    email,
                    code,
                }),
            });

            /*
             * Email has now been verified.
             * Automatically try the original login again.
             */
            await loginUser();

        } catch (error) {
            console.error("Email verification/login error:", error);

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
        setVerificationEmail("");
        setVerificationCode("");
        setCodeSent(false);
        setError("");
    };

    // --------------------------------------------------
    // Password reset
    // --------------------------------------------------

    const handleOpenResetPassword = () => {
        setShowResetPassword(true);

        setResetUsername(username);
        setResetEmail("");
        setResetCode("");
        setNewPassword("");
        setConfirmPassword("");
        setResetCodeSent(false);
        setResetError("");
        setResetSuccess("");

        setError("");
    };

    const handleSendResetCode = async () => {
        setResetError("");
        setResetSuccess("");

        const email = resetEmail.trim();
        const resetUser = resetUsername.trim();

        if (!resetUser) {
            setResetError("Please enter your username.");
            return;
        }

        if (!email) {
            setResetError("Please enter your email address.");
            return;
        }

        setResetLoading(true);

        try {
            await apiFetch("/auth/forgot-password", {
                method: "POST",
                body: JSON.stringify({
                    email,
                    username: resetUser,
                }),
            });

            setResetCode("");
            setResetCodeSent(true);

        } catch (error) {
            console.error("Forgot password error:", error);

            if (error instanceof Error) {
                setResetError(error.message);
            } else {
                setResetError("Unable to send password reset code.");
            }
        } finally {
            setResetLoading(false);
        }
    };

    const handleResetPassword = async () => {
        setResetError("");
        setResetSuccess("");

        const email = resetEmail.trim();
        const code = resetCode.trim();

        if (!email) {
            setResetError("Please enter your email address.");
            return;
        }

        if (code.length !== 6) {
            setResetError("Please enter the 6-digit reset code.");
            return;
        }

        if (!newPassword) {
            setResetError("Please enter a new password.");
            return;
        }

        if (!confirmPassword) {
            setResetError("Please confirm your new password.");
            return;
        }

        if (newPassword !== confirmPassword) {
            setResetError("Passwords do not match.");
            return;
        }

        setResetLoading(true);

        try {
            await apiFetch("/auth/reset-password", {
                method: "POST",
                body: JSON.stringify({
                    email,
                    code,
                    new_password: newPassword,
                    confirm_password: confirmPassword,
                }),
            });

            setResetSuccess(
                "Password reset successfully. You can now log in."
            );

            setResetCode("");
            setNewPassword("");
            setConfirmPassword("");

            /*
             * Give the user a moment to see the success message,
             * then close the reset popup.
             */
            setTimeout(() => {
                setShowResetPassword(false);
                setResetCodeSent(false);
                setResetSuccess("");
                setResetError("");
            }, 1500);

        } catch (error) {
            console.error("Reset password error:", error);

            if (error instanceof Error) {
                setResetError(error.message);
            } else {
                setResetError("Unable to reset password.");
            }
        } finally {
            setResetLoading(false);
        }
    };

    const handleCloseResetPassword = () => {
        if (resetLoading) {
            return;
        }

        setShowResetPassword(false);
        setResetUsername("");
        setResetEmail("");
        setResetCode("");
        setNewPassword("");
        setConfirmPassword("");
        setResetCodeSent(false);
        setResetError("");
        setResetSuccess("");
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
                        disabled={loading || verificationLoading}
                    />

                    <label>Password</label>

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="password-form"
                        disabled={loading || verificationLoading}
                    />

                    <button
                        type="submit"
                        className="login-button"
                        disabled={loading || verificationLoading}
                    >
                        {loading ? "Logging in..." : "Login"}
                    </button>

                </form>

                <button
                    type="button"
                    className="forgot-password-link"
                    onClick={handleOpenResetPassword}
                    disabled={loading || verificationLoading}
                >
                    Forgot password?
                </button>

                {error && !showVerification && (
                    <p>{error}</p>
                )}

                <div className="register-prompt">
                    <span>Don't have an account?</span>

                    <button
                        type="button"
                        onClick={() => navigate("/register")}
                        className="register-link"
                        disabled={loading || verificationLoading}
                    >
                        Register
                    </button>
                </div>

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
                                    Your email has not been verified yet.
                                    Enter the email address associated with
                                    your account to receive a verification
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
                                    <p className="login-verification-error">
                                        {error}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="login-button verification-button"
                                    onClick={handleSendVerificationCode}
                                    disabled={verificationLoading}
                                >
                                    {verificationLoading
                                        ? "Sending..."
                                        : "Send Verification Code"}
                                </button>

                                <button
                                    type="button"
                                    className="verification-cancel"
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
                                    <p className="login-verification-error">
                                        {error}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="login-button verification-button"
                                    onClick={handleVerifyCode}
                                    disabled={
                                        verificationLoading ||
                                        verificationCode.length !== 6
                                    }
                                >
                                    {verificationLoading
                                        ? "Verifying..."
                                        : "Verify & Login"}
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
                                    className="verification-cancel"
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


            {/* Password reset popup */}

            {showResetPassword && (
                <div className="verification-overlay">

                    <div className="verification-modal reset-password-modal">

                        {!resetCodeSent ? (
                            <>
                                <h2>Reset your password</h2>

                                <p className="verification-description">
                                    Enter your username and the email address
                                    associated with your account to receive a
                                    password reset code.
                                </p>

                                <label htmlFor="reset-username">
                                    Username
                                </label>

                                <input
                                    id="reset-username"
                                    type="text"
                                    placeholder="Username"
                                    value={resetUsername}
                                    onChange={(e) =>
                                        setResetUsername(e.target.value)
                                    }
                                    disabled={resetLoading}
                                    autoFocus
                                />

                                <label htmlFor="reset-email">
                                    Email
                                </label>

                                <input
                                    id="reset-email"
                                    type="email"
                                    placeholder="Email"
                                    value={resetEmail}
                                    onChange={(e) =>
                                        setResetEmail(e.target.value)
                                    }
                                    disabled={resetLoading}
                                />

                                {resetError && (
                                    <p className="login-verification-error">
                                        {resetError}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="login-button verification-button"
                                    onClick={handleSendResetCode}
                                    disabled={resetLoading}
                                >
                                    {resetLoading
                                        ? "Sending..."
                                        : "Send Reset Code"}
                                </button>

                                <button
                                    type="button"
                                    className="verification-cancel"
                                    onClick={handleCloseResetPassword}
                                    disabled={resetLoading}
                                >
                                    Cancel
                                </button>
                            </>
                        ) : (
                            <>
                                <h2>Reset your password</h2>

                                <p className="verification-description">
                                    We've sent a 6-digit reset code to:
                                </p>

                                <p className="verification-email">
                                    {resetEmail}
                                </p>

                                <label htmlFor="reset-code">
                                    Reset Code
                                </label>

                                <input
                                    id="reset-code"
                                    className="verification-input"
                                    type="text"
                                    inputMode="numeric"
                                    autoComplete="one-time-code"
                                    maxLength={6}
                                    placeholder="000000"
                                    value={resetCode}
                                    onChange={(e) =>
                                        setResetCode(
                                            e.target.value
                                                .replace(/\D/g, "")
                                                .slice(0, 6)
                                        )
                                    }
                                    disabled={resetLoading}
                                    autoFocus
                                />

                                <label htmlFor="new-password">
                                    New Password
                                </label>

                                <input
                                    id="new-password"
                                    type="password"
                                    placeholder="New password"
                                    value={newPassword}
                                    onChange={(e) =>
                                        setNewPassword(e.target.value)
                                    }
                                    disabled={resetLoading}
                                />

                                <label htmlFor="confirm-password">
                                    Confirm New Password
                                </label>

                                <input
                                    id="confirm-password"
                                    type="password"
                                    placeholder="Confirm new password"
                                    value={confirmPassword}
                                    onChange={(e) =>
                                        setConfirmPassword(e.target.value)
                                    }
                                    disabled={resetLoading}
                                />

                                {resetError && (
                                    <p className="login-verification-error">
                                        {resetError}
                                    </p>
                                )}

                                {resetSuccess && (
                                    <p className="reset-password-success">
                                        {resetSuccess}
                                    </p>
                                )}

                                <button
                                    type="button"
                                    className="login-button verification-button"
                                    onClick={handleResetPassword}
                                    disabled={
                                        resetLoading ||
                                        resetCode.length !== 6 ||
                                        !newPassword ||
                                        !confirmPassword
                                    }
                                >
                                    {resetLoading
                                        ? "Resetting..."
                                        : "Reset Password"}
                                </button>

                                <button
                                    type="button"
                                    className="resend-code-button"
                                    onClick={handleSendResetCode}
                                    disabled={resetLoading}
                                >
                                    Resend Code
                                </button>

                                <button
                                    type="button"
                                    className="verification-cancel"
                                    onClick={handleCloseResetPassword}
                                    disabled={resetLoading}
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

export default Login;