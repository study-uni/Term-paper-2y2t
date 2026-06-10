<script setup>
import { ref, computed } from "vue";
import { useDepartmentStore } from "../../stores/department";
import { useAuthStore } from "../../stores/auth";
import Tabs from "primevue/tabs";
import TabList from "primevue/tablist";
import Tab from "primevue/tab";
import TabPanels from "primevue/tabpanels";
import TabPanel from "primevue/tabpanel";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import ManageGroups from "../../components/ManageGroups.vue";
import ManageStudents from "../../components/ManageStudents.vue";
import ManageTeachers from "../../components/ManageTeachers.vue";
import ManageDisciplines from "../../components/ManageDisciplines.vue";

const department = useDepartmentStore();
const auth = useAuthStore();

const activeTab = ref("groups");

const canEditDepartmentInfo = computed(() => auth.role === "admin");
</script>

<template>
  <div class="page-container">
    <h2><i class="pi pi-sliders-h"></i> Підсистема управління</h2>
    <p v-if="auth.role === 'admin'">
      Адміністратор: повний доступ до структури кафедри та довідників.
    </p>
    <p v-else>
      Менеджер: додавання та редагування викладачів, студентів, груп і
      дисциплін.
    </p>

    <div v-if="canEditDepartmentInfo" class="admin-info">
      <h4>Інформація про кафедру (тільки адміністратор)</h4>
      <div class="flex flex-col gap-2 mt-2">
        <label class="font-medium text-amber-900 text-sm">Назва кафедри</label>
        <InputText
          v-model="department.info.name"
          @change="department.persist()"
          class="w-full"
        />

        <label class="font-medium text-amber-900 text-sm mt-2"
          >Опис кафедри</label
        >
        <Textarea
          v-model="department.info.description"
          rows="3"
          autoResize
          @change="department.persist()"
          class="w-full"
        />
      </div>
    </div>

    <Tabs v-model:value="activeTab" class="mt-4">
      <TabList>
        <Tab value="groups">Групи</Tab>
        <Tab value="students">Студенти</Tab>
        <Tab value="teachers">Викладачі</Tab>
        <Tab value="disciplines">Дисципліни</Tab>
      </TabList>
      <TabPanels>
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
</template>

<style scoped>
.admin-info {
  background: #fef3c7;
  border: 1px solid #fcd34d;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.admin-info h4 {
  color: #92400e;
  margin-bottom: 8px;
}
</style>
