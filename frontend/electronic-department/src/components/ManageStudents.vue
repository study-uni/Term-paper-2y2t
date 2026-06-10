<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Button from "primevue/button";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { students, groups } = storeToRefs(department);

const newStudent = ref({ name: "", groupId: groups.value[0]?.id ?? null });
const editDialogVisible = ref(false);
const editForm = ref({ id: null, name: "", groupId: null });

const openEdit = (item) => {
  editForm.value = { ...item };
  editDialogVisible.value = true;
};

const saveEdit = async () => {
  try {
    await department.updateStudent(editForm.value.id, {
      name: editForm.value.name,
      groupId: editForm.value.groupId,
    });
    editDialogVisible.value = false;
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};

const addStudent = async () => {
  const gId = newStudent.value.groupId || groups.value[0]?.id;
  if (!newStudent.value.name.trim() || !gId) return;
  try {
    await department.addStudent(newStudent.value.name.trim(), gId);
    newStudent.value.name = "";
  } catch (e) {
    console.error("Failed to add student:", e);
  }
};
</script>

<template>
  <div>
    <form
      @submit.prevent="addStudent"
      class="flex gap-2 items-center mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg shadow-sm"
    >
      <InputText
        v-model="newStudent.name"
        placeholder="ПІБ студента"
        class="flex-1"
        required
      />
      <Select
        v-model="newStudent.groupId"
        :options="groups"
        optionLabel="name"
        optionValue="id"
        placeholder="Оберіть групу"
        class="w-64"
        required
      />
      <Button
        type="submit"
        label="Додати студента"
        icon="pi pi-plus"
        severity="success"
      />
    </form>

    <DataTable
      :value="students"
      class="p-datatable-sm"
      responsiveLayout="scroll"
    >
      <Column field="name" header="ПІБ" />
      <Column header="Група">
        <template #body="slotProps">
          {{ department.groupById(slotProps.data.groupId)?.name }}
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
              @click="openEdit(slotProps.data)"
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              size="small"
              rounded
              @click="department.removeStudent(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <Dialog
      v-model:visible="editDialogVisible"
      header="Редагувати студента"
      modal
      :style="{ width: '32rem' }"
    >
      <div class="flex flex-col gap-3 pt-2">
        <label class="font-medium text-slate-700 text-sm">ПІБ</label>
        <InputText v-model="editForm.name" class="w-full" autofocus />
        <label class="font-medium text-slate-700 text-sm">Група</label>
        <Select
          v-model="editForm.groupId"
          :options="groups"
          optionLabel="name"
          optionValue="id"
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
