import { useNavigate } from "react-router-dom";
import "./Landing.css";
import ThemeToggle from "../components/ThemeToggle";

function Landing() {
    const navigate = useNavigate();

    return (
        <div className="landing-page">


            <main className="landing-hero">
                <section className="hero-content">
                    <p className="hero-eyebrow">
                        YOUR HEALTH, SIMPLIFIED
                    </p>

                    <h1>
                        Better knowledge.
                        <br />
                        Better support.
                        <br />
                        <span>Better healthcare.</span>
                    </h1>

                    <p className="hero-description">
                        Understand your health concerns, prepare for
                        consultations, and feel more confident in your
                        healthcare journey.
                    </p>

                    <div className="hero-actions">
                        <button
                            className="hero-button"
                            onClick={() => navigate("/register")}
                        >
                            Get Started
                        </button>

                        <button
                            className="hero-signin"
                            onClick={() => navigate("/login")}
                        >
                            Already have an account?{" "}
                            <span>Sign in</span>
                        </button>
                    </div>
                </section>

                <section className="hero-visual">
                    <div className="hero-circle hero-circle-large" />
                    <div className="hero-circle hero-circle-small" />

                    <div className="health-visual">
                        <div className="health-orbit health-orbit-one" />
                        <div className="health-orbit health-orbit-two" />

                        <div className="health-center">
                            <div className="health-icon"><span>+</span></div>
                            <p>Better care starts<br />with understanding.</p>
                        </div>

                        <div className="health-pill health-pill-top">
                            <span className="health-pill-dot" />
                            Personalised support
                        </div>

                        <div className="health-pill health-pill-bottom">
                            <span>✓</span>
                            Private &amp; secure
                        </div>
                    </div>
                </section>
            </main>

            <div className="landing-tagline">
                Supporting better conversations between patients
                and healthcare professionals.
            </div>
            <div className="landing-theme-toggle">
                <ThemeToggle />
            </div>
        </div>
    );
}

export default Landing;