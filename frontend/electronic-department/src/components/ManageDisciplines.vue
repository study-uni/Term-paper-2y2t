<script setup>
import { ref } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../stores/department";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Button from "primevue/button";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import Dialog from "primevue/dialog";

const department = useDepartmentStore();
const { disciplines } = storeToRefs(department);

const newDiscipline = ref({ name: "", description: "" });
const disciplineError = ref("");

const isEditDialogVisible = ref(false);
const editForm = ref({ id: null, name: "", description: "" });

const addDiscipline = async () => {
  disciplineError.value = "";
  const name = newDiscipline.value.name.trim();
  if (!name) return;
  try {
    await department.addDiscipline(
      name,
      newDiscipline.value.description.trim(),
    );
    newDiscipline.value = { name: "", description: "" };
  } catch (e) {
    console.error("Failed to add discipline:", e);
    disciplineError.value =
      e.response?.data?.detail ?? "Не вдалося додати дисципліну";
  }
};

const openEditDialog = (discipline) => {
  editForm.value = { ...discipline };
  isEditDialogVisible.value = true;
};

const closeEditDialog = () => {
  isEditDialogVisible.value = false;
  editForm.value = { id: null, name: "", description: "" };
};

const saveEdit = async () => {
  const { id, name, description } = editForm.value;
  if (!name.trim()) return;
  try {
    await department.updateDiscipline(id, {
      name: name.trim(),
      description: description.trim(),
    });
    closeEditDialog();
  } catch (e) {
    console.error("Failed to save edit:", e);
  }
};
</script>

<template>
  <div class="space-y-6">
    <div v-if="disciplineError" class="error-message">
      {{ disciplineError }}
    </div>

    <!-- Add Discipline Form -->
    <form
      @submit.prevent="addDiscipline"
      class="flex flex-col md:flex-row gap-3 items-stretch md:items-center mb-6 p-5 bg-white border border-slate-200 rounded-2xl shadow-sm"
    >
      <InputText
        v-model="newDiscipline.name"
        placeholder="Назва дисципліни"
        class="flex-1 rounded-xl"
        required
      />
      <InputText
        v-model="newDiscipline.description"
        placeholder="Короткий опис"
        class="flex-1 rounded-xl"
      />
      <Button
        type="submit"
        label="Додати дисципліну"
        icon="pi pi-plus"
        severity="success"
        class="rounded-xl px-5"
      />
    </form>

    <!-- Disciplines Table -->
    <DataTable
      :value="disciplines"
      class="p-datatable-sm"
      responsiveLayout="scroll"
      :rows="10"
      paginator
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
      currentPageReportTemplate="Показано від {first} до {last} з {totalRecords} дисциплін"
    >
      <Column header="Назва" sortable field="name">
        <template #body="slotProps">
          <span class="font-semibold text-slate-800">{{
            slotProps.data.name
          }}</span>
        </template>
      </Column>
      <Column header="Опис" field="description">
        <template #body="slotProps">
          <span class="text-slate-600 text-sm">{{
            slotProps.data.description || "—"
          }}</span>
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
              @click="department.removeDiscipline(slotProps.data.id)"
            />
          </div>
        </template>
      </Column>
    </DataTable>

    <!-- Edit Dialog -->
    <Dialog
      v-model:visible="isEditDialogVisible"
      modal
      header="Редагувати дисципліну"
      class="w-full max-w-md"
      :style="{ width: '90vw' }"
      :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
    >
      <div class="flex flex-col gap-4 py-3">
        <div class="flex flex-col gap-2">
          <label for="disc-name" class="font-semibold text-slate-700 text-sm"
            >Назва дисципліни</label
          >
          <InputText
            id="disc-name"
            v-model="editForm.name"
            class="w-full rounded-xl"
            required
          />
        </div>
        <div class="flex flex-col gap-2">
          <label for="disc-desc" class="font-semibold text-slate-700 text-sm"
            >Опис</label
          >
          <Textarea
            id="disc-desc"
            v-model="editForm.description"
            rows="3"
            autoResize
            class="w-full rounded-xl"
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
