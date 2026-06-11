<script setup>
import { computed } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../../stores/department";
import { useListControls } from "../../composables/useListControls";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Select from "primevue/select";

const department = useDepartmentStore();
const { info, teachers, disciplines } = storeToRefs(department);

const teachersForDisplay = computed(() =>
  teachers.value.map((t) => ({
    id: t.id,
    name: t.name,
    position: t.position,
    subject: department.teacherDisciplineNames(t.id).join(", ") || "—",
  })),
);

const {
  searchQuery,
  filterValue,
  filteredItems: filteredTeachers,
} = useListControls(
  teachersForDisplay,
  ["name", "subject", "position"],
  (item, filter) => item.position === filter,
);

const { searchQuery: disciplineSearch, filteredItems: filteredDisciplines } =
  useListControls(disciplines, ["name", "description"]);

const positionOptions = [
  { label: "Всі посади", value: "Всі" },
  { label: "Професор", value: "Професор" },
  { label: "Доцент", value: "Доцент" },
  { label: "Асистент", value: "Асистент" },
];
</script>

<template>
  <div class="page-container page-wide">
    <h2><i class="pi pi-info-circle"></i> Про кафедру</h2>
    <p>Загальна інформація для незареєстрованих та всіх відвідувачів.</p>

    <section class="info-card">
      <h3>{{ info.name }}</h3>
      <p class="info-desc">{{ info.description }}</p>
      <div class="info-meta">
        <span
          ><i class="pi pi-user"></i> Завідувач:
          <strong>{{ info.head }}</strong></span
        >
        <span><i class="pi pi-envelope"></i> {{ info.email }}</span>
        <span><i class="pi pi-phone"></i> {{ info.phone }}</span>
      </div>
    </section>

    <section class="section-block">
      <h3><i class="pi pi-users"></i> Викладачі кафедри</h3>
      <div class="toolbar flex gap-3 items-center">
        <InputText
          v-model="searchQuery"
          placeholder="Пошук за ПІБ або дисципліною..."
          class="flex-1"
        />
        <Select
          v-model="filterValue"
          :options="positionOptions"
          optionLabel="label"
          optionValue="value"
          class="w-64"
        />
      </div>

      <DataTable
        :value="filteredTeachers"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column field="name" header="ПІБ" sortable></Column>
        <Column field="position" header="Посада">
          <template #body="slotProps">
            <span class="badge">{{ slotProps.data.position }}</span>
          </template>
        </Column>
        <Column field="subject" header="Дисципліни"></Column>
        <template #empty>
          <div class="empty-message">Викладачів не знайдено.</div>
        </template>
      </DataTable>
    </section>

    <section class="section-block">
      <h3><i class="pi pi-book"></i> Дисципліни кафедри</h3>
      <div class="toolbar">
        <InputText
          v-model="disciplineSearch"
          placeholder="Пошук за назвою..."
          class="flex-1"
        />
      </div>

      <DataTable
        :value="filteredDisciplines"
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
    </section>
  </div>
</template>

<style scoped>
.page-wide {
  max-width: 1200px;
}
.info-card {
  background: linear-gradient(135deg, #eff6ff 0%, #f8fafc 100%);
  border: 1px solid #bfdbfe;
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 28px;
}
.info-card h3 {
  color: #1e40af;
  margin-bottom: 10px;
}
.info-desc {
  color: #475569;
  line-height: 1.6;
  margin-bottom: 14px;
}
.info-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 0.95rem;
  color: #334155;
}
.info-meta i {
  color: #3b82f6;
  margin-right: 4px;
}
.section-block {
  margin-bottom: 32px;
}
.section-block h3 {
  color: #1e293b;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.empty-row {
  text-align: center;
  color: #94a3b8;
}
</style>
