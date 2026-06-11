<script setup>
import { ref, watch, nextTick } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { students, groups } = storeToRefs(department);

const newStudent = ref({ name: "", groupId: null });
const studentError = ref("");

const isEditDialogVisible = ref(false);
const editForm = ref({ id: null, name: "", groupId: null });

watch(
  groups,
  async (newGroups) => {
    if (newGroups.length > 0 && newStudent.value.groupId === null) {
      await nextTick();
      newStudent.value.groupId = newGroups[0].id;
    }
  },
  { immediate: true },
);

const addStudent = async () => {
  studentError.value = "";
  const name = newStudent.value.name.trim();
  const gId = newStudent.value.groupId;
  if (!name) {
    studentError.value = "Будь ласка, введіть ПІБ студента";
    return;
  }
  if (!gId) {
    studentError.value = "Будь ласка, оберіть групу";
    return;
  }
  try {
    await department.addStudent(name, gId);
    newStudent.value.name = "";
  } catch (e) {
    console.error("Failed to add student:", e);
    studentError.value =
      e.response?.data?.detail ?? "Не вдалося додати студента";
  }
};

const openEditDialog = (student) => {
  editForm.value = {
    id: student.id,
    name: student.name,
    groupId: student.groupId ?? student.group_id,
  };
  isEditDialogVisible.value = true;
};

const closeEditDialog = () => {
  isEditDialogVisible.value = false;
  editForm.value = { id: null, name: "", groupId: null };
};

const saveEdit = async () => {
  const { id, name, groupId } = editForm.value;
  if (!name.trim() || !groupId) return;
  try {
    await department.updateStudent(id, {
      name: name.trim(),
      groupId: groupId,
    });
    closeEditDialog();
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};
</script>

<template>
  <div class="space-y-6">
    <div v-if="studentError" class="error-message">
      {{ studentError }}
    </div>

    <!-- Add Student Form -->
    <form
      @submit.prevent="addStudent"
      class="flex flex-col md:flex-row gap-3 items-stretch md:items-center mb-6 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm"
    >
      <InputText
        v-model="newStudent.name"
        placeholder="ПІБ студента"
        class="flex-1 rounded-xl"
        required
      />
      <Select
        v-model="newStudent.groupId"
        :options="groups"
        optionLabel="name"
        optionValue="id"
        placeholder="Оберіть групу"
        class="w-full md:w-64 rounded-xl"
        required
      />
      <Button
        type="submit"
        label="Додати студента"
        icon="pi pi-plus"
        severity="success"
        class="rounded-xl px-5"
      />
    </form>

    <!-- Students Table -->
    <DataTable
      :value="students"
      class="p-datatable-sm"
      responsiveLayout="scroll"
      :rows="10"
      paginator
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="Показано від {first} до {last} з {totalRecords} студентів"
    >
      <Column header="ПІБ" sortable field="name">
        <template #body="slotProps">
          <span class="font-medium text-slate-800">{{
            slotProps.data.name
          }}</span>
        </template>
      </Column>
      <Column header="Група" sortable field="groupName">
        <template #body="slotProps">
          <span
            class="badge font-semibold bg-blue-50 text-blue-700 px-3 py-1 rounded-full border border-blue-100"
          >
            {{
              slotProps.data.groupName ??
              department.groupById(slotProps.data.groupId)?.name ??
              "—"
            }}
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
              @click="department.removeStudent(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="isEditDialogVisible"
      modal
      header="Редагувати студента"
      class="w-full max-w-md"
      :style="{ width: '90vw' }"
      :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
    >
      <div class="flex flex-col gap-4 py-3">
        <div class="flex flex-col gap-2">
          <label for="student-name" class="font-semibold text-slate-700 text-sm"
            >ПІБ студента</label
          >
          <InputText
            id="student-name"
            v-model="editForm.name"
            class="w-full rounded-xl"
            required
          />
        </div>
        <div class="flex flex-col gap-2">
          <label
            for="student-group"
            class="font-semibold text-slate-700 text-sm"
            >Група</label
          >
          <Select
            id="student-group"
            v-model="editForm.groupId"
            :options="groups"
            optionLabel="name"
            optionValue="id"
            placeholder="Оберіть групу"
            class="w-full rounded-xl"
            required
          />
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
