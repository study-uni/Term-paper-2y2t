<script setup>
import { ref, computed, watch } from "vue";
import { useDepartmentStore } from "../../stores/department";
import { useAuthStore } from "../../stores/auth";
import { useListControls } from "../../composables/useListControls";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import InputNumber from "primevue/inputnumber";
import Select from "primevue/select";

const department = useDepartmentStore();
const auth = useAuthStore();

const selectedDisciplineId = ref(null);
const lastUpdatedStudent = ref("");

// Fetch grades when selected discipline changes
watch(selectedDisciplineId, async (newVal) => {
  try {
    await department.fetchGradesForTeacher(newVal);
  } catch (e) {
    console.error("Failed to fetch journal grades:", e);
  }
});

const teacherId = computed(() => auth.profileId);
const teacher = computed(() => department.teacherById(teacherId.value));

const teacherDisciplines = computed(() => {
  const t = teacher.value;
  if (!t) return [];
  return t.disciplineIds
    .map((id) => department.disciplineById(id))
    .filter(Boolean);
});

const disciplineOptions = computed(() => [
  { label: "Всі мої дисципліни", value: null },
  ...teacherDisciplines.value.map((d) => ({ label: d.name, value: d.id })),
]);

const journalRows = computed(() => {
  if (!teacherId.value) return [];
  let rows = department.journalForTeacher(teacherId.value);
  if (selectedDisciplineId.value != null) {
    rows = rows.filter((r) => r.discipline_id === selectedDisciplineId.value);
  }
  return rows;
});

const { searchQuery, filteredItems } = useListControls(journalRows, [
  "student",
  "subject",
]);

const updateGrade = async (row) => {
  const value = Math.min(100, Math.max(0, Number(row.grade) || 0));
  try {
    await department.updateGrade(row.id, value);
    row.grade = value;
    lastUpdatedStudent.value = row.student;
    setTimeout(() => {
      lastUpdatedStudent.value = "";
    }, 3000);
  } catch (e) {
    console.error("Failed to update grade:", e);
  }
};
</script>

<template>
  <div class="page-container">
    <h2><i class="pi pi-book"></i> Журнал оцінок</h2>
    <p v-if="teacher">
      Викладач: <strong>{{ teacher.name }}</strong
      >. Оцінки лише по дисциплінах, які ви викладаєте.
    </p>
    <p v-else class="alert-warn">
      Профіль викладача не знайдено. Увійдіть знову під роллю «Викладач».
    </p>

    <div v-if="teacher && teacherDisciplines.length === 0" class="alert-warn">
      У вашому профілі не призначено дисциплін. Зверніться до менеджера кафедри.
    </div>

    <template v-else-if="teacher">
      <div class="toolbar flex gap-3 items-center">
        <Select
          v-model="selectedDisciplineId"
          :options="disciplineOptions"
          optionLabel="label"
          optionValue="value"
          class="w-80"
        />
        <InputText
          v-model="searchQuery"
          placeholder="Пошук студента..."
          class="flex-1"
        />
      </div>

      <div v-if="lastUpdatedStudent" class="alert-success">
        <i class="pi pi-check"></i> Оцінку для
        <strong>{{ lastUpdatedStudent }}</strong> збережено.
      </div>

      <DataTable
        :value="filteredItems"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column field="student" header="Студент" sortable></Column>
        <Column field="subject" header="Дисципліна" sortable></Column>
        <Column header="Оцінка (0–100)">
          <template #body="slotProps">
            <InputNumber
              v-model="slotProps.data.grade"
              :min="0"
              :max="100"
              :useGrouping="false"
              inputClass="grade-input"
              @blur="updateGrade(slotProps.data)"
            />
          </template>
        </Column>
        <template #empty>
          <div class="empty-message">Записів не знайдено.</div>
        </template>
      </DataTable>
    </template>
  </div>
</template>

<style scoped>
.alert-success {
  background: #dcfce7;
  color: #166534;
  padding: 10px 15px;
  border-radius: 6px;
  margin-bottom: 15px;
}
.alert-warn {
  background: #fef3c7;
  color: #92400e;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}
.empty-row {
  text-align: center;
  color: #94a3b8;
}
</style>
