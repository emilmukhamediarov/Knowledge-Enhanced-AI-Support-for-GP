import "@testing-library/jest-dom/vitest";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import RoleRoute from "../components/RoleRoute";

describe("RoleRoute", () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it("redirects unauthenticated users to login", () => {
        render(
            <MemoryRouter initialEntries={["/protected"]}>
                <Routes>
                    <Route
                        path="/protected"
                        element={
                            <RoleRoute roles={["doctor"]}>
                                <div>Protected Page</div>
                            </RoleRoute>
                        }
                    />
                    <Route path="/login" element={<div>Login Page</div>} />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText("Login Page")).toBeInTheDocument();
        expect(screen.queryByText("Protected Page")).not.toBeInTheDocument();
    });

    it("allows a logged-in user with the correct role", () => {
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("role", "doctor");

        render(
            <MemoryRouter initialEntries={["/protected"]}>
                <Routes>
                    <Route
                        path="/protected"
                        element={
                            <RoleRoute roles={["doctor"]}>
                                <div>Protected Page</div>
                            </RoleRoute>
                        }
                    />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText("Protected Page")).toBeInTheDocument();
    });

    it("redirects a logged-in user with the wrong role to home", () => {
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("role", "patient");

        render(
            <MemoryRouter initialEntries={["/protected"]}>
                <Routes>
                    <Route
                        path="/protected"
                        element={
                            <RoleRoute roles={["doctor"]}>
                                <div>Protected Page</div>
                            </RoleRoute>
                        }
                    />
                    <Route path="/home" element={<div>Home Page</div>} />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText("Home Page")).toBeInTheDocument();
        expect(screen.queryByText("Protected Page")).not.toBeInTheDocument();
    });

    it("allows any role included in the roles prop", () => {
        localStorage.setItem("loggedIn", "true");
        localStorage.setItem("role", "patient");

        render(
            <MemoryRouter initialEntries={["/protected"]}>
                <Routes>
                    <Route
                        path="/protected"
                        element={
                            <RoleRoute roles={["doctor", "patient"]}>
                                <div>Protected Page</div>
                            </RoleRoute>
                        }
                    />
                </Routes>
            </MemoryRouter>
        );

        expect(screen.getByText("Protected Page")).toBeInTheDocument();
    });
});