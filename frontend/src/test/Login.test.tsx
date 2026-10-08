import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Login from "../pages/Login";
import { apiFetch } from "../api/client";

vi.mock("../api/client", () => ({
    apiFetch: vi.fn(),
}));

const mockedApiFetch = vi.mocked(apiFetch);

describe("Login", () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it("renders the login form", () => {
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        expect(
            screen.getByRole("heading", { name: "Login" })
        ).toBeInTheDocument();

        expect(
            screen.getByPlaceholderText("Username")
        ).toBeInTheDocument();

        expect(
            screen.getByPlaceholderText("Password")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("button", { name: "Login" })
        ).toBeInTheDocument();
    });

    it("shows an error when username or password is empty", async () => {
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Login" })
        );

        expect(
            screen.getAllByText(
                "Please enter your username and password."
            ).length
        ).toBeGreaterThan(0);

        expect(mockedApiFetch).not.toHaveBeenCalled();
    });

    it("logs in a doctor and stores their login information", async () => {
        mockedApiFetch.mockResolvedValueOnce({
            access_token: "doctor-token",
            user_id: 123,
            role: "doctor",
            name: "Dr Test",
        });

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        fireEvent.change(
            screen.getByPlaceholderText("Username"),
            {
                target: { value: "doctor1" },
            }
        );

        fireEvent.change(
            screen.getByPlaceholderText("Password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Login" })
        );

        await waitFor(() => {
            expect(mockedApiFetch).toHaveBeenCalledWith(
                "/auth/login",
                expect.objectContaining({
                    method: "POST",
                })
            );
        });

        expect(localStorage.getItem("loggedIn")).toBe("true");
        expect(localStorage.getItem("access_token")).toBe(
            "doctor-token"
        );
        expect(localStorage.getItem("userId")).toBe("123");
        expect(localStorage.getItem("role")).toBe("doctor");
        expect(localStorage.getItem("userName")).toBe("Dr Test");
    });

    it("logs in a patient and stores their login information", async () => {
        mockedApiFetch.mockResolvedValueOnce({
            access_token: "patient-token",
            user_id: 456,
            role: "patient",
            name: "Test Patient",
        });

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        fireEvent.change(
            screen.getByPlaceholderText("Username"),
            {
                target: { value: "patient1" },
            }
        );

        fireEvent.change(
            screen.getByPlaceholderText("Password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Login" })
        );

        await waitFor(() => {
            expect(mockedApiFetch).toHaveBeenCalled();
        });

        expect(localStorage.getItem("loggedIn")).toBe("true");
        expect(localStorage.getItem("access_token")).toBe(
            "patient-token"
        );
        expect(localStorage.getItem("userId")).toBe("456");
        expect(localStorage.getItem("role")).toBe("patient");
        expect(localStorage.getItem("userName")).toBe("Test Patient");
    });

    it("shows the API error when login fails", async () => {
        mockedApiFetch.mockRejectedValueOnce(
            new Error("Invalid username or password.")
        );

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        fireEvent.change(
            screen.getByPlaceholderText("Username"),
            {
                target: { value: "wronguser" },
            }
        );

        fireEvent.change(
            screen.getByPlaceholderText("Password"),
            {
                target: { value: "wrongpassword" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Login" })
        );

        await waitFor(() => {
            expect(
                screen.getAllByText(
                    "Invalid username or password."
                ).length
            ).toBeGreaterThan(0);
        });

        expect(localStorage.getItem("loggedIn")).toBeNull();
    });

    it("opens the email verification popup when the account is unverified", async () => {
        mockedApiFetch.mockRejectedValueOnce(
            new Error("Please verify your email before logging in.")
        );

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        fireEvent.change(
            screen.getByPlaceholderText("Username"),
            {
                target: { value: "unverified" },
            }
        );

        fireEvent.change(
            screen.getByPlaceholderText("Password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Login" })
        );

        await waitFor(() => {
            expect(
                screen.getByRole("heading", {
                    name: "Verify your email",
                })
            ).toBeInTheDocument();
        });

        expect(
            screen.getByPlaceholderText("Email")
        ).toBeInTheDocument();
    });
});