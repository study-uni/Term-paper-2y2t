import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
  {
    path: "/",
    component: () => import("../views/public/GeneralInfoView.vue"),
  },
  {
    path: "/browse",
    component: () => import("../views/browse/BrowseView.vue"),
    meta: { roles: ["admin", "manager", "teacher", "student"] },
  },
  {
    path: "/management",
    component: () => import("../views/manager/ManagementView.vue"),
    meta: { roles: ["admin", "manager"] },
  },
  {
    path: "/journal",
    component: () => import("../views/grades/JournalView.vue"),
    meta: { roles: ["teacher"] },
  },
  {
    path: "/my-grades",
    component: () => import("../views/grades/StudentGradesView.vue"),
    meta: { roles: ["student"] },
  },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  if (to.meta.roles && !to.meta.roles.includes(authStore.role)) {
    return next({ path: "/", replace: true });
  }
  next();
});
