import "./ThemeToggle.css";
import { useTheme } from "../hooks/useTheme";

function ThemeToggle() {
    const { theme, setTheme } = useTheme();

    const isDark = theme === "dark";

    const toggleTheme = () => {
        setTheme(isDark ? "light" : "dark");
    };

    return (
        <div className="theme-container">
            <button
                className={`theme-toggle ${isDark ? "dark" : ""}`}
                onClick={toggleTheme}
                aria-label={
                    isDark
                        ? "Switch to light mode"
                        : "Switch to dark mode"
                }
            >
                <span className="theme-toggle-icon sun">
                    ☀
                </span>

                <span className="theme-toggle-icon moon">
                    ☾
                </span>

                <span className="theme-toggle-thumb" />
            </button>

            <span className="theme-label">
                {isDark ? "Dark mode" : "Light mode"}
            </span>
        </div>
    );
}

export default ThemeToggle;