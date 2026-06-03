import { defineStore } from 'pinia';

const STORAGE_KEY = 'ed-auth';

const ROLE_PROFILES = {
  admin: { name: 'Адміністратор Системи', profileId: null },
  manager: { name: 'Менеджер Кафедри', profileId: null },
  teacher: { name: 'Прокопенко Андрій Васильович', profileId: 1, profileType: 'teacher' },
  student: { name: 'Рудий Іван Володимирович', profileId: 1, profileType: 'student' },
  guest: { name: null, profileId: null },
};

function loadStoredAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw);
    if (!data?.role || data.role === 'guest') return null;
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
      role: 'guest',
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

export const useAuthStore = defineStore('auth', {
  state: () => buildInitialState(),

  getters: {
    isGuest: (state) => state.role === 'guest',
    canManage: (state) => ['admin', 'manager'].includes(state.role),
    isTeacher: (state) => state.role === 'teacher',
    isStudent: (state) => state.role === 'student',
    roleLabel: (state) => {
      const labels = {
        guest: 'Незареєстрований',
        admin: 'Адміністратор',
        manager: 'Менеджер',
        teacher: 'Викладач',
        student: 'Студент',
      };
      return labels[state.role] ?? state.role;
    },
  },

  actions: {
    login(userRole) {
      const profile = ROLE_PROFILES[userRole] ?? ROLE_PROFILES.guest;
      this.role = userRole;
      this.profileId = profile.profileId ?? null;
      this.profileType = profile.profileType ?? null;
      this.user = profile.name ? { name: profile.name } : null;
      this.token = userRole === 'guest' ? null : 'mock-jwt-token';
      this.persist();
    },
    logout() {
      this.role = 'guest';
      this.user = null;
      this.token = null;
      this.profileId = null;
      this.profileType = null;
      this.persist();
    },
    persist() {
      if (this.role === 'guest') {
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
        })
      );
    },
  },
});
