<script setup>
import { computed, ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../../stores/department";
import { useListControls } from "../../composables/useListControls";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Button from "primevue/button";

const department = useDepartmentStore();
const { teachers, students, groups, disciplines } = storeToRefs(department);

const activeTab = ref("students");

const studentsDisplay = computed(() =>
  students.value.map((s) => ({
    id: s.id,
    name: s.name,
    group:
      s.groupName ?? department.groupById(s.groupId)?.name ?? "—",
    groupId: s.groupId,
  })),
);

const teachersDisplay = computed(() =>
  teachers.value.map((t) => ({
    id: t.id,
    name: t.name,
    position: t.position,
    disciplines: department.teacherDisciplineNames(t.id).join(", ") || "—",
  })),
);

const groupFilterOptions = computed(() => [
  { label: "Всі групи", value: "Всі" },
  ...groups.value.map((g) => ({ label: g.name, value: g.name })),
]);

const positionFilterOptions = [
  { label: "Всі посади", value: "Всі" },
  { label: "Професор", value: "Професор" },
  { label: "Доцент", value: "Доцент" },
  { label: "Асистент", value: "Асистент" },
];

const {
  searchQuery: studentSearch,
  filterValue: studentGroupFilter,
  filteredItems: filteredStudents,
} = useListControls(
  studentsDisplay,
  ["name", "group"],
  (item, filter) => item.group === filter,
);

const {
  searchQuery: teacherSearch,
  filterValue: teacherPositionFilter,
  filteredItems: filteredTeachersList,
} = useListControls(
  teachersDisplay,
  ["name", "disciplines", "position"],
  (item, filter) => item.position === filter,
);

const { searchQuery: groupSearch, filteredItems: filteredGroups } =
  useListControls(groups, ["name"]);

const {
  searchQuery: disciplineSearch,
  filteredItems: filteredDisciplinesList,
} = useListControls(disciplines, ["name", "description"]);

const tabs = [
  { id: "students", label: "Студенти", icon: "pi-users" },
  { id: "teachers", label: "Викладачі", icon: "pi-id-card" },
  { id: "groups", label: "Групи", icon: "pi-sitemap" },
  { id: "disciplines", label: "Дисципліни", icon: "pi-book" },
];
</script>

<template>
  <div class="page-container page-wide">
    <h2><i class="pi pi-list"></i> Підсистема виводу</h2>
    <p>Перегляд структури кафедри з пошуком, фільтрами та сортуванням.</p>

    <div class="tabs flex gap-2 mb-4">
      <Button
        v-for="tab in tabs"
        :key="tab.id"
        :severity="activeTab === tab.id ? 'primary' : 'secondary'"
        :icon="'pi ' + tab.icon"
        :label="tab.label"
        @click="activeTab = tab.id"
      />
    </div>

    <template v-if="activeTab === 'students'">
      <div class="toolbar flex gap-3 items-center">
        <InputText
          v-model="studentSearch"
          placeholder="Пошук студента..."
          class="flex-1"
        />
        <Select
          v-model="studentGroupFilter"
          :options="groupFilterOptions"
          optionLabel="label"
          optionValue="value"
          class="w-64"
        />
      </div>

      <DataTable
        :value="filteredStudents"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column field="name" header="ПІБ" sortable></Column>
        <Column field="group" header="Група">
          <template #body="slotProps">
            <span class="badge">{{ slotProps.data.group }}</span>
          </template>
        </Column>
        <template #empty>
          <div class="empty-message">Студентів не знайдено.</div>
        </template>
      </DataTable>
    </template>

    <template v-if="activeTab === 'teachers'">
      <div class="toolbar flex gap-3 items-center">
        <InputText
          v-model="teacherSearch"
          placeholder="Пошук викладача..."
          class="flex-1"
        />
        <Select
          v-model="teacherPositionFilter"
          :options="positionFilterOptions"
          optionLabel="label"
          optionValue="value"
          class="w-64"
        />
      </div>

      <DataTable
        :value="filteredTeachersList"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column field="name" header="ПІБ" sortable></Column>
        <Column field="position" header="Посада" sortable></Column>
        <Column field="disciplines" header="Дисципліни"></Column>
        <template #empty>
          <div class="empty-message">Викладачів не знайдено.</div>
        </template>
      </DataTable>
    </template>

    <template v-if="activeTab === 'groups'">
      <div class="toolbar">
        <InputText
          v-model="groupSearch"
          placeholder="Пошук групи..."
          class="flex-1"
        />
      </div>

      <DataTable
        :value="filteredGroups"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column
          field="name"
          header="Назва групи"
          sortable
          style="font-weight: bold"
        ></Column>
        <Column header="Кількість студентів">
          <template #body="slotProps">
            {{
              slotProps.data.student_count ??
              students.filter((s) => s.groupId === slotProps.data.id).length
            }}
          </template>
        </Column>
        <template #empty>
          <div class="empty-message">Груп не знайдено.</div>
        </template>
      </DataTable>
    </template>

    <template v-if="activeTab === 'disciplines'">
      <div class="toolbar">
        <InputText
          v-model="disciplineSearch"
          placeholder="Пошук дисципліни..."
          class="flex-1"
        />
      </div>

      <DataTable
        :value="filteredDisciplinesList"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column
          field="name"
          header="Назва"
          sortable
          style="font-weight: bold"
        ></Column>
        <Column field="description" header="Опис"></Column>
        <template #empty>
          <div class="empty-message">Дисциплін не знайдено.</div>
        </template>
      </DataTable>
    </template>
  </div>
</template>

<style scoped>
.page-wide {
  max-width: 1200px;
}
.empty-row {
  text-align: center;
  color: #94a3b8;
}
</style>
