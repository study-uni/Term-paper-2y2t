<script setup>
import { ref, computed } from 'vue';
import { useDepartmentStore } from '../../stores/department';
import { useAuthStore } from '../../stores/auth';
import { useListControls } from '../../composables/useListControls';

const department = useDepartmentStore();
const auth = useAuthStore();

const selectedDisciplineId = ref(null);
const lastUpdatedStudent = ref('');

const teacherId = computed(() => auth.profileId);
const teacher = computed(() => department.teacherById(teacherId.value));

const teacherDisciplines = computed(() => {
  const t = teacher.value;
  if (!t) return [];
  return t.disciplineIds
    .map((id) => department.disciplineById(id))
    .filter(Boolean);
});

const journalRows = computed(() => {
  if (!teacherId.value) return [];
  let rows = department.journalForTeacher(teacherId.value);
  if (selectedDisciplineId.value != null) {
    rows = rows.filter((r) => r.disciplineId === selectedDisciplineId.value);
  }
  return rows;
});

const { searchQuery, filteredItems, toggleSort, sortIndicator } = useListControls(
  journalRows,
  ['student', 'subject']
);

const updateGrade = (row) => {
  const value = Math.min(100, Math.max(0, Number(row.grade) || 0));
  department.updateGrade(row.id, value);
  row.grade = value;
  lastUpdatedStudent.value = row.student;
  setTimeout(() => { lastUpdatedStudent.value = ''; }, 3000);
};
</script>

<template>
  <div class="page-container">
    <h2><i class="pi pi-book"></i> Журнал оцінок</h2>
    <p v-if="teacher">
      Викладач: <strong>{{ teacher.name }}</strong>. Оцінки лише по дисциплінах, які ви викладаєте.
    </p>
    <p v-else class="alert-warn">Профіль викладача не знайдено. Увійдіть знову під роллю «Викладач».</p>

    <div v-if="teacher && teacherDisciplines.length === 0" class="alert-warn">
      У вашому профілі не призначено дисциплін. Зверніться до менеджера кафедри.
    </div>

    <template v-else-if="teacher">
      <div class="toolbar">
        <select v-model="selectedDisciplineId" class="custom-select">
          <option :value="null">Всі мої дисципліни</option>
          <option v-for="d in teacherDisciplines" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
        <input v-model="searchQuery" type="text" placeholder="Пошук студента..." class="custom-input" />
      </div>

      <div v-if="lastUpdatedStudent" class="alert-success">
        <i class="pi pi-check"></i> Оцінку для <strong>{{ lastUpdatedStudent }}</strong> збережено.
      </div>

      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleSort('student')">Студент{{ sortIndicator('student') }}</th>
            <th class="sortable" @click="toggleSort('subject')">Дисципліна{{ sortIndicator('subject') }}</th>
            <th>Оцінка (0–100)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in filteredItems" :key="row.id">
            <td>{{ row.student }}</td>
            <td>{{ row.subject }}</td>
            <td>
              <input
                type="number"
                v-model.number="row.grade"
                @change="updateGrade(row)"
                min="0"
                max="100"
                class="grade-input"
              />
            </td>
          </tr>
          <tr v-if="filteredItems.length === 0">
            <td colspan="3" class="empty-row">Записів немає</td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<style scoped>
.grade-input { width: 70px; padding: 6px; border: 1px solid #ccc; border-radius: 4px; text-align: center; font-weight: bold; }
.alert-success { background: #dcfce7; color: #166534; padding: 10px 15px; border-radius: 6px; margin-bottom: 15px; }
.alert-warn { background: #fef3c7; color: #92400e; padding: 12px; border-radius: 6px; margin-bottom: 12px; }
.sortable { cursor: pointer; }
.empty-row { text-align: center; color: #94a3b8; }
</style>
