<script setup>
import { onMounted, ref, computed } from "vue";
import { useAuthStore } from "./stores/auth";
import { useDepartmentStore } from "./stores/department";
import { useRouter } from "vue-router";
import Button from "primevue/button";
import Select from "primevue/select";
import Menu from "primevue/menu";

const authStore = useAuthStore();
const departmentStore = useDepartmentStore();
const router = useRouter();

const roleOptions = [
  { label: "Незареєстрований", value: "guest" },
  { label: "Адміністратор", value: "admin" },
  { label: "Менеджер", value: "manager" },
  { label: "Викладач", value: "teacher" },
  { label: "Студент", value: "student" },
];

const selectedRole = ref(authStore.role);

onMounted(async () => {
  await departmentStore.initPublic();

  if (authStore.role !== "guest") {
    await departmentStore.initPrivate(authStore.role, authStore.profileId);
  }
});

const changeRole = async (roleName) => {
  try {
    await authStore.login(roleName);
    selectedRole.value = roleName;

    if (roleName === "guest") {
      departmentStore.clearPrivate();
    } else {
      await departmentStore.initPrivate(authStore.role, authStore.profileId);
    }

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
    selectedRole.value = authStore.role;
  }
};

const onRoleSelect = (roleName) => {
  if (roleName && roleName !== authStore.role) {
    changeRole(roleName);
  }
};

const handleLogout = () => {
  authStore.logout();
  selectedRole.value = "guest";
  departmentStore.clearPrivate();
  router.push("/");
};

const menuItems = computed(() => {
  const items = [
    {
      label: "Загальна інформація",
      icon: "pi pi-home",
      route: "/",
    }
  ];

  if (["admin", "manager", "teacher", "student"].includes(authStore.role)) {
    items.push({
      label: "Вивід даних (П2)",
      icon: "pi pi-list",
      route: "/browse",
    });
  }

  if (authStore.canManage) {
    items.push({
      label: "Управління (П1)",
      icon: "pi pi-sliders-h",
      route: "/management",
    });
  }

  if (authStore.isTeacher) {
    items.push({
      label: "Журнал оцінок (П3)",
      icon: "pi pi-book",
      route: "/journal",
    });
  }

  if (authStore.isStudent) {
    items.push({
      label: "Мої оцінки (П3)",
      icon: "pi pi-user",
      route: "/my-grades",
    });
  }

  return items;
});
</script>

<template>
  <div id="app-layout" class="flex flex-col h-screen overflow-hidden bg-slate-50">
    <header class="app-header bg-slate-900 text-white px-6 py-4 flex justify-between items-center z-10 shadow-lg">
      <div class="logo flex items-center gap-3 select-none">
        <div class="logo-icon bg-gradient-to-tr from-indigo-500 to-purple-500 w-10 h-10 rounded-xl flex items-center justify-center shadow-md shadow-indigo-500/20">
          <i class="pi pi-graduation-cap text-white text-xl"></i>
        </div>
        <span class="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
          Електронна Кафедра
        </span>
      </div>

      <div class="role-simulator flex gap-4 items-center flex-wrap justify-end">
        <div class="flex items-center gap-2">
          <span class="status-text text-slate-400 text-sm font-medium">Тестувати роль:</span>
          <Select
            v-model="selectedRole"
            :options="roleOptions"
            optionLabel="label"
            optionValue="value"
            class="role-select rounded-xl border-slate-700 bg-slate-800 text-white text-sm"
            @update:model-value="onRoleSelect"
          />
        </div>
        
        <div v-if="authStore.user" class="flex items-center gap-3 bg-slate-800/60 border border-slate-700/50 px-4 py-2 rounded-xl">
          <span class="text-xs text-indigo-400 font-semibold uppercase tracking-wider">{{ authStore.roleLabel }}</span>
          <span class="text-sm text-slate-200 font-medium truncate max-w-[180px]" :title="authStore.user.name">
            {{ authStore.user.name }}
          </span>
        </div>

        <Button
          v-if="authStore.role !== 'guest'"
          @click="handleLogout"
          severity="danger"
          outlined
          size="small"
          icon="pi pi-sign-out"
          class="rounded-xl border-red-500/40 text-red-400 hover:bg-red-500/10"
          title="Вийти"
        />
      </div>
    </header>

    <div class="main-content flex flex-1 overflow-hidden">
      <aside class="sidebar w-72 bg-white border-r border-slate-200 p-4 flex flex-col gap-6 z-0 shadow-sm">
        <div class="px-3 py-2">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">Навігація</span>
        </div>
        <Menu :model="menuItems" class="w-full border-none bg-transparent p-0">
          <template #item="{ item, props }">
            <router-link v-if="item.route" v-slot="{ href, navigate, isActive }" :to="item.route" custom>
              <a
                :href="href"
                v-bind="props.action"
                @click="navigate"
                :class="[
                  'nav-item flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group border border-transparent my-1',
                  isActive 
                    ? 'bg-indigo-50/70 border-indigo-100/50 text-indigo-600 font-semibold shadow-sm shadow-indigo-500/5' 
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                ]"
              >
                <span :class="[item.icon, 'text-lg transition-transform duration-200 group-hover:scale-110', isActive ? 'text-indigo-600' : 'text-slate-400 group-hover:text-slate-600']"></span>
                <span class="text-sm font-medium">{{ item.label }}</span>
              </a>
            </router-link>
          </template>
        </Menu>
      </aside>

      <main class="content-body flex-1 overflow-y-auto bg-slate-50/50">
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
/* PrimeVue component overrides to match our design */
.p-menu {
  border: none !important;
  background: transparent !important;
  padding: 0 !important;
}
.p-menu-list {
  padding: 0 !important;
  list-style: none;
}
.p-menuitem {
  margin: 0 !important;
}
.p-menuitem-content {
  background: transparent !important;
}

.role-select {
  min-width: 180px;
}
</style>
