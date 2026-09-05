//const API_URL = "http://localhost:8000";
const API_URL = import.meta.env.VITE_API_URL

export async function apiFetch(
    endpoint: string,
    options: RequestInit = {}
) {
    const token = localStorage.getItem("access_token");

    const response = await fetch(
        `${API_URL}${endpoint}`,
        {
            ...options,
            headers: {
                "Content-Type": "application/json",

                ...(token
                    ? {
                        Authorization: `Bearer ${token}`,
                    }
                    : {}),

                ...(options.headers || {}),
            },
        }
    );

    if (response.status === 401) {
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