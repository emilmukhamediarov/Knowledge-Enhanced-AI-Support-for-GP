import { Navigate } from "react-router-dom";
import type {ReactNode} from "react";

type RoleRouteProps = {
    children: ReactNode;
    roles: ("doctor" | "patient" | "admin")[];
};

function RoleRoute({ children, roles }: RoleRouteProps) {
    const loggedIn = localStorage.getItem("loggedIn") === "true";
    const userRole = localStorage.getItem("role");

    if (!loggedIn) {
        return <Navigate to="/login" replace />;
    }

    if (!roles.includes(userRole as "doctor" | "patient" | "admin")) {
        return <Navigate to="/home" replace />;
    }

    return children;
}

export default RoleRoute;