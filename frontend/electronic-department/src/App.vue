<script setup>
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";
import { useDepartmentStore } from "./stores/department";
import { useRouter } from "vue-router";
import Button from "primevue/button";

const authStore = useAuthStore();
const departmentStore = useDepartmentStore();
const router = useRouter();

onMounted(async () => {
  // Load public resources (info, teachers, disciplines)
  await departmentStore.initPublic();

  // If simulated role is active, load private resources (groups, students, grades)
  if (authStore.role !== "guest") {
    await departmentStore.initPrivate(authStore.role, authStore.profileId);
  }
});

const changeRole = async (roleName) => {
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
        <Button
          @click="changeRole('guest')"
          :severity="authStore.role === 'guest' ? 'primary' : 'secondary'"
          size="small"
          label="Незареєстрований"
        />
        <Button
          @click="changeRole('admin')"
          :severity="authStore.role === 'admin' ? 'primary' : 'secondary'"
          size="small"
          label="Адміністратор"
        />
        <Button
          @click="changeRole('manager')"
          :severity="authStore.role === 'manager' ? 'primary' : 'secondary'"
          size="small"
          label="Менеджер"
        />
        <Button
          @click="changeRole('teacher')"
          :severity="authStore.role === 'teacher' ? 'primary' : 'secondary'"
          size="small"
          label="Викладач"
        />
        <Button
          @click="changeRole('student')"
          :severity="authStore.role === 'student' ? 'primary' : 'secondary'"
          size="small"
          label="Студент"
        />
        <span v-if="authStore.user" class="user-badge"
          >{{ authStore.roleLabel }}: {{ authStore.user.name }}</span
        >
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
        <router-link to="/" class="nav-item">
          <i class="pi pi-home"></i> Загальна інформація
        </router-link>

        <router-link
          v-if="
            ['admin', 'manager', 'teacher', 'student'].includes(authStore.role)
          "
          to="/browse"
          class="nav-item"
        >
          <i class="pi pi-list"></i> Вивід даних (Підсистема 2)
        </router-link>

        <router-link
          v-if="authStore.canManage"
          to="/management"
          class="nav-item"
        >
          <i class="pi pi-sliders-h"></i> Управління (Підсистема 1)
        </router-link>

        <router-link v-if="authStore.isTeacher" to="/journal" class="nav-item">
          <i class="pi pi-book"></i> Журнал оцінок (Підсистема 3)
        </router-link>

        <router-link
          v-if="authStore.isStudent"
          to="/my-grades"
          class="nav-item"
        >
          <i class="pi pi-user"></i> Мої оцінки (Підсистема 3)
        </router-link>
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
  background: #1e293b;
  color: white;
  padding: 15px 25px;
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
  gap: 8px;
  align-items: center;
}
.status-text {
  font-size: 0.9rem;
  color: #94a3b8;
}
.user-badge {
  font-size: 0.85rem;
  color: #94a3b8;
  margin-left: 8px;
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
  width: 260px;
  background: #f8fafc;
  border-right: 1px solid #e2e8f0;
  padding: 20px 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  color: #334155;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
}
.nav-item:hover {
  background: #f1f5f9;
}
.nav-item.router-link-active {
  background: #e0f2fe;
  color: #0369a1;
}
.content-body {
  flex: 1;
  padding: 30px;
  overflow-y: auto;
  background: #ffffff;
}
</style>
