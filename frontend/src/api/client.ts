const API_URL = import.meta.env.VITE_API_URL;

export async function apiFetch(
    endpoint: string,
    options: RequestInit = {}
) {
    const token = localStorage.getItem("access_token");

    const headers = new Headers(options.headers);

    if (!headers.has("Content-Type") && options.body) {
        headers.set("Content-Type", "application/json");
    }

    if (token && endpoint !== "/auth/login") {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        if (endpoint === "/auth/login") {
            let message = "Invalid username or password.";

            try {
                const errorData = await response.json();

                if (errorData.detail) {
                    message = errorData.detail;
                }
            } catch {
                // Ignore JSON parsing errors
            }

            throw new Error(message);
        }

        localStorage.removeItem("access_token");
        localStorage.removeItem("loggedIn");
        localStorage.removeItem("role");
        localStorage.removeItem("userId");

        window.dispatchEvent(
            new Event("session-expired")
        );

        throw new Error("Session expired");
    }

    if (!response.ok) {
        let message = `Request failed: ${response.status}`;

        try {
            const errorData = await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }
        } catch {
            // Ignore JSON parsing errors
        }

        throw new Error(message);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}