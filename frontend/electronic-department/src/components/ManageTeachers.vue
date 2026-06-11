<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Checkbox from "primevue/checkbox";
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { teachers, disciplines } = storeToRefs(department);

const newTeacher = ref({ name: "", position: "Асистент", disciplineIds: [] });
const teacherError = ref("");

const isEditDialogVisible = ref(false);
const editForm = ref({ id: null, name: "", position: "Асистент", disciplineIds: [] });

const addTeacher = async () => {
  teacherError.value = "";
  const name = newTeacher.value.name.trim();
  if (!name) return;
  try {
    await department.addTeacher(
      name,
      newTeacher.value.position,
      [...newTeacher.value.disciplineIds],
    );
    newTeacher.value = { name: "", position: "Асистент", disciplineIds: [] };
  } catch (e) {
    console.error("Failed to add teacher:", e);
    teacherError.value = e.response?.data?.detail ?? "Не вдалося додати викладача";
  }
};

const openEditDialog = (teacher) => {
  editForm.value = {
    id: teacher.id,
    name: teacher.name,
    position: teacher.position,
    disciplineIds: [...(teacher.disciplineIds ?? teacher.discipline_ids ?? [])],
  };
  isEditDialogVisible.value = true;
};

const closeEditDialog = () => {
  isEditDialogVisible.value = false;
  editForm.value = { id: null, name: "", position: "Асистент", disciplineIds: [] };
};

const saveEdit = async () => {
  const { id, name, position, disciplineIds } = editForm.value;
  if (!name.trim()) return;
  try {
    await department.updateTeacher(id, {
      name: name.trim(),
      position,
      disciplineIds: [...disciplineIds],
    });
    closeEditDialog();
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};
</script>

<template>
  <div class="space-y-6">
    <div v-if="teacherError" class="error-message">
      {{ teacherError }}
    </div>

    <!-- Add Teacher Form -->
    <form
      @submit.prevent="addTeacher"
      class="flex flex-col gap-4 mb-6 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm"
    >
      <div class="flex flex-col md:flex-row gap-3 w-full items-stretch md:items-center">
        <InputText
          v-model="newTeacher.name"
          placeholder="ПІБ викладача"
          class="flex-1 rounded-xl"
          required
        />
        <Select
          v-model="newTeacher.position"
          :options="['Професор', 'Доцент', 'Асистент']"
          placeholder="Посада"
          class="w-full md:w-64 rounded-xl"
          required
        />
      </div>

      <div class="flex flex-col gap-2 bg-slate-50 p-4 rounded-xl border border-slate-100">
        <span class="text-sm font-semibold text-slate-600">Дисципліни:</span>
        <div class="flex flex-wrap gap-x-6 gap-y-3">
          <div
            v-for="d in disciplines"
            :key="d.id"
            class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none"
          >
            <Checkbox
              v-model="newTeacher.disciplineIds"
              :value="d.id"
              :inputId="'new-t-disc-' + d.id"
            />
            <label :for="'new-t-disc-' + d.id" class="cursor-pointer font-medium">{{ d.name }}</label>
          </div>
          <div v-if="disciplines.length === 0" class="text-xs text-slate-400">
            Немає створених дисциплін
          </div>
        </div>
      </div>

      <Button
        type="submit"
        label="Додати викладача"
        icon="pi pi-plus"
        severity="success"
        class="self-start rounded-xl px-5"
      />
    </form>

    <!-- Teachers Table -->
    <DataTable
      :value="teachers"
      class="p-datatable-sm"
      responsiveLayout="scroll"
      :rows="10"
      paginator
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="Показано від {first} до {last} з {totalRecords} викладачів"
    >
      <Column header="ПІБ" sortable field="name">
        <template #body="slotProps">
          <span class="font-medium text-slate-800">{{ slotProps.data.name }}</span>
        </template>
      </Column>
      <Column header="Посада" sortable field="position">
        <template #body="slotProps">
          <span class="badge font-semibold bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full border border-emerald-100">
            {{ slotProps.data.position }}
          </span>
        </template>
      </Column>
      <Column header="Дисципліни">
        <template #body="slotProps">
          <span class="text-slate-600 text-sm">
            {{ department.teacherDisciplineNames(slotProps.data.id).join(", ") || "—" }}
          </span>
        </template>
      </Column>
      <Column header="Дії" style="width: 8rem; text-align: right">
        <template #body="slotProps">
          <div class="flex gap-2 justify-end">
            <Button
              icon="pi pi-pencil"
              severity="info"
              size="small"
              rounded
              outlined
              title="Редагувати"
              @click="openEditDialog(slotProps.data)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              size="small"
              rounded
              outlined
              title="Видалити"
              @click="department.removeTeacher(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="isEditDialogVisible"
      modal
      header="Редагувати викладача"
      class="w-full max-w-lg"
      :style="{ width: '90vw' }"
      :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
    >
      <div class="flex flex-col gap-4 py-3">
        <div class="flex flex-col gap-2">
          <label for="teacher-name" class="font-semibold text-slate-700 text-sm">ПІБ викладача</label>
          <InputText
            id="teacher-name"
            v-model="editForm.name"
            class="w-full rounded-xl"
            required
          />
        </div>
        <div class="flex flex-col gap-2">
          <label for="teacher-position" class="font-semibold text-slate-700 text-sm">Посада</label>
          <Select
            id="teacher-position"
            v-model="editForm.position"
            :options="['Професор', 'Доцент', 'Асистент']"
            class="w-full rounded-xl"
            required
          />
        </div>
        <div class="flex flex-col gap-2 bg-slate-50 p-4 rounded-xl border border-slate-100 mt-2">
          <span class="text-sm font-semibold text-slate-700">Дисципліни викладача:</span>
          <div class="flex flex-wrap gap-x-6 gap-y-3 mt-1">
            <div
              v-for="d in disciplines"
              :key="d.id"
              class="flex items-center gap-2 text-sm text-slate-700 cursor-pointer select-none"
            >
              <Checkbox
                v-model="editForm.disciplineIds"
                :value="d.id"
                :inputId="'edit-t-disc-' + d.id"
              />
              <label :for="'edit-t-disc-' + d.id" class="cursor-pointer font-medium">{{ d.name }}</label>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button
          label="Скасувати"
          icon="pi pi-times"
          severity="secondary"
          text
          class="rounded-xl"
          @click="closeEditDialog"
        />
        <Button
          label="Зберегти"
          icon="pi pi-check"
          severity="success"
          class="rounded-xl px-4"
          @click="saveEdit"
        />
      </template>
    </Dialog>
  </div>
</template>
