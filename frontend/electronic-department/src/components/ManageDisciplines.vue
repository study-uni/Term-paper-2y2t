<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Button from "primevue/button";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { disciplines } = storeToRefs(department);

const newDiscipline = ref({ name: "", description: "" });
const editDialogVisible = ref(false);
const editForm = ref({ id: null, name: "", description: "" });

const openEdit = (item) => {
  editForm.value = { ...item };
  editDialogVisible.value = true;
};

const saveEdit = async () => {
  try {
    await department.updateDiscipline(editForm.value.id, {
      name: editForm.value.name,
      description: editForm.value.description,
    });
    editDialogVisible.value = false;
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};

const addDiscipline = async () => {
  if (!newDiscipline.value.name.trim()) return;
  try {
    await department.addDiscipline(
      newDiscipline.value.name.trim(),
      newDiscipline.value.description,
    );
    newDiscipline.value = { name: "", description: "" };
  } catch (e) {
    console.error("Failed to add discipline:", e);
  }
};
</script>

<template>
  <div>
    <form
      @submit.prevent="addDiscipline"
      class="flex gap-2 items-center mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg shadow-sm"
    >
      <InputText
        v-model="newDiscipline.name"
        placeholder="Назва дисципліни"
        class="flex-1"
        required
      />
      <InputText
        v-model="newDiscipline.description"
        placeholder="Короткий опис"
        class="flex-1"
      />
      <Button
        type="submit"
        label="Додати дисципліну"
        icon="pi pi-plus"
        severity="success"
      />
    </form>

    <DataTable
      :value="disciplines"
      class="p-datatable-sm"
      responsiveLayout="scroll"
    >
      <Column field="name" header="Назва" />
      <Column field="description" header="Опис" />
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
              @click="department.removeDiscipline(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <Dialog
      v-model:visible="editDialogVisible"
      header="Редагувати дисципліну"
      modal
      :style="{ width: '32rem' }"
    >
      <div class="flex flex-col gap-3 pt-2">
        <label class="font-medium text-slate-700 text-sm">Назва</label>
        <InputText v-model="editForm.name" class="w-full" autofocus />
        <label class="font-medium text-slate-700 text-sm">Опис</label>
        <Textarea
          v-model="editForm.description"
          rows="3"
          autoResize
          class="w-full"
        />
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
