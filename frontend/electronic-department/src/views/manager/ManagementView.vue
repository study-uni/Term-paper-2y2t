<script setup>
import { ref, computed } from "vue";
import { storeToRefs } from "pinia";
import { useDepartmentStore } from "../../stores/department";
import { useAuthStore } from "../../stores/auth";
import DataTable from "primevue/datatable";
import Column from "primevue/column";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Button from "primevue/button";
import Textarea from "primevue/textarea";

const department = useDepartmentStore();
const auth = useAuthStore();
const { teachers, students, groups, disciplines } = storeToRefs(department);

const activeTab = ref("groups");
const editingId = ref(null);
const editForm = ref({});

const newGroupName = ref("");
const newStudent = ref({ name: "", groupId: null });
const newTeacher = ref({ name: "", position: "Асистент", disciplineIds: [] });
const newDiscipline = ref({ name: "", description: "" });

// Initialize groupId when groups load
if (groups.value.length > 0) {
  newStudent.value.groupId = groups.value[0].id;
}

const canEditDepartmentInfo = computed(() => auth.role === "admin");

const startEdit = (type, item) => {
  editingId.value = `${type}-${item.id}`;
  editForm.value = { ...item };
};

const cancelEdit = () => {
  editingId.value = null;
  editForm.value = {};
};

const saveEdit = (type) => {
  const id = editForm.value.id;
  if (type === "group") department.updateGroup(id, editForm.value.name);
  if (type === "student")
    department.updateStudent(id, {
      name: editForm.value.name,
      groupId: editForm.value.groupId,
    });
  if (type === "teacher") {
    department.updateTeacher(id, {
      name: editForm.value.name,
      position: editForm.value.position,
      disciplineIds: [...editForm.value.disciplineIds],
    });
  }
  if (type === "discipline") {
    department.updateDiscipline(id, {
      name: editForm.value.name,
      description: editForm.value.description,
    });
  }
  cancelEdit();
};

const addGroup = () => {
  if (!newGroupName.value.trim()) return;
  department.addGroup(newGroupName.value.trim());
  newGroupName.value = "";
};

const addStudent = () => {
  const gId = newStudent.value.groupId || groups.value[0]?.id;
  if (!newStudent.value.name.trim() || !gId) return;
  department.addStudent(newStudent.value.name.trim(), gId);
  newStudent.value.name = "";
};

const addTeacher = () => {
  if (!newTeacher.value.name.trim()) return;
  department.addTeacher(
    newTeacher.value.name.trim(),
    newTeacher.value.position,
    [...newTeacher.value.disciplineIds],
  );
  newTeacher.value = { name: "", position: "Асистент", disciplineIds: [] };
};

const addDiscipline = () => {
  if (!newDiscipline.value.name.trim()) return;
  department.addDiscipline(
    newDiscipline.value.name.trim(),
    newDiscipline.value.description,
  );
  newDiscipline.value = { name: "", description: "" };
};

const toggleDisciplineForTeacher = (disciplineId) => {
  const ids = newTeacher.value.disciplineIds;
  const idx = ids.indexOf(disciplineId);
  if (idx >= 0) ids.splice(idx, 1);
  else ids.push(disciplineId);
};

const toggleEditDiscipline = (disciplineId) => {
  const ids = editForm.value.disciplineIds;
  const idx = ids.indexOf(disciplineId);
  if (idx >= 0) ids.splice(idx, 1);
  else ids.push(disciplineId);
};

const isEditing = (type, id) => editingId.value === `${type}-${id}`;

const tabs = [
  { id: "groups", label: "Групи" },
  { id: "students", label: "Студенти" },
  { id: "teachers", label: "Викладачі" },
  { id: "disciplines", label: "Дисципліни" },
];
</script>

<template>
  <div class="page-container page-wide">
    <h2><i class="pi pi-sliders-h"></i> Підсистема управління</h2>
    <p v-if="auth.role === 'admin'">
      Адміністратор: повний доступ до структури кафедри та довідників.
    </p>
    <p v-else>
      Менеджер: додавання та редагування викладачів, студентів, груп і
      дисциплін.
    </p>

    <div v-if="canEditDepartmentInfo" class="admin-info">
      <h4>Інформація про кафедру (тільки адміністратор)</h4>
      <div class="flex flex-col gap-2 mt-2">
        <label class="font-medium text-amber-900 text-sm">Назва кафедри</label>
        <InputText
          v-model="department.info.name"
          @change="department.persist()"
          class="w-full"
        />

        <label class="font-medium text-amber-900 text-sm mt-2"
          >Опис кафедри</label
        >
        <Textarea
          v-model="department.info.description"
          rows="3"
          autoResize
          @change="department.persist()"
          class="w-full"
        />
      </div>
    </div>

    <div class="tabs flex gap-2 my-4">
      <Button
        v-for="tab in tabs"
        :key="tab.id"
        :severity="activeTab === tab.id ? 'success' : 'secondary'"
        :label="tab.label"
        @click="activeTab = tab.id"
      />
    </div>

    <section v-if="activeTab === 'groups'">
      <form
        @submit.prevent="addGroup"
        class="flex gap-2 items-center mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg"
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

      <DataTable
        :value="groups"
        class="p-datatable-sm"
        responsiveLayout="scroll"
      >
        <Column header="Група">
          <template #body="slotProps">
            <InputText
              v-if="isEditing('group', slotProps.data.id)"
              v-model="editForm.name"
              class="w-full"
            />
            <span v-else>{{ slotProps.data.name }}</span>
          </template>
        </Column>
        <Column header="Дії" style="width: 8rem; text-align: right">
          <template #body="slotProps">
            <div class="flex gap-2 justify-end">
              <template v-if="isEditing('group', slotProps.data.id)">
                <Button
                  icon="pi pi-check"
                  severity="success"
                  size="small"
                  rounded
                  @click="saveEdit('group')"
                />
                <Button
                  icon="pi pi-times"
                  severity="secondary"
                  size="small"
                  rounded
                  @click="cancelEdit"
                />
              </template>
              <template v-else>
                <Button
                  icon="pi pi-pencil"
                  severity="info"
                  size="small"
                  rounded
                  @click="startEdit('group', slotProps.data)"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  size="small"
                  rounded
                  @click="department.removeGroup(slotProps.data.id)"
                />
              </template>
            </div>
          </template>
        </Column>
      </DataTable>
    </section>

    <section v-if="activeTab === 'students'">
      <form
        @submit.prevent="addStudent"
        class="flex gap-2 items-center mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg"
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
        <Column header="ПІБ">
          <template #body="slotProps">
            <InputText
              v-if="isEditing('student', slotProps.data.id)"
              v-model="editForm.name"
              class="w-full"
            />
            <span v-else>{{ slotProps.data.name }}</span>
          </template>
        </Column>
        <Column header="Група">
          <template #body="slotProps">
            <Select
              v-if="isEditing('student', slotProps.data.id)"
              v-model="editForm.groupId"
              :options="groups"
              optionLabel="name"
              optionValue="id"
              class="w-full"
            />
            <span v-else>{{
              department.groupById(slotProps.data.groupId)?.name
            }}</span>
          </template>
        </Column>
        <Column header="Дії" style="width: 8rem; text-align: right">
          <template #body="slotProps">
            <div class="flex gap-2 justify-end">
              <template v-if="isEditing('student', slotProps.data.id)">
                <Button
                  icon="pi pi-check"
                  severity="success"
                  size="small"
                  rounded
                  @click="saveEdit('student')"
                />
                <Button
                  icon="pi pi-times"
                  severity="secondary"
                  size="small"
                  rounded
                  @click="cancelEdit"
                />
              </template>
              <template v-else>
                <Button
                  icon="pi pi-pencil"
                  severity="info"
                  size="small"
                  rounded
                  @click="startEdit('student', slotProps.data)"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  size="small"
                  rounded
                  @click="department.removeStudent(slotProps.data.id)"
                />
              </template>
            </div>
          </template>
        </Column>
      </DataTable>
    </section>

    <section v-if="activeTab === 'teachers'">
      <form
        @submit.prevent="addTeacher"
        class="flex flex-col gap-3 mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg"
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
            :options="['Професор', 'Доцент', 'Асистент']"
            placeholder="Посада"
            class="w-64"
            required
          />
        </div>
        <div class="flex flex-col gap-1">
          <span class="text-sm font-medium text-slate-600">Дисципліни:</span>
          <div class="flex flex-wrap gap-4">
            <label
              v-for="d in disciplines"
              :key="d.id"
              class="flex items-center gap-1 text-sm cursor-pointer select-none"
            >
              <input
                type="checkbox"
                :checked="newTeacher.disciplineIds.includes(d.id)"
                @change="toggleDisciplineForTeacher(d.id)"
              />
              {{ d.name }}
            </label>
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
        <Column header="ПІБ">
          <template #body="slotProps">
            <InputText
              v-if="isEditing('teacher', slotProps.data.id)"
              v-model="editForm.name"
              class="w-full"
            />
            <span v-else>{{ slotProps.data.name }}</span>
          </template>
        </Column>
        <Column header="Посада">
          <template #body="slotProps">
            <Select
              v-if="isEditing('teacher', slotProps.data.id)"
              v-model="editForm.position"
              :options="['Професор', 'Доцент', 'Асистент']"
              class="w-full"
            />
            <span v-else>{{ slotProps.data.position }}</span>
          </template>
        </Column>
        <Column header="Дисципліни">
          <template #body="slotProps">
            <div
              v-if="isEditing('teacher', slotProps.data.id)"
              class="flex flex-wrap gap-2"
            >
              <label
                v-for="d in disciplines"
                :key="d.id"
                class="flex items-center gap-1 text-xs cursor-pointer select-none"
              >
                <input
                  type="checkbox"
                  :checked="editForm.disciplineIds.includes(d.id)"
                  @change="toggleEditDiscipline(d.id)"
                />
                {{ d.name }}
              </label>
            </div>
            <span v-else>{{
              department.teacherDisciplineNames(slotProps.data.id).join(", ") ||
              "—"
            }}</span>
          </template>
        </Column>
        <Column header="Дії" style="width: 8rem; text-align: right">
          <template #body="slotProps">
            <div class="flex gap-2 justify-end">
              <template v-if="isEditing('teacher', slotProps.data.id)">
                <Button
                  icon="pi pi-check"
                  severity="success"
                  size="small"
                  rounded
                  @click="saveEdit('teacher')"
                />
                <Button
                  icon="pi pi-times"
                  severity="secondary"
                  size="small"
                  rounded
                  @click="cancelEdit"
                />
              </template>
              <template v-else>
                <Button
                  icon="pi pi-pencil"
                  severity="info"
                  size="small"
                  rounded
                  @click="
                    startEdit('teacher', {
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
              </template>
            </div>
          </template>
        </Column>
      </DataTable>
    </section>

    <section v-if="activeTab === 'disciplines'">
      <form
        @submit.prevent="addDiscipline"
        class="flex gap-2 items-center mb-4 p-4 bg-slate-50 border border-slate-200 rounded-lg"
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
        <Column header="Назва">
          <template #body="slotProps">
            <InputText
              v-if="isEditing('discipline', slotProps.data.id)"
              v-model="editForm.name"
              class="w-full"
            />
            <span v-else>{{ slotProps.data.name }}</span>
          </template>
        </Column>
        <Column header="Опис">
          <template #body="slotProps">
            <InputText
              v-if="isEditing('discipline', slotProps.data.id)"
              v-model="editForm.description"
              class="w-full"
            />
            <span v-else>{{ slotProps.data.description }}</span>
          </template>
        </Column>
        <Column header="Дії" style="width: 8rem; text-align: right">
          <template #body="slotProps">
            <div class="flex gap-2 justify-end">
              <template v-if="isEditing('discipline', slotProps.data.id)">
                <Button
                  icon="pi pi-check"
                  severity="success"
                  size="small"
                  rounded
                  @click="saveEdit('discipline')"
                />
                <Button
                  icon="pi pi-times"
                  severity="secondary"
                  size="small"
                  rounded
                  @click="cancelEdit"
                />
              </template>
              <template v-else>
                <Button
                  icon="pi pi-pencil"
                  severity="info"
                  size="small"
                  rounded
                  @click="startEdit('discipline', slotProps.data)"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  size="small"
                  rounded
                  @click="department.removeDiscipline(slotProps.data.id)"
                />
              </template>
            </div>
          </template>
        </Column>
      </DataTable>
    </section>
  </div>
</template>

<style scoped>
.page-wide {
  max-width: 1100px;
}
.admin-info {
  background: #fef3c7;
  border: 1px solid #fcd34d;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}
.admin-info h4 {
  color: #92400e;
  margin-bottom: 8px;
}
</style>
