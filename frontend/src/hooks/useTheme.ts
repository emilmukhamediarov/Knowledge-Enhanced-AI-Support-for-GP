import { useEffect, useState } from "react";

export type Theme = "system" | "light" | "dark";

const STORAGE_KEY = "theme";

function getSystemTheme(): "light" | "dark" {
    return window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";
}

function applyTheme(theme: Theme) {
    const root = document.documentElement;

    root.classList.remove("theme-light", "theme-dark");

    if (theme === "light") {
        root.classList.add("theme-light");
    } else if (theme === "dark") {
        root.classList.add("theme-dark");
    }
}

export function useTheme() {
    const [theme, setThemeState] = useState<Theme>(() => {
        const saved = localStorage.getItem(STORAGE_KEY);

        if (
            saved === "light" ||
            saved === "dark" ||
            saved === "system"
        ) {
            return saved;
        }

        return "system";
    });

    useEffect(() => {
        applyTheme(theme);

        if (theme === "system") {
            localStorage.removeItem(STORAGE_KEY);
        } else {
            localStorage.setItem(STORAGE_KEY, theme);
        }
    }, [theme]);

    useEffect(() => {
        if (theme !== "system") {
            return;
        }

        const mediaQuery = window.matchMedia(
            "(prefers-color-scheme: dark)"
        );

        const handleChange = () => {
            applyTheme("system");
        };

        mediaQuery.addEventListener("change", handleChange);

        return () => {
            mediaQuery.removeEventListener("change", handleChange);
        };
    }, [theme]);

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme);
    };

    return {
        theme,
        setTheme,
        systemTheme: getSystemTheme(),
    };
}