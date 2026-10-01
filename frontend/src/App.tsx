import { createBrowserRouter, RouterProvider, Route, createRoutesFromElements, Outlet } from "react-router-dom";

import Home from "./pages/Home";
import PatientHome from "./pages/patient/PatientHome";
import DoctorHome from "./pages/doctor/DoctorHome";
import Chat from "./pages/patient/Chat";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import RoleRoute from "./components/RoleRoute";
import Register from "./pages/Register";
import NewConsultation from "./pages/patient/NewConsultation";
import Sidebar from "./components/Sidebar";
import ProtectedRoute from "./components/ProtectedRoute";
import AllConsultations from "./pages/patient/AllConsultations";
import Landing from "./pages/Landing";
import Patients from "./pages/doctor/Patients";
import Consultations from "./pages/doctor/Consultations";
import DoctorConsultation from "./pages/doctor/DoctorConsultation";
import SessionExpiredModal from "./components/SessionExpiredModal";
import PatientDetails from "./pages/doctor/PatientDetails";
import Settings from "./pages/Settings";
import EditProfile from "./pages/patient/EditProfile";

function ProtectedLayout() {
    return (
        <div className="app-layout">
            <Sidebar />
            <Outlet />
        </div>
    );
}

// controls overall app & routing

const router = createBrowserRouter(
    createRoutesFromElements(
        <Route element={<><Navbar /><SessionExpiredModal /><Outlet /></>}>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />}/>
            <Route path="/register" element={<Register />}/>

            {/* Protected routes */}
            <Route element={<ProtectedRoute><ProtectedLayout /></ProtectedRoute>}>
                <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>}/>
                <Route path="/edit-profile" element={<ProtectedRoute><EditProfile /></ProtectedRoute>}/>

                {/* Admin */}
                <Route path="/home" element={<RoleRoute roles={["admin"]}><Home /></RoleRoute>}/>

                {/* Doctor pathway */}
                <Route path="/doctorhome" element={<RoleRoute roles={["doctor", "admin"]}><DoctorHome /></RoleRoute>}/>
                <Route path="/doctor/patients" element={<ProtectedRoute><RoleRoute roles={["doctor", "admin"]}><Patients /></RoleRoute></ProtectedRoute>}/>
                <Route path="/doctor/consultations" element={<ProtectedRoute><RoleRoute roles={["doctor", "admin"]}><Consultations /></RoleRoute></ProtectedRoute>}/>
                <Route path="/doctor/consultations/:consultationId" element={<ProtectedRoute><RoleRoute roles={["doctor", "admin"]}><DoctorConsultation /></RoleRoute></ProtectedRoute>}/>
                <Route path="/doctor/patients/:patientId" element={<ProtectedRoute><RoleRoute roles={["doctor", "admin"]}><PatientDetails /></RoleRoute></ProtectedRoute>}/>

                {/* Patient pathway */}
                <Route path="/patienthome" element={<RoleRoute roles={["patient", "admin"]}><PatientHome /></RoleRoute>}/>
                <Route path="/new-consultation" element={<RoleRoute roles={["patient", "admin"]}><NewConsultation /></RoleRoute>}/>
                <Route path="/chat/:consultationId" element={<Chat />}/>
                <Route path="/all-chats" element={<RoleRoute roles={["patient", "admin"]}><AllConsultations /></RoleRoute>}/>

            </Route>
        </Route>
    )
);

function App() {
    return <RouterProvider router={router} />;
}

export default App;