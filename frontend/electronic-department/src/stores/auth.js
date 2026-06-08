import { defineStore } from "pinia";
import api from "../api";

const STORAGE_KEY = "ed-auth";

function loadStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw);
    if (!data?.role || data.role === "guest") return null;
    return data;
  } catch {
    return null;
  }
}

function buildInitialState() {
  const stored = loadStoredAuth();
  if (!stored) {
    return {
      user: null,
      role: "guest",
      token: null,
      profileId: null,
      profileType: null,
    };
  }
  return {
    user: stored.user ?? null,
    role: stored.role,
    token: stored.token ?? null,
    profileId: stored.profileId ?? null,
    profileType: stored.profileType ?? null,
  };
}

export const useAuthStore = defineStore("auth", {
  state: () => buildInitialState(),

  getters: {
    isGuest: (state) => state.role === "guest",
    canManage: (state) => ["admin", "manager"].includes(state.role),
    isTeacher: (state) => state.role === "teacher",
    isStudent: (state) => state.role === "student",
    roleLabel: (state) => {
      const labels = {
        guest: "Незареєстрований",
        admin: "Адміністратор",
        manager: "Менеджер",
        teacher: "Викладач",
        student: "Студент",
      };
      return labels[state.role] ?? state.role;
    },
  },

  actions: {
    async login(userRole, profileId = null) {
      if (userRole === "guest") {
        this.role = "guest";
        this.user = null;
        this.token = null;
        this.profileId = null;
        this.profileType = null;
        this.persist();
        return;
      }

      try {
        const response = await api.post("/auth/mock-login", {
          role: userRole,
          profile_id: profileId,
        });

        const data = response.data;
        this.role = data.role;
        this.token = data.access_token;
        this.profileId = data.profile_id;
        this.profileType = data.profile_type;
        this.user = { name: data.name };
        this.persist();
      } catch (error) {
        console.error("Login failed:", error);
        throw error;
      }
    },
    logout() {
      this.role = "guest";
      this.user = null;
      this.token = null;
      this.profileId = null;
      this.profileType = null;
      this.persist();
    },
    persist() {
      if (this.role === "guest") {
        localStorage.removeItem(STORAGE_KEY);
        return;
      }
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          role: this.role,
          user: this.user,
          token: this.token,
          profileId: this.profileId,
          profileType: this.profileType,
        }),
      );
    },
  },
});
