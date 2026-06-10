<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Checkbox from "primevue/checkbox";
import Button from "primevue/button";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { teachers, disciplines } = storeToRefs(department);

const positionOptions = ["Професор", "Доцент", "Асистент"];

const newTeacher = ref({ name: "", position: "Асистент", disciplineIds: [] });
const editDialogVisible = ref(false);
const editForm = ref({
  id: null,
  name: "",
  position: "Асистент",
  disciplineIds: [],
});

const openEdit = (item) => {
  editForm.value = {
    ...item,
    disciplineIds: [...item.disciplineIds],
  };
  editDialogVisible.value = true;
};

const saveEdit = async () => {
  try {
    await department.updateTeacher(editForm.value.id, {
      name: editForm.value.name,
      position: editForm.value.position,
      disciplineIds: [...editForm.value.disciplineIds],
    });
    editDialogVisible.value = false;
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};

const addTeacher = async () => {
  if (!newTeacher.value.name.trim()) return;
  try {
    await department.addTeacher(
      newTeacher.value.name.trim(),
      newTeacher.value.position,
      [...newTeacher.value.disciplineIds],
    );
    newTeacher.value = { name: "", position: "Асистент", disciplineIds: [] };
  } catch (e) {
    console.error("Failed to add teacher:", e);
  }
};

const toggleDiscipline = (ids, disciplineId, checked) => {
  const idx = ids.indexOf(disciplineId);
  if (checked && idx < 0) ids.push(disciplineId);
  if (!checked && idx >= 0) ids.splice(idx, 1);
};
</script>

<template>
  <div>
    <form
      @submit.prevent="addTeacher"
      class="flex flex-col gap-3 mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg shadow-sm"
    >
      <div class="flex gap-3 w-full">
        <InputText
          v-model="newTeacher.name"
          placeholder="ПІБ викладача"
          class="flex-1"
          required
        />
        <Select
          v-model="newTeacher.position"
          :options="positionOptions"
          placeholder="Посада"
          class="w-64"
          required
        />
      </div>
      <div class="flex flex-col gap-2">
        <span class="text-sm font-medium text-slate-600">Дисципліни:</span>
        <div class="flex flex-wrap gap-4">
          <div
            v-for="d in disciplines"
            :key="d.id"
            class="flex items-center gap-2"
          >
            <Checkbox
              :inputId="'new-disc-' + d.id"
              :modelValue="newTeacher.disciplineIds.includes(d.id)"
              binary
              @update:modelValue="
                (checked) =>
                  toggleDiscipline(newTeacher.disciplineIds, d.id, checked)
              "
            />
            <label
              :for="'new-disc-' + d.id"
              class="text-sm cursor-pointer select-none"
            >
              {{ d.name }}
            </label>
          </div>
        </div>
      </div>
      <Button
        type="submit"
        label="Додати викладача"
        icon="pi pi-plus"
        severity="success"
        class="self-start"
      />
    </form>

    <DataTable
      :value="teachers"
      class="p-datatable-sm"
      responsiveLayout="scroll"
    >
      <Column field="name" header="ПІБ" />
      <Column field="position" header="Посада" />
      <Column header="Дисципліни">
        <template #body="slotProps">
          {{
            department.teacherDisciplineNames(slotProps.data.id).join(", ") ||
            "—"
          }}
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
              @click="
                openEdit({
                  ...slotProps.data,
                  disciplineIds: [...slotProps.data.disciplineIds],
                })
              "
            />
            <Button
              icon="pi pi-trash"
              severity="danger"
              size="small"
              rounded
              @click="department.removeTeacher(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <Dialog
      v-model:visible="editDialogVisible"
      header="Редагувати викладача"
      modal
      :style="{ width: '36rem' }"
    >
      <div class="flex flex-col gap-3 pt-2">
        <label class="font-medium text-slate-700 text-sm">ПІБ</label>
        <InputText v-model="editForm.name" class="w-full" autofocus />
        <label class="font-medium text-slate-700 text-sm">Посада</label>
        <Select
          v-model="editForm.position"
          :options="positionOptions"
          class="w-full"
        />
        <span class="text-sm font-medium text-slate-600">Дисципліни</span>
        <div class="flex flex-wrap gap-3">
          <div
            v-for="d in disciplines"
            :key="d.id"
            class="flex items-center gap-2"
          >
            <Checkbox
              :inputId="'edit-disc-' + d.id"
              :modelValue="editForm.disciplineIds.includes(d.id)"
              binary
              @update:modelValue="
                (checked) =>
                  toggleDiscipline(editForm.disciplineIds, d.id, checked)
              "
            />
            <label
              :for="'edit-disc-' + d.id"
              class="text-sm cursor-pointer select-none"
            >
              {{ d.name }}
            </label>
          </div>
        </div>
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
