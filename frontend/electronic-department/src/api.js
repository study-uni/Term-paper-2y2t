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
      import("pinia")
        .then(({ getActivePinia }) => {
          const pinia = getActivePinia();
          if (!pinia) {
            localStorage.removeItem("ed-auth");
            return;
          }
          return Promise.all([
            import("./stores/auth"),
            import("./stores/department"),
          ]).then(([authModule, departmentModule]) => {
            authModule.useAuthStore(pinia).logout();
            departmentModule.useDepartmentStore(pinia).clearPrivate();
          });
        })
        .catch(() => {
          localStorage.removeItem("ed-auth");
        });
      if (window.location.pathname !== "/") {
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  },
);

export default api;
