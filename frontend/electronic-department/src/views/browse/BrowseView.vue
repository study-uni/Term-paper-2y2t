<script setup>
import { computed, ref } from 'vue';
import { storeToRefs } from 'pinia';
import { useDepartmentStore } from '../../stores/department';
import { useListControls } from '../../composables/useListControls';

const department = useDepartmentStore();
const { teachers, students, groups, disciplines } = storeToRefs(department);

const activeTab = ref('students');

const studentsDisplay = computed(() =>
  students.value.map((s) => ({
    id: s.id,
    name: s.name,
    group: department.groupById(s.groupId)?.name ?? '—',
    groupId: s.groupId,
  }))
);

const teachersDisplay = computed(() =>
  teachers.value.map((t) => ({
    id: t.id,
    name: t.name,
    position: t.position,
    disciplines: department.teacherDisciplineNames(t.id).join(', ') || '—',
  }))
);

const groupFilterOptions = computed(() => ['Всі', ...groups.value.map((g) => g.name)]);

const {
  searchQuery: studentSearch,
  filterValue: studentGroupFilter,
  filteredItems: filteredStudents,
  toggleSort: toggleStudentSort,
  sortIndicator: studentSortIndicator,
} = useListControls(studentsDisplay, ['name', 'group'], (item, filter) => item.group === filter);

const {
  searchQuery: teacherSearch,
  filterValue: teacherPositionFilter,
  filteredItems: filteredTeachersList,
  toggleSort: toggleTeacherSort,
  sortIndicator: teacherSortIndicator,
} = useListControls(
  teachersDisplay,
  ['name', 'disciplines', 'position'],
  (item, filter) => item.position === filter
);

const {
  searchQuery: groupSearch,
  filteredItems: filteredGroups,
  toggleSort: toggleGroupSort,
  sortIndicator: groupSortIndicator,
} = useListControls(groups, ['name']);

const {
  searchQuery: disciplineSearch,
  filteredItems: filteredDisciplinesList,
  toggleSort: toggleDisciplineSort,
  sortIndicator: disciplineSortIndicator,
} = useListControls(disciplines, ['name', 'description']);

const tabs = [
  { id: 'students', label: 'Студенти', icon: 'pi-users' },
  { id: 'teachers', label: 'Викладачі', icon: 'pi-id-card' },
  { id: 'groups', label: 'Групи', icon: 'pi-sitemap' },
  { id: 'disciplines', label: 'Дисципліни', icon: 'pi-book' },
];
</script>

<template>
  <div class="page-container page-wide">
    <h2><i class="pi pi-list"></i> Підсистема виводу</h2>
    <p>Перегляд структури кафедри з пошуком, фільтрами та сортуванням.</p>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <i :class="['pi', tab.icon]"></i> {{ tab.label }}
      </button>
    </div>

    <template v-if="activeTab === 'students'">
      <div class="toolbar">
        <input v-model="studentSearch" type="text" placeholder="Пошук студента..." class="custom-input" />
        <select v-model="studentGroupFilter" class="custom-select">
          <option v-for="g in groupFilterOptions" :key="g" :value="g">{{ g === 'Всі' ? 'Всі групи' : g }}</option>
        </select>
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleStudentSort('name')">ПІБ{{ studentSortIndicator('name') }}</th>
            <th class="sortable" @click="toggleStudentSort('group')">Група{{ studentSortIndicator('group') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in filteredStudents" :key="s.id">
            <td>{{ s.name }}</td>
            <td><span class="badge">{{ s.group }}</span></td>
          </tr>
          <tr v-if="filteredStudents.length === 0">
            <td colspan="2" class="empty-row">Немає записів</td>
          </tr>
        </tbody>
      </table>
    </template>

    <template v-if="activeTab === 'teachers'">
      <div class="toolbar">
        <input v-model="teacherSearch" type="text" placeholder="Пошук викладача..." class="custom-input" />
        <select v-model="teacherPositionFilter" class="custom-select">
          <option value="Всі">Всі посади</option>
          <option value="Професор">Професор</option>
          <option value="Доцент">Доцент</option>
          <option value="Асистент">Асистент</option>
        </select>
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleTeacherSort('name')">ПІБ{{ teacherSortIndicator('name') }}</th>
            <th class="sortable" @click="toggleTeacherSort('position')">Посада{{ teacherSortIndicator('position') }}</th>
            <th>Дисципліни</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTeachersList" :key="t.id">
            <td>{{ t.name }}</td>
            <td>{{ t.position }}</td>
            <td>{{ t.disciplines }}</td>
          </tr>
          <tr v-if="filteredTeachersList.length === 0">
            <td colspan="3" class="empty-row">Немає записів</td>
          </tr>
        </tbody>
      </table>
    </template>

    <template v-if="activeTab === 'groups'">
      <div class="toolbar">
        <input v-model="groupSearch" type="text" placeholder="Пошук групи..." class="custom-input" />
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleGroupSort('name')">Назва групи{{ groupSortIndicator('name') }}</th>
            <th>Кількість студентів</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in filteredGroups" :key="g.id">
            <td><strong>{{ g.name }}</strong></td>
            <td>{{ students.filter((s) => s.groupId === g.id).length }}</td>
          </tr>
          <tr v-if="filteredGroups.length === 0">
            <td colspan="2" class="empty-row">Немає записів</td>
          </tr>
        </tbody>
      </table>
    </template>

    <template v-if="activeTab === 'disciplines'">
      <div class="toolbar">
        <input v-model="disciplineSearch" type="text" placeholder="Пошук дисципліни..." class="custom-input" />
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleDisciplineSort('name')">Назва{{ disciplineSortIndicator('name') }}</th>
            <th>Опис</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filteredDisciplinesList" :key="d.id">
            <td>{{ d.name }}</td>
            <td>{{ d.description }}</td>
          </tr>
          <tr v-if="filteredDisciplinesList.length === 0">
            <td colspan="2" class="empty-row">Немає записів</td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<style scoped>
.page-wide { max-width: 1000px; }
.tabs { display: flex; gap: 8px; margin-bottom: 20px; flex-wrap: wrap; }
.tabs button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 6px;
  cursor: pointer;
  color: #475569;
  font-weight: 500;
}
.tabs button.active { background: #3b82f6; color: white; border-color: #3b82f6; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #0369a1; }
.empty-row { text-align: center; color: #94a3b8; }
</style>
