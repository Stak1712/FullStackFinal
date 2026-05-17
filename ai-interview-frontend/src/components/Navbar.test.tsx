import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Navbar from "./Navbar";
import { useAuth } from "../auth/AuthContext";

vi.mock("../auth/AuthContext", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

function renderNavbar(auth: any) {
  mockedUseAuth.mockReturnValue(auth);
  return render(
    <MemoryRouter>
      <Navbar />
    </MemoryRouter>
  );
}

describe("Navbar", () => {
  beforeEach(() => mockedUseAuth.mockReset());

  it("shows login/register links for guest", () => {
    renderNavbar({ isAuth: false, user: null, hasRole: () => false, logout: vi.fn() });

    expect(screen.getByRole("link", { name: "Войти" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Регистрация" })).toBeInTheDocument();
    expect(screen.queryByText("Админ-панель")).not.toBeInTheDocument();
  });

  it("shows private navigation for authenticated user", () => {
    renderNavbar({
      isAuth: true,
      user: { first_name: "Турпал", last_name: "Шабазов", role: "user" },
      hasRole: () => false,
      logout: vi.fn(),
    });

    expect(screen.getByRole("link", { name: "Начать интервью" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Турпал Шабазов" })).toBeInTheDocument();
    expect(screen.queryByText("Админ-панель")).not.toBeInTheDocument();
  });

  it("shows admin panel link only for admin", () => {
    renderNavbar({
      isAuth: true,
      user: { email: "admin@example.com", role: "admin" },
      hasRole: (role: string) => role === "admin",
      logout: vi.fn(),
    });

    expect(screen.getByRole("link", { name: "Админ-панель" })).toBeInTheDocument();
  });
});
