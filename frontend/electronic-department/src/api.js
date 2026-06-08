import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8001/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to automatically attach JWT token
api.interceptors.request.use(
  (config) => {
    // We import auth store dynamically to avoid circular dependency
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
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn("Unauthorized access - clearing session");
      localStorage.removeItem("ed-auth");
      // Force redirect to general page
      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  },
);

export default api;
