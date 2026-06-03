<script setup>
import { computed } from "vue";
import { useDepartmentStore } from "../../stores/department";
import { useAuthStore } from "../../stores/auth";
import { useListControls } from "../../composables/useListControls";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Select from "primevue/select";

const department = useDepartmentStore();
const auth = useAuthStore();

const studentId = computed(() => auth.profileId);
const student = computed(() => department.studentById(studentId.value));

const gradesList = computed(() => {
  const id = studentId.value;
  if (id == null) return [];
  return department.studentGrades(id);
});

const { searchQuery, filterValue, filteredItems } = useListControls(
  gradesList,
  ["discipline", "teacher"],
  (item, filter) => item.ECTS === filter,
);

const ectsSelectOptions = [
  { label: "Всі оцінки ECTS", value: "Всі" },
  { label: "ECTS: A", value: "A" },
  { label: "ECTS: B", value: "B" },
  { label: "ECTS: C", value: "C" },
  { label: "ECTS: D", value: "D" },
  { label: "ECTS: E", value: "E" },
  { label: "ECTS: F", value: "F" },
];
</script>

<template>
  <div class="page-container">
    <h2><i class="pi pi-user"></i> Мої оцінки</h2>
    <p v-if="student">
      Студент: <strong>{{ student.name }}</strong
      >, група
      <span class="badge">{{
        department.groupById(student.groupId)?.name
      }}</span>
    </p>
    <p v-else class="alert-warn">
      Профіль студента не знайдено. Увійдіть знову під роллю «Студент».
    </p>

    <template v-if="student">
      <div class="toolbar flex gap-3 items-center">
        <InputText
          v-model="searchQuery"
          placeholder="Пошук за дисципліною..."
          class="flex-1"
        />
        <Select
          v-model="filterValue"
          :options="ectsSelectOptions"
          optionLabel="label"
          optionValue="value"
          class="w-64"
        />
      </div>

      <DataTable
        :value="filteredItems"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column
          field="discipline"
          header="Дисципліна"
          sortable
          style="font-weight: bold"
        ></Column>
        <Column field="teacher" header="Викладач"></Column>
        <Column field="grade" header="Бал" sortable>
          <template #body="slotProps">
            <span class="grade-cell">{{ slotProps.data.grade }}</span>
          </template>
        </Column>
        <Column field="ECTS" header="ECTS">
          <template #body="slotProps">
            <span class="badge ects-badge">{{ slotProps.data.ECTS }}</span>
          </template>
        </Column>
      </DataTable>
    </template>
  </div>
</template>

<style scoped>
.grade-cell {
  font-weight: bold;
  color: #1e3a8a;
}
.ects-badge {
  background-color: #10b981;
}
.alert-warn {
  background: #fef3c7;
  color: #92400e;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}
</style>
