import { useNavigate, NavLink } from "react-router-dom";
import "./Navbar.css";
import bitwiseLogo from '../assets/bitwiseLogo.svg';

function Navbar() {
    const navigate = useNavigate();
    const loggedIn = localStorage.getItem("loggedIn") === "true";
    const role = localStorage.getItem("role");
    const handleLogout = () => {
        localStorage.removeItem("loggedIn");
        localStorage.removeItem("role");
        navigate("/login");
    };

    return (
        <nav>
            <div>
                <img src={bitwiseLogo} alt="Bitwise Logo" className="scaled-svg" />
            </div>
            {loggedIn && (
                <div className="nav-links">
                    {role === "admin" && (<NavLink to="/home" className={({ isActive }) => isActive ? "active" : ""}>Home</NavLink>)}
                    {role === "patient" && (<NavLink to="/patienthome" className={({ isActive }) => isActive ? "active" : ""}>Home</NavLink>)}
                    {role === "patient" && (<NavLink to="/all-chats" className={({ isActive }) => isActive ? "active" : ""}>All Chats</NavLink>)}
                    {role === "doctor" && (<NavLink to="/doctorhome" className={({ isActive }) => isActive ? "active" : ""}>Home</NavLink>)}
                    {(role === "doctor" || role === "admin") && (<NavLink to="/summary" className={({ isActive }) => isActive ? "active" : ""}>Summary</NavLink>)}
                    {(role === "doctor" || role === "admin") && (<NavLink to="/rag" className={({ isActive }) => isActive ? "active" : ""}>Rag</NavLink>)}
                </div>
            )}
            {loggedIn && (
                <button className="logout-button" onClick={handleLogout}>
                    Logout
                </button>
            )}
        </nav>
    );
}

export default Navbar;


{/*
<div className="nav-links">
    {(role === "admin") && (<Link to="/home">Home</Link>)}
    {(role === "patient") && (<Link to="/patienthome">Home</Link>)}
    {(role === "doctor") && (<Link to="/doctorhome">Home</Link>)}
    {(role === "patient" || role === "admin") && (<Link to="/chat">Chat</Link>)}
    {(role === "doctor" || role === "admin") && (<Link to="/summary">Summary</Link>)}
</div>
 */}