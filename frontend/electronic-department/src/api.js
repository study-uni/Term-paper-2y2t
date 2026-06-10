import axios from "axios";

const primaryBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001/api";
const fallbackBaseUrl = import.meta.env.VITE_API_FALLBACK_URL || "http://localhost:8000/api";

const api = axios.create({
  baseURL: primaryBaseUrl,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to automatically attach JWT token
api.interceptors.request.use(
  (config) => {
    const rawAuth = localStorage.getItem("ed-auth");
    if (rawAuth) {
      try {
        const authData = JSON.parse(rawAuth);
        if (authData && authData.token) {
          config.headers.Authorization = `Bearer ${authData.token}`;
        }
      } catch (e) {
        console.error("Error parsing auth token", e);
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Response interceptor to handle auth errors and fallback network issues
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    if (config && !config.__retry && !error.response) {
      config.__retry = true;
      config.baseURL = fallbackBaseUrl;
      console.warn(
        `Primary API base URL failed, retrying with fallback ${fallbackBaseUrl}`,
      );
      return api.request(config);
    }

    if (error.response && error.response.status === 401) {
      console.warn("Unauthorized access - clearing session");
      localStorage.removeItem("ed-auth");
      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
    }

    return Promise.reject(error);
  },
);

export default api;
