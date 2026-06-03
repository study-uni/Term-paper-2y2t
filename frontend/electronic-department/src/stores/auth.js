import { defineStore } from "pinia";
import { useDepartmentStore } from "./department";

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
    login(userRole) {
      this.role = userRole;
      this.token = userRole === "guest" ? null : "mock-jwt-token";

      if (userRole === "admin") {
        this.profileId = null;
        this.profileType = null;
        this.user = { name: "Адміністратор Системи" };
      } else if (userRole === "manager") {
        this.profileId = null;
        this.profileType = null;
        this.user = { name: "Менеджер Кафедри" };
      } else if (userRole === "teacher") {
        const dept = useDepartmentStore();
        const firstTeacher = dept.teachers[0];
        if (firstTeacher) {
          this.profileId = firstTeacher.id;
          this.profileType = "teacher";
          this.user = { name: firstTeacher.name };
        } else {
          this.profileId = null;
          this.profileType = "teacher";
          this.user = { name: "Викладач (Немає профілів)" };
        }
      } else if (userRole === "student") {
        const dept = useDepartmentStore();
        const firstStudent = dept.students[0];
        if (firstStudent) {
          this.profileId = firstStudent.id;
          this.profileType = "student";
          this.user = { name: firstStudent.name };
        } else {
          this.profileId = null;
          this.profileType = "student";
          this.user = { name: "Студент (Немає профілів)" };
        }
      } else {
        this.role = "guest";
        this.profileId = null;
        this.profileType = null;
        this.user = null;
      }
      this.persist();
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
