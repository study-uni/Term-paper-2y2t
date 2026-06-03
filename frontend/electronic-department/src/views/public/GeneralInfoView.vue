<script setup>
import { computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDepartmentStore } from '../../stores/department';
import { useListControls } from '../../composables/useListControls';

const department = useDepartmentStore();
const { info, teachers, disciplines } = storeToRefs(department);

const teachersForDisplay = computed(() =>
  teachers.value.map((t) => ({
    id: t.id,
    name: t.name,
    position: t.position,
    subject: department.teacherDisciplineNames(t.id).join(', ') || '—',
  }))
);

const {
  searchQuery,
  filterValue,
  filteredItems: filteredTeachers,
  toggleSort,
  sortIndicator,
} = useListControls(teachersForDisplay, ['name', 'subject', 'position'], (item, filter) => item.position === filter);

const {
  searchQuery: disciplineSearch,
  filteredItems: filteredDisciplines,
  toggleSort: toggleDisciplineSort,
  sortIndicator: disciplineSortIndicator,
} = useListControls(disciplines, ['name', 'description']);
</script>

<template>
  <div class="page-container page-wide">
    <h2><i class="pi pi-info-circle"></i> Про кафедру</h2>
    <p>Загальна інформація для незареєстрованих та всіх відвідувачів.</p>

    <section class="info-card">
      <h3>{{ info.name }}</h3>
      <p class="info-desc">{{ info.description }}</p>
      <div class="info-meta">
        <span><i class="pi pi-user"></i> Завідувач: <strong>{{ info.head }}</strong></span>
        <span><i class="pi pi-envelope"></i> {{ info.email }}</span>
        <span><i class="pi pi-phone"></i> {{ info.phone }}</span>
      </div>
    </section>

    <section class="section-block">
      <h3><i class="pi pi-users"></i> Викладачі кафедри</h3>
      <div class="toolbar">
        <input v-model="searchQuery" type="text" placeholder="Пошук за ПІБ або дисципліною..." class="custom-input" />
        <select v-model="filterValue" class="custom-select">
          <option value="Всі">Всі посади</option>
          <option value="Професор">Професор</option>
          <option value="Доцент">Доцент</option>
          <option value="Асистент">Асистент</option>
        </select>
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleSort('name')">ПІБ{{ sortIndicator('name') }}</th>
            <th class="sortable" @click="toggleSort('position')">Посада{{ sortIndicator('position') }}</th>
            <th class="sortable" @click="toggleSort('subject')">Дисципліни{{ sortIndicator('subject') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in filteredTeachers" :key="t.id">
            <td>{{ t.name }}</td>
            <td><span class="badge">{{ t.position }}</span></td>
            <td>{{ t.subject }}</td>
          </tr>
          <tr v-if="filteredTeachers.length === 0">
            <td colspan="3" class="empty-row">Нічого не знайдено</td>
          </tr>
        </tbody>
      </table>
    </section>

    <section class="section-block">
      <h3><i class="pi pi-book"></i> Дисципліни кафедри</h3>
      <div class="toolbar">
        <input v-model="disciplineSearch" type="text" placeholder="Пошук за назвою..." class="custom-input" />
      </div>
      <table class="custom-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleDisciplineSort('name')">Назва{{ disciplineSortIndicator('name') }}</th>
            <th>Опис</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="d in filteredDisciplines" :key="d.id">
            <td><strong>{{ d.name }}</strong></td>
            <td>{{ d.description }}</td>
          </tr>
          <tr v-if="filteredDisciplines.length === 0">
            <td colspan="2" class="empty-row">Нічого не знайдено</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.page-wide { max-width: 1000px; }
.info-card {
  background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 28px;
}
.info-card h3 { color: #1e40af; margin-bottom: 10px; }
.info-desc { color: #475569; line-height: 1.6; margin-bottom: 14px; }
.info-meta { display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.95rem; color: #334155; }
.info-meta i { color: #3b82f6; margin-right: 4px; }
.section-block { margin-bottom: 32px; }
.section-block h3 { color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.sortable { cursor: pointer; user-select: none; }
.sortable:hover { color: #0369a1; }
.empty-row { text-align: center; color: #94a3b8; }
</style>
