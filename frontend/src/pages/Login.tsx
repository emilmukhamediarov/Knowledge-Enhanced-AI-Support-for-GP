/*NOTES
URLs:

/login

/patient
/patient/chat

/doctor
/doctor/consultations
/doctor/consultations/123
*/
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const navigate = useNavigate();

    // THIS NEEDS TO CHANGE ONCE AUTHENTICATION AND ROLES IS IMPLEMENTED!!!!
    const handleLogin = () => {
        if (username == "doctor" && password == "password123") {
            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("role", "doctor");
            navigate("/doctorhome");
        } else if (username == "patient" && password == "password123") {
            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("role", "patient");
            navigate("/patienthome");
        } else if (username == "admin" && password == "password123"){
            localStorage.setItem("loggedIn", "true");
            localStorage.setItem("role", "admin");
            navigate("/home");
        } else {
            setError("Invalid username or password");
        }
    };

    return (
        <div className="login-page">
            <div className="login-form">
                <h1>Login</h1>
                <label>Email</label>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="username-form"
                />
                {/*FOR THIS: Add hiding of the password when typing*/}
                <label>Password</label>
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="password-form"
                />
                {/*FOR THIS: add the enter->Login too (copy from Chat)*/}
                <button onClick={handleLogin} className="login-button">
                    Login
                </button>
                {error && <p>{error}</p>}
            </div>
        </div>
    );

}

export default Login;