<script setup>
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "./stores/auth";
import { useDepartmentStore } from "./stores/department";
import Select from "primevue/select";
import Button from "primevue/button";
import Menu from "primevue/menu";

const authStore = useAuthStore();
const departmentStore = useDepartmentStore();
const router = useRouter();
const route = useRoute();

const roleOptions = [
  { label: "Незареєстрований", value: "guest" },
  { label: "Адміністратор", value: "admin" },
  { label: "Менеджер", value: "manager" },
  { label: "Викладач", value: "teacher" },
  { label: "Студент", value: "student" },
];

onMounted(async () => {
  await departmentStore.initPublic();

  if (authStore.role !== "guest") {
    await departmentStore.initPrivate(authStore.role, authStore.profileId);
  }
});

const changeRole = async (roleName) => {
  if (!roleName) return;
  try {
    await authStore.login(roleName);
    await departmentStore.initPrivate(authStore.role, authStore.profileId);
    const defaultRoutes = {
      teacher: "/journal",
      student: "/my-grades",
      admin: "/management",
      manager: "/management",
      guest: "/",
    };
    router.push(defaultRoutes[roleName] ?? "/");
  } catch (e) {
    console.error("Failed to login simulated role:", e);
  }
};

const handleLogout = () => {
  authStore.logout();
  departmentStore.clearPrivate();
  router.push("/");
};

const menuItems = computed(() => {
  const items = [
    {
      label: "Загальна інформація",
      icon: "pi pi-home",
      class: route.path === "/" ? "menu-item-active" : "",
      command: () => router.push("/"),
    },
  ];

  if (["admin", "manager", "teacher", "student"].includes(authStore.role)) {
    items.push({
      label: "Вивід даних (Підсистема 2)",
      icon: "pi pi-list",
      class: route.path === "/browse" ? "menu-item-active" : "",
      command: () => router.push("/browse"),
    });
  }

  if (authStore.canManage) {
    items.push({
      label: "Управління (Підсистема 1)",
      icon: "pi pi-sliders-h",
      class: route.path === "/management" ? "menu-item-active" : "",
      command: () => router.push("/management"),
    });
  }

  if (authStore.isTeacher) {
    items.push({
      label: "Журнал оцінок (Підсистема 3)",
      icon: "pi pi-book",
      class: route.path === "/journal" ? "menu-item-active" : "",
      command: () => router.push("/journal"),
    });
  }

  if (authStore.isStudent) {
    items.push({
      label: "Мої оцінки (Підсистема 3)",
      icon: "pi pi-user",
      class: route.path === "/my-grades" ? "menu-item-active" : "",
      command: () => router.push("/my-grades"),
    });
  }

  return items;
});
</script>

<template>
  <div id="app-layout">
    <header class="app-header">
      <div class="logo">
        <i class="pi pi-graduation-cap" style="font-size: 2rem"></i>
        <span>Електронна Кафедра</span>
      </div>

      <div class="role-simulator">
        <span class="status-text">Тестувати роль:</span>
        <Select
          :modelValue="authStore.role"
          :options="roleOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Оберіть роль"
          class="role-select"
          @update:modelValue="changeRole"
        />
        <span v-if="authStore.user" class="user-badge">
          {{ authStore.roleLabel }}: {{ authStore.user.name }}
        </span>
        <Button
          v-if="authStore.role !== 'guest'"
          @click="handleLogout"
          severity="danger"
          size="small"
          icon="pi pi-sign-out"
          title="Вийти"
        />
      </div>
    </header>

    <div class="main-content">
      <aside class="sidebar">
        <Menu :model="menuItems" class="sidebar-menu w-full" />
      </aside>

      <main class="content-body">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style>
#app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: white;
  padding: 14px 24px;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.25);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.3rem;
  font-weight: bold;
}

.role-simulator {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.role-select {
  min-width: 200px;
}

.status-text {
  font-size: 0.9rem;
  color: #94a3b8;
  white-space: nowrap;
}

.user-badge {
  font-size: 0.85rem;
  color: #cbd5e1;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 280px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  padding: 16px 8px;
  overflow-y: auto;
}

.sidebar-menu {
  border: none;
  background: transparent;
}

.sidebar-menu .menu-item-active .p-menu-item-content {
  background: #e0f2fe;
  color: #0369a1;
}

.content-body {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  background: #f1f5f9;
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .role-simulator {
    width: 100%;
  }

  .role-select {
    flex: 1;
    min-width: 0;
  }

  .sidebar {
    width: 220px;
  }

  .content-body {
    padding: 16px;
  }
}
</style>
