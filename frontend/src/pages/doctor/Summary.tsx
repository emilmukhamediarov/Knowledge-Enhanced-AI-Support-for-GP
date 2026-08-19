/*
Temporary page to assign functionality from backend to frontend; will most likely be integrated into a broader tsx


*/
import { useEffect, useState } from "react";
import { apiFetch } from "../../api/client";

type summaryData = {
    main_concern: string;
    symptoms: string[];
    duration: string;
    severity: string;
    medical_history: string[];
    medications: string[];
    allergies: string[];
    additional_concerns: string[];
};

function Summary() {
    const [summary, setSummary] = useState<summaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const getSummary = async() => {
            try {
                const data = await apiFetch("/summary");
                const parsedSummary: summaryData = JSON.parse(data.summary);
                setSummary(parsedSummary);
            } catch {
                console.error("Summary error:", error);
                setError("Failed to load summary.");
            } finally {
                setLoading(false);
            }
        };
        getSummary();
    }, []);

    if (loading) {
        return <p>Loading summary...</p>;
    }

    if (error) {
        return <p>{error}</p>;
    }

    if (!summary) {
        return <p>No summary available.</p>;
    }

    return (
        <main>
            <h1> Patient Summary </h1>

            <section>
                <h2>Main Concern</h2>
                <p>{summary.main_concern || "None provided"}</p>
            </section>

            <section>
                <h2>Symptoms</h2>
                {summary.symptoms.length > 0 ? (
                <ul>
                    {summary.symptoms.map((symptom, index) => (<li key={index}>{symptom}</li>))}
                </ul>
                ) : (<p>None provided.</p>)}
            </section>

            <section>
                <h2>Duration</h2>
                <p>{summary.duration || "None provided"}</p>
            </section>

            <section>
                <h2>Severity</h2>
                <p>{summary.severity || "None provided"}</p>
            </section>

            <section>
                <h2>Medical History</h2>
                {summary.medical_history.length > 0 ? (
                <ul>
                    {summary.medical_history.map((item, index) => (<li key={index}>{item}</li>))}
                </ul>
                ) : (<p>None provided.</p>)}
            </section>

            <section>
                <h2>Medications</h2>
                {summary.medications.length > 0 ? (
                <ul>
                    {summary.medications.map((medication, index) => (<li key={index}>{medication}</li>))}
                </ul>
                ) : (<p>None provided.</p>)}
            </section>

            <section>
                <h2>Allergies</h2>
                {summary.allergies.length > 0 ? (
                <ul>
                    {summary.allergies.map((allergy, index) => (<li key={index}>{allergy}</li>))}
                </ul>
                ) : (<p>None provided.</p>)}
            </section>

            <section>
                <h2>Additional Concerns</h2>
                {summary.additional_concerns.length > 0 ? (
                <ul>
                    {summary.additional_concerns.map((concern, index) => (<li key={index}>{concern}</li>))}
                </ul>
                ) : (<p>None provided.</p>)}
            </section>

        </main>
    );
}

export default Summary;