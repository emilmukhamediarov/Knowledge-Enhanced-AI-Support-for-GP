// Temp admin home for testing

import { useEffect, useState } from "react";
import { apiFetch } from "../api/client";
import "./Home.css";

function Home() {
    const [message, setMessage] = useState("");

    const consultationId = 1;

    useEffect(() => {
        apiFetch("/")
            .then((data) => setMessage(data.message))
            .catch((error) => console.error("Backend error:", error));
    }, []);

    const clearResultsCache = () => {
        localStorage.removeItem(`rag_${consultationId}`);
        localStorage.removeItem(`summary_${consultationId}`);
    };

    return (
        <main>
            <h1>Admin Home</h1>

            <p>{message}</p>

            <button
                type="button"
                onClick={clearResultsCache}
                className="clear-results-button"
            >
                Clear RAG & Summary
            </button>
        </main>
    );
}

export default Home;