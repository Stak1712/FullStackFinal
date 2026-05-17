import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import ProtectedRoute from "./ProtectedRoute";
import { useAuth } from "./AuthContext";

vi.mock("./AuthContext", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

function renderPrivateRoute() {
  return render(
    <MemoryRouter initialEntries={["/private"]}>
      <Routes>
        <Route
          path="/private"
          element={
            <ProtectedRoute roles={["admin"]} permissions={["admin:panel"]}>
              <div>Secret admin content</div>
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<div>Login page</div>} />
        <Route path="/forbidden" element={<div>Forbidden page</div>} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ProtectedRoute", () => {
  beforeEach(() => {
    mockedUseAuth.mockReset();
  });

  it("redirects anonymous user to login", () => {
    mockedUseAuth.mockReturnValue({
      isAuth: false,
      loading: false,
      hasRole: () => false,
      hasPermission: () => false,
    } as any);

    renderPrivateRoute();

    expect(screen.getByText("Login page")).toBeInTheDocument();
  });

  it("redirects authenticated user without role to forbidden page", () => {
    mockedUseAuth.mockReturnValue({
      isAuth: true,
      loading: false,
      hasRole: () => false,
      hasPermission: () => true,
    } as any);

    renderPrivateRoute();

    expect(screen.getByText("Forbidden page")).toBeInTheDocument();
  });

  it("renders content when role and permission match", () => {
    mockedUseAuth.mockReturnValue({
      isAuth: true,
      loading: false,
      hasRole: () => true,
      hasPermission: () => true,
    } as any);

    renderPrivateRoute();

    expect(screen.getByText("Secret admin content")).toBeInTheDocument();
  });
});
