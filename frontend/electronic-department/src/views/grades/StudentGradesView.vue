<script setup>
import { computed } from 'vue';
import { useDepartmentStore } from '../../stores/department';
import { useAuthStore } from '../../stores/auth';
import { useListControls } from '../../composables/useListControls';

const department = useDepartmentStore();
const auth = useAuthStore();

const studentId = computed(() => auth.profileId);
const student = computed(() => department.studentById(studentId.value));

const gradesList = computed(() => {
  const id = studentId.value;
  if (id == null) return [];
  return department.studentGrades(id);
});

const { searchQuery, filterValue, filteredItems, toggleSort, sortIndicator } = useListControls(
  gradesList,
  ['discipline', 'teacher'],
  (item, filter) => item.ECTS === filter
);

const ectsOptions = ['Всі', 'A', 'B', 'C', 'D', 'E', 'F'];
</script>

<template>
  <div class="page-container">
    <h2><i class="pi pi-user"></i> Мої оцінки</h2>
    <p v-if="student">
      Студент: <strong>{{ student.name }}</strong>,
      група <span class="badge">{{ department.groupById(student.groupId)?.name }}</span>
    </p>
    <p v-else class="alert-warn">Профіль студента не знайдено. Увійдіть знову під роллю «Студент».</p>

    <template v-if="student">
      <div class="toolbar">
        <input v-model="searchQuery" type="text" placeholder="Пошук за дисципліною..." class="custom-input" />
        <select v-model="filterValue" class="custom-select">
          <option v-for="opt in ectsOptions" :key="opt" :value="opt">
            {{ opt === 'Всі' ? 'Всі оцінки ECTS' : `ECTS: ${opt}` }}
          </option>
        </select>
      </div>

      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleSort('discipline')">Дисципліна{{ sortIndicator('discipline') }}</th>
            <th>Викладач</th>
            <th class="sortable" @click="toggleSort('grade')">Бал{{ sortIndicator('grade') }}</th>
            <th>ECTS</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.discipline }}</strong></td>
            <td>{{ item.teacher }}</td>
            <td class="grade-cell">{{ item.grade }}</td>
            <td><span class="badge ects-badge">{{ item.ECTS }}</span></td>
          </tr>
          <tr v-if="filteredItems.length === 0">
            <td colspan="4" class="empty-row">Оцінок не знайдено</td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<style scoped>
.grade-cell { font-weight: bold; color: #1e3a8a; }
.ects-badge { background-color: #10b981; }
.sortable { cursor: pointer; }
.empty-row { text-align: center; color: #94a3b8; }
.alert-warn { background: #fef3c7; color: #92400e; padding: 12px; border-radius: 6px; margin-bottom: 12px; }
</style>
