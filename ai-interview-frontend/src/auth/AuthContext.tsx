import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { http, plainHttp, refreshAccessToken } from "../api/http";
import { hasPermission as checkPermission, hasRole as checkRole } from "./access";
import type { User } from "./access";
import { isJwtExpired } from "./jwt";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./tokenStorage";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  isAuth: boolean;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (firstName: string, lastName: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
  hasRole: (...roles: string[]) => boolean;
};

type LoginResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_expires_in: number;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(getAccessToken());
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const clearAuthState = () => {
    clearTokens();
    setToken(null);
    setUser(null);
  };

  useEffect(() => {
    const handler = () => clearAuthState();
    window.addEventListener("auth:logout", handler);
    return () => window.removeEventListener("auth:logout", handler);
  }, []);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      setError(null);

      let accessToken = getAccessToken();
      const refreshToken = getRefreshToken();

      if (!accessToken && !refreshToken) {
        setLoading(false);
        return;
      }

      if (!accessToken || isJwtExpired(accessToken)) {
        accessToken = await refreshAccessToken();
      }

      if (!accessToken) {
        clearAuthState();
        setLoading(false);
        return;
      }

      setToken(accessToken);
      try {
        const res = await http.get<User>("/auth/me");
        setUser(res.data);
      } catch {
        clearAuthState();
      } finally {
        setLoading(false);
      }
    };

    void init();
  }, []);

  const login = async (email: string, password: string) => {
    setError(null);
    const res = await http.post<LoginResponse>("/auth/login", {
      email,
      password,
    });
    setTokens(res.data.access_token, res.data.refresh_token);
    setToken(res.data.access_token);
    const me = await http.get<User>("/auth/me");
    setUser(me.data);
  };

  const register = async (firstName: string, lastName: string, email: string, password: string) => {
    setError(null);
    await http.post<User>("/auth/register", {
      first_name: firstName,
      last_name: lastName,
      email,
      password,
    });
    await login(email, password);
  };

  const logout = async () => {
    const refreshToken = getRefreshToken();
    try {
      if (refreshToken) {
        await plainHttp.post("/auth/logout", { refresh_token: refreshToken });
      }
    } catch {
      // Игнорируем сетевую ошибку и всё равно чистим локальное состояние.
    } finally {
      clearAuthState();
    }
  };

  const hasPermission = (permission: string) => checkPermission(user, permission);
  const hasRole = (...roles: string[]) => checkRole(user, roles);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuth: Boolean(user && token),
      loading,
      error,
      login,
      register,
      logout,
      hasPermission,
      hasRole,
    }),
    [token, user, loading, error]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
