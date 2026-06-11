<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { groups } = storeToRefs(department);

const newGroupName = ref("");
const groupError = ref("");

const isEditDialogVisible = ref(false);
const editForm = ref({ id: null, name: "" });

const addGroup = async () => {
  groupError.value = "";
  const name = newGroupName.value.trim();
  if (!name) return;
  try {
    await department.addGroup(name);
    newGroupName.value = "";
  } catch (e) {
    console.error("Failed to add group:", e);
    groupError.value = e.response?.data?.detail ?? "Не вдалося додати групу";
  }
};

const openEditDialog = (group) => {
  editForm.value = { ...group };
  isEditDialogVisible.value = true;
};

const closeEditDialog = () => {
  isEditDialogVisible.value = false;
  editForm.value = { id: null, name: "" };
};

const saveEdit = async () => {
  const { id, name } = editForm.value;
  if (!name.trim()) return;
  try {
    await department.updateGroup(id, name.trim());
    closeEditDialog();
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};
</script>

<template>
  <div class="space-y-6">
    <div v-if="groupError" class="error-message">
      {{ groupError }}
    </div>

    <!-- Add Group Form -->
    <form
      @submit.prevent="addGroup"
      class="flex flex-col sm:flex-row gap-3 items-stretch sm:items-center mb-6 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm"
    >
      <InputText
        v-model="newGroupName"
        placeholder="Назва групи (напр. Б-121-24-5)"
        class="flex-1 rounded-xl"
        required
      />
      <Button
        type="submit"
        label="Додати групу"
        icon="pi pi-plus"
        severity="success"
        class="rounded-xl px-5"
      />
    </form>

    <!-- Groups Table -->
    <DataTable
      :value="groups"
      class="p-datatable-sm"
      responsiveLayout="scroll"
      :rows="10"
      paginator
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="Показано від {first} до {last} з {totalRecords} груп"
    >
      <Column header="Група" sortable field="name">
        <template #body="slotProps">
          <span class="font-medium text-slate-800">{{ slotProps.data.name }}</span>
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
              @click="department.removeGroup(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="isEditDialogVisible"
      modal
      header="Редагувати групу"
      class="w-full max-w-md"
      :style="{ width: '90vw' }"
      :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
    >
      <div class="flex flex-col gap-4 py-3">
        <div class="flex flex-col gap-2">
          <label for="group-name" class="font-semibold text-slate-700 text-sm">Назва групи</label>
          <InputText
            id="group-name"
            v-model="editForm.name"
            class="w-full rounded-xl"
            required
            @keyup.enter="saveEdit"
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
