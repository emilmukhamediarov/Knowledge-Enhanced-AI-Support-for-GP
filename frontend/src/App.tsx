import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Home from './pages/Home';
import PatientHome from './pages/patient/PatientHome';
import DoctorHome from './pages/doctor/DoctorHome';
import Chat from './pages/patient/Chat'
import Summary from './pages/doctor/Summary'
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import RoleRoute from "./components/RoleRoute";
import Rag from "./pages/doctor/Rag";
import Register from "./pages/Register";

// controls overall app & routing

function App() {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path="/" element={<Navigate to="/login" replace />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />

                <Route path="/home" element={<RoleRoute roles={["admin"]}><Home /></RoleRoute>} />

                {/*Doctor pathway*/}
                <Route path="/doctorhome"element={<RoleRoute roles={["doctor", "admin"]}><DoctorHome /></RoleRoute>} />
                <Route path="/summary"element={<RoleRoute roles={["doctor", "admin"]}><Summary /></RoleRoute>} />
                <Route path="/rag"element={<RoleRoute roles={["doctor", "admin"]}><Rag /></RoleRoute>} />

                {/*Patient pathway*/}
                <Route path="/patienthome" element={<RoleRoute roles={["patient", "admin"]}><PatientHome /></RoleRoute>} />
                <Route path="/chat" element={<RoleRoute roles={["patient", "admin"]}><Chat /></RoleRoute>} />


                {/*
                <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
                <Route path="/chat" element={<ProtectedRoute><Chat /></ProtectedRoute>} />
                <Route path="/summary" element={<ProtectedRoute><Summary /></ProtectedRoute>} />
                */}

            </Routes>
        </BrowserRouter>
    );
}

export default App
