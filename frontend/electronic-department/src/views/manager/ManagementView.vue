<script setup>
import { computed } from "vue";
import { useDepartmentStore } from "../../stores/department";
import { useAuthStore } from "../../stores/auth";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import Tab from "primevue/tab";
import TabPanels from "primevue/tabpanels";
import TabPanel from "primevue/tabpanel";

import ManageGroups from "../../components/ManageGroups.vue";
import ManageStudents from "../../components/ManageStudents.vue";
import ManageTeachers from "../../components/ManageTeachers.vue";
import ManageDisciplines from "../../components/ManageDisciplines.vue";

const department = useDepartmentStore();
const auth = useAuthStore();

const canEditDepartmentInfo = computed(() => auth.role === "admin");
</script>

<template>
  <div class="page-container page-wide max-w-7xl mx-auto">
    <div class="mb-6">
      <h2><i class="pi pi-sliders-h text-indigo-600"></i> Підсистема управління</h2>
      <p v-if="auth.role === 'admin'" class="text-slate-500">
        Адміністратор: повний доступ до структури кафедри та довідників.
      </p>
      <p v-else class="text-slate-500">
        Менеджер: додавання та редагування викладачів, студентів, груп і дисциплін.
      </p>
    </div>

    <!-- Admin Department Info Card -->
    <div v-if="canEditDepartmentInfo" class="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200/60 p-6 rounded-2xl mb-8 shadow-sm">
      <h3 class="text-amber-800 font-bold text-lg mb-4 flex items-center gap-2">
        <i class="pi pi-info-circle"></i> Інформація про кафедру (тільки адміністратор)
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex flex-col gap-2">
          <label class="font-semibold text-amber-950 text-sm">Назва кафедри</label>
          <InputText
            v-model="department.info.name"
            @change="department.persist()"
            class="w-full rounded-xl border-amber-200/80 focus:border-amber-500 bg-white"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="font-semibold text-amber-950 text-sm">Опис кафедри</label>
          <Textarea
            v-model="department.info.description"
            rows="2"
            autoResize
            @change="department.persist()"
            class="w-full rounded-xl border-amber-200/80 focus:border-amber-500 bg-white"
          />
        </div>
      </div>
    </div>

    <!-- Dynamic PrimeVue Tabs -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6">
      <Tabs value="groups">
        <TabList class="mb-4">
          <Tab value="groups" class="gap-2">
            <i class="pi pi-sitemap"></i> Групи
          </Tab>
          <Tab value="students" class="gap-2">
            <i class="pi pi-users"></i> Студенти
          </Tab>
          <Tab value="teachers" class="gap-2">
            <i class="pi pi-id-card"></i> Викладачі
          </Tab>
          <Tab value="disciplines" class="gap-2">
            <i class="pi pi-book"></i> Дисципліни
          </Tab>
        </TabList>

        <TabPanels class="pt-4">
          <TabPanel value="groups">
            <ManageGroups />
          </TabPanel>
          <TabPanel value="students">
            <ManageStudents />
          </TabPanel>
          <TabPanel value="teachers">
            <ManageTeachers />
          </TabPanel>
          <TabPanel value="disciplines">
            <ManageDisciplines />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </div>
  </div>
</template>

<style scoped>
.page-wide {
  max-width: 1400px;
}
</style>
