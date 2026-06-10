<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Button from "primevue/button";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { groups } = storeToRefs(department);

const newGroupName = ref("");
const editDialogVisible = ref(false);
const editForm = ref({ id: null, name: "" });

const openEdit = (item) => {
  editForm.value = { ...item };
  editDialogVisible.value = true;
};

const saveEdit = async () => {
  try {
    await department.updateGroup(editForm.value.id, editForm.value.name);
    editDialogVisible.value = false;
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};

const addGroup = async () => {
  if (!newGroupName.value.trim()) return;
  try {
    await department.addGroup(newGroupName.value.trim());
    newGroupName.value = "";
  } catch (e) {
    console.error("Failed to add group:", e);
  }
};
</script>

<template>
  <div>
    <form
      @submit.prevent="addGroup"
      class="flex gap-2 items-center mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg shadow-sm"
    >
      <InputText
        v-model="newGroupName"
        placeholder="Назва групи (напр. Б-121-24-5)"
        class="flex-1"
        required
      />
      <Button
        type="submit"
        label="Додати групу"
        icon="pi pi-plus"
        severity="success"
      />
    </form>

    <DataTable :value="groups" class="p-datatable-sm" responsiveLayout="scroll">
      <Column field="name" header="Група" />
      <Column header="Дії" style="width: 8rem; text-align: right">
        <template #body="slotProps">
          <div class="flex gap-2 justify-end">
            <Button
              icon="pi pi-pencil"
              severity="info"
              size="small"
              rounded
              @click="openEdit(slotProps.data)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              size="small"
              rounded
              @click="department.removeGroup(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <Dialog
      v-model:visible="editDialogVisible"
      header="Редагувати групу"
      modal
      :style="{ width: '28rem' }"
    >
      <div class="flex flex-col gap-3 pt-2">
        <label class="font-medium text-slate-700 text-sm">Назва групи</label>
        <InputText v-model="editForm.name" class="w-full" autofocus />
      </div>
      <template #footer>
        <Button
          label="Скасувати"
          severity="secondary"
          @click="editDialogVisible = false"
        />
        <Button label="Зберегти" icon="pi pi-check" @click="saveEdit" />
      </template>
    </Dialog>
  </div>
</template>
