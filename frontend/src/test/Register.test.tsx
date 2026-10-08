import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Register from "../pages/Register";
import { apiFetch } from "../api/client";

vi.mock("../api/client", () => ({
    apiFetch: vi.fn(),
}));

const mockedApiFetch = vi.mocked(apiFetch);

describe("Register", () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.useRealTimers();
    });

    it("renders the registration form", () => {
        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        expect(
            screen.getByRole("heading", { name: "Register" })
        ).toBeInTheDocument();

        expect(screen.getByPlaceholderText("Name")).toBeInTheDocument();
        expect(screen.getByPlaceholderText("Email")).toBeInTheDocument();
        expect(
            screen.getByPlaceholderText("Username")
        ).toBeInTheDocument();
        expect(
            screen.getByPlaceholderText("Password")
        ).toBeInTheDocument();
        expect(
            screen.getByPlaceholderText("Confirm password")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("button", { name: "Register" })
        ).toBeInTheDocument();
    });

    it("shows an error when the name is empty", () => {
        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        expect(
            screen.getByText("Please enter your name.")
        ).toBeInTheDocument();

        expect(mockedApiFetch).not.toHaveBeenCalled();
    });

    it("shows an error when the email is empty", () => {
        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        expect(
            screen.getByText("Please enter your email address.")
        ).toBeInTheDocument();

        expect(mockedApiFetch).not.toHaveBeenCalled();
    });

    it("shows an error when the username is empty", () => {
        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        expect(
            screen.getByText("Please enter a username.")
        ).toBeInTheDocument();

        expect(mockedApiFetch).not.toHaveBeenCalled();
    });

    it("shows an error when the password is empty", () => {
        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        expect(
            screen.getByText("Please enter a password.")
        ).toBeInTheDocument();

        expect(mockedApiFetch).not.toHaveBeenCalled();
    });

    it("shows an error when the passwords do not match", () => {
        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password123" },
        });

        fireEvent.change(
            screen.getByPlaceholderText("Confirm password"),
            {
                target: { value: "differentpassword" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        expect(
            screen.getByText("Passwords do not match.")
        ).toBeInTheDocument();

        expect(mockedApiFetch).not.toHaveBeenCalled();
    });

    it("sends a verification code after valid registration details", async () => {
        mockedApiFetch.mockResolvedValueOnce({});

        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password123" },
        });

        fireEvent.change(
            screen.getByPlaceholderText("Confirm password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        await waitFor(() => {
            expect(mockedApiFetch).toHaveBeenCalledWith(
                "/auth/send-code",
                {
                    method: "POST",
                    body: JSON.stringify({
                        email: "test@example.com",
                        username: "testuser",
                    }),
                }
            );
        });

        expect(
            screen.getByRole("heading", {
                name: "Verify your email",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByPlaceholderText("000000")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("button", {
                name: "Verify Email",
            })
        ).toBeInTheDocument();
    });

    it("shows an API error when sending the verification code fails", async () => {
        mockedApiFetch.mockRejectedValueOnce(
            new Error("Email is already registered.")
        );

        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password123" },
        });

        fireEvent.change(
            screen.getByPlaceholderText("Confirm password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        await waitFor(() => {
            expect(
                screen.getByText("Email is already registered.")
            ).toBeInTheDocument();
        });

        expect(
            screen.queryByRole("heading", {
                name: "Verify your email",
            })
        ).not.toBeInTheDocument();
    });

    it("requires a 6-digit verification code", async () => {
        mockedApiFetch.mockResolvedValueOnce({});

        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password123" },
        });

        fireEvent.change(
            screen.getByPlaceholderText("Confirm password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        await waitFor(() => {
            expect(
                screen.getByPlaceholderText("000000")
            ).toBeInTheDocument();
        });

        const codeInput = screen.getByPlaceholderText("000000");

        fireEvent.change(codeInput, {
            target: { value: "123" },
        });

        expect(
            screen.getByRole("button", {
                name: "Verify Email",
            })
        ).toBeDisabled();

        expect(mockedApiFetch).toHaveBeenCalledTimes(1);
    });

    it("completes registration with a valid verification code", async () => {
        mockedApiFetch
            .mockResolvedValueOnce({})
            .mockResolvedValueOnce({});

        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password123" },
        });

        fireEvent.change(
            screen.getByPlaceholderText("Confirm password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        await waitFor(() => {
            expect(
                screen.getByPlaceholderText("000000")
            ).toBeInTheDocument();
        });

        fireEvent.change(
            screen.getByPlaceholderText("000000"),
            {
                target: { value: "123456" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", {
                name: "Verify Email",
            })
        );

        await waitFor(() => {
            expect(mockedApiFetch).toHaveBeenCalledWith(
                "/auth/register",
                {
                    method: "POST",
                    body: JSON.stringify({
                        name: "Test User",
                        email: "test@example.com",
                        username: "testuser",
                        password: "password123",
                        validation_code: "123456",
                    }),
                }
            );
        });

        expect(
            screen.getByText(
                "Account created successfully! You can now log in."
            )
        ).toBeInTheDocument();
    });

    it("filters non-numeric characters from the verification code", async () => {
        mockedApiFetch.mockResolvedValueOnce({});

        render(
            <MemoryRouter>
                <Register />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText("Name"), {
            target: { value: "Test User" },
        });

        fireEvent.change(screen.getByPlaceholderText("Email"), {
            target: { value: "test@example.com" },
        });

        fireEvent.change(screen.getByPlaceholderText("Username"), {
            target: { value: "testuser" },
        });

        fireEvent.change(screen.getByPlaceholderText("Password"), {
            target: { value: "password123" },
        });

        fireEvent.change(
            screen.getByPlaceholderText("Confirm password"),
            {
                target: { value: "password123" },
            }
        );

        fireEvent.click(
            screen.getByRole("button", { name: "Register" })
        );

        await waitFor(() => {
            expect(
                screen.getByPlaceholderText("000000")
            ).toBeInTheDocument();
        });

        const codeInput = screen.getByPlaceholderText("000000");

        fireEvent.change(codeInput, {
            target: { value: "12a3b4567" },
        });

        expect(codeInput).toHaveValue("123456");
    });
});