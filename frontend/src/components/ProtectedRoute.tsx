//this checks localStorage to see if the user is logged in
//obsolete; keeping it for basic testing for now
import { Navigate } from "react-router-dom";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const token = localStorage.getItem("access_token");

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

export default ProtectedRoute;