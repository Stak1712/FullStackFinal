import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "../auth/tokenStorage";

type RetryableRequestConfig = InternalAxiosRequestConfig & { _retry?: boolean };

type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_expires_in: number;
};

const baseURL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";

export const plainHttp = axios.create({ baseURL });

export const http = axios.create({
  baseURL,
});

function notifyLogout() {
  clearTokens();
  window.dispatchEvent(new Event("auth:logout"));
}

export async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    notifyLogout();
    return null;
  }

  try {
    const res = await plainHttp.post<TokenPair>("/auth/refresh", { refresh_token: refreshToken });
    setTokens(res.data.access_token, res.data.refresh_token);
    return res.data.access_token;
  } catch {
    notifyLogout();
    return null;
  }
}

http.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

http.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const responseStatus = error.response?.status;
    const originalRequest = error.config as RetryableRequestConfig | undefined;
    const requestUrl = originalRequest?.url ?? "";

    const isAuthEndpoint = requestUrl.includes("/auth/login") || requestUrl.includes("/auth/register") || requestUrl.includes("/auth/refresh");

    if (responseStatus !== 401 || !originalRequest || originalRequest._retry || isAuthEndpoint) {
      if (responseStatus === 401 && isAuthEndpoint) {
        notifyLogout();
      }
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }

    const newAccessToken = await refreshPromise;
    if (!newAccessToken) {
      return Promise.reject(error);
    }

    originalRequest.headers = originalRequest.headers ?? {};
    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
    return http(originalRequest);
  }
);
