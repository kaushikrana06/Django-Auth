import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig, AxiosRequestHeaders } from "axios";

// runtime/base url support
const runtimeBase = (window as any).__ENV?.API_BASE_URL;
const baseURL = runtimeBase || import.meta.env.VITE_API_BASE_URL || "/api";

const api = axios.create({
  baseURL,
  withCredentials: true,
});

// in-memory access token
let accessToken: string | null = null;
export const setAccessToken = (t: string | null) => { accessToken = t; };
export const getAccessToken = () => accessToken;

// attach Authorization
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) {
    const headers = (config.headers ?? {}) as AxiosRequestHeaders;
    headers.Authorization = `Bearer ${accessToken}`;
    config.headers = headers;
  }
  return config;
});

// refresh queue…
let isRefreshing = false;
let queue: Array<(t: string | null) => void> = [];

async function doRefresh(): Promise<string> {
  const { data } = await axios.post(
    baseURL.replace(/\/$/, "") + "/refresh/",
    {},
    { withCredentials: true }
  );
  return data.access as string;
}

api.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const token = await doRefresh();
          setAccessToken(token);
          queue.forEach(fn => fn(token));
          queue = [];
          isRefreshing = false;

          const h = (original.headers ?? {}) as AxiosRequestHeaders;
          h.Authorization = `Bearer ${token}`;
          original.headers = h;
          return api(original);
        } catch (e) {
          queue.forEach(fn => fn(null));
          queue = [];
          isRefreshing = false;
          setAccessToken(null);
          return Promise.reject(e);
        }
      }

      return new Promise((resolve, reject) => {
        queue.push((t) => {
          if (!t) return reject(error);
          const h = (original.headers ?? {}) as AxiosRequestHeaders;
          h.Authorization = `Bearer ${t}`;
          original.headers = h;
          resolve(api(original));
        });
      });
    }
    return Promise.reject(error);
  }
);

export default api;
