import { Link } from "react-router-dom";
import "./Navbar.css";

function Navbar() {
    return (
        <nav>
            <div>
                <Link to="/">Home</Link>
                <Link to="/chat">Chat</Link>
                <Link to="/summary">Summary</Link>
            </div>
            <button>
                Logout
            </button>
        </nav>
    );
}

export default Navbar;