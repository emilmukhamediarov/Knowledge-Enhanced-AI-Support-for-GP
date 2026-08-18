import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from './pages/Home';
import Chat from './pages/Chat'
import Navbar from "./components/Navbar";

/*
import bitwiseNamedImg from './assets/BitwiseNamed.png'
import bitwiseImg from './assets/BitwiseLogo.svg'
import './App.css'
*/

// controls overall app & routing

function App() {
    return (
        <BrowserRouter>
            <Navbar />
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/chat" element={<Chat />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App
