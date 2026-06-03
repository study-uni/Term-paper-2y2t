<script setup>
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useDepartmentStore } from '../../stores/department';
import { useAuthStore } from '../../stores/auth';

const department = useDepartmentStore();
const auth = useAuthStore();
const { teachers, students, groups, disciplines } = storeToRefs(department);

const activeTab = ref('groups');
const editingId = ref(null);
const editForm = ref({});

const newGroupName = ref('');
const newStudent = ref({ name: '', groupId: groups.value[0]?.id ?? null });
const newTeacher = ref({ name: '', position: 'Асистент', disciplineIds: [] });
const newDiscipline = ref({ name: '', description: '' });

const canEditDepartmentInfo = computed(() => auth.role === 'admin');

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
  if (type === 'group') department.updateGroup(id, editForm.value.name);
  if (type === 'student') department.updateStudent(id, { name: editForm.value.name, groupId: editForm.value.groupId });
  if (type === 'teacher') {
    department.updateTeacher(id, {
      name: editForm.value.name,
      position: editForm.value.position,
      disciplineIds: [...editForm.value.disciplineIds],
    });
  }
  if (type === 'discipline') {
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
  newGroupName.value = '';
};

const addStudent = () => {
  if (!newStudent.value.name.trim() || !newStudent.value.groupId) return;
  department.addStudent(newStudent.value.name.trim(), newStudent.value.groupId);
  newStudent.value.name = '';
};

const addTeacher = () => {
  if (!newTeacher.value.name.trim()) return;
  department.addTeacher(newTeacher.value.name.trim(), newTeacher.value.position, [...newTeacher.value.disciplineIds]);
  newTeacher.value = { name: '', position: 'Асистент', disciplineIds: [] };
};

const addDiscipline = () => {
  if (!newDiscipline.value.name.trim()) return;
  department.addDiscipline(newDiscipline.value.name.trim(), newDiscipline.value.description);
  newDiscipline.value = { name: '', description: '' };
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
  { id: 'groups', label: 'Групи' },
  { id: 'students', label: 'Студенти' },
  { id: 'teachers', label: 'Викладачі' },
  { id: 'disciplines', label: 'Дисципліни' },
];
</script>

<template>
  <div class="page-container page-wide">
    <h2><i class="pi pi-sliders-h"></i> Підсистема управління</h2>
    <p v-if="auth.role === 'admin'">
      Адміністратор: повний доступ до структури кафедри та довідників.
    </p>
    <p v-else>Менеджер: додавання та редагування викладачів, студентів, груп і дисциплін.</p>

    <div v-if="canEditDepartmentInfo" class="admin-info">
      <h4>Інформація про кафедру (тільки адміністратор)</h4>
      <label>Назва <input v-model="department.info.name" class="custom-input" /></label>
      <label>Опис <textarea v-model="department.info.description" class="custom-input" rows="2"></textarea></label>
    </div>

    <div class="tabs">
      <button v-for="tab in tabs" :key="tab.id" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">
        {{ tab.label }}
      </button>
    </div>

    <section v-if="activeTab === 'groups'">
      <form @submit.prevent="addGroup" class="management-form">
        <input v-model="newGroupName" type="text" placeholder="Назва групи (напр. Б-121-24-5)" class="custom-input" required />
        <button type="submit" class="btn-add"><i class="pi pi-plus"></i> Додати групу</button>
      </form>
      <table class="custom-table">
        <thead><tr><th>Група</th><th>Дії</th></tr></thead>
        <tbody>
          <tr v-for="g in groups" :key="g.id">
            <td>
              <template v-if="isEditing('group', g.id)">
                <input v-model="editForm.name" class="inline-input" />
              </template>
              <template v-else>{{ g.name }}</template>
            </td>
            <td class="actions">
              <template v-if="isEditing('group', g.id)">
                <button @click="saveEdit('group')" class="btn-save"><i class="pi pi-check"></i></button>
                <button @click="cancelEdit" class="btn-cancel"><i class="pi pi-times"></i></button>
              </template>
              <template v-else>
                <button @click="startEdit('group', g)" class="btn-edit"><i class="pi pi-pencil"></i></button>
                <button @click="department.removeGroup(g.id)" class="btn-delete"><i class="pi pi-trash"></i></button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-if="activeTab === 'students'">
      <form @submit.prevent="addStudent" class="management-form">
        <input v-model="newStudent.name" type="text" placeholder="ПІБ студента" class="custom-input" required />
        <select v-model="newStudent.groupId" class="custom-select" required>
          <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
        <button type="submit" class="btn-add"><i class="pi pi-plus"></i> Додати студента</button>
      </form>
      <table class="custom-table">
        <thead><tr><th>ПІБ</th><th>Група</th><th>Дії</th></tr></thead>
        <tbody>
          <tr v-for="s in students" :key="s.id">
            <td>
              <input v-if="isEditing('student', s.id)" v-model="editForm.name" class="inline-input" />
              <template v-else>{{ s.name }}</template>
            </td>
            <td>
              <select v-if="isEditing('student', s.id)" v-model="editForm.groupId" class="custom-select">
                <option v-for="g in groups" :key="g.id" :value="g.id">{{ g.name }}</option>
              </select>
              <template v-else>{{ department.groupById(s.groupId)?.name }}</template>
            </td>
            <td class="actions">
              <template v-if="isEditing('student', s.id)">
                <button @click="saveEdit('student')" class="btn-save"><i class="pi pi-check"></i></button>
                <button @click="cancelEdit" class="btn-cancel"><i class="pi pi-times"></i></button>
              </template>
              <template v-else>
                <button @click="startEdit('student', s)" class="btn-edit"><i class="pi pi-pencil"></i></button>
                <button @click="department.removeStudent(s.id)" class="btn-delete"><i class="pi pi-trash"></i></button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-if="activeTab === 'teachers'">
      <form @submit.prevent="addTeacher" class="management-form management-form-wrap">
        <input v-model="newTeacher.name" type="text" placeholder="ПІБ викладача" class="custom-input" required />
        <select v-model="newTeacher.position" class="custom-select">
          <option>Професор</option>
          <option>Доцент</option>
          <option>Асистент</option>
        </select>
        <div class="discipline-checks">
          <label v-for="d in disciplines" :key="d.id" class="check-label">
            <input
              type="checkbox"
              :checked="newTeacher.disciplineIds.includes(d.id)"
              @change="toggleDisciplineForTeacher(d.id)"
            />
            {{ d.name }}
          </label>
        </div>
        <button type="submit" class="btn-add"><i class="pi pi-plus"></i> Додати викладача</button>
      </form>
      <table class="custom-table">
        <thead><tr><th>ПІБ</th><th>Посада</th><th>Дисципліни</th><th>Дії</th></tr></thead>
        <tbody>
          <tr v-for="t in teachers" :key="t.id">
            <td>
              <input v-if="isEditing('teacher', t.id)" v-model="editForm.name" class="inline-input" />
              <template v-else>{{ t.name }}</template>
            </td>
            <td>
              <select v-if="isEditing('teacher', t.id)" v-model="editForm.position" class="custom-select">
                <option>Професор</option>
                <option>Доцент</option>
                <option>Асистент</option>
              </select>
              <template v-else>{{ t.position }}</template>
            </td>
            <td>
              <div v-if="isEditing('teacher', t.id)" class="discipline-checks">
                <label v-for="d in disciplines" :key="d.id" class="check-label">
                  <input
                    type="checkbox"
                    :checked="editForm.disciplineIds.includes(d.id)"
                    @change="toggleEditDiscipline(d.id)"
                  />
                  {{ d.name }}
                </label>
              </div>
              <template v-else>{{ department.teacherDisciplineNames(t.id).join(', ') || '—' }}</template>
            </td>
            <td class="actions">
              <template v-if="isEditing('teacher', t.id)">
                <button @click="saveEdit('teacher')" class="btn-save"><i class="pi pi-check"></i></button>
                <button @click="cancelEdit" class="btn-cancel"><i class="pi pi-times"></i></button>
              </template>
              <template v-else>
                <button @click="startEdit('teacher', { ...t, disciplineIds: [...t.disciplineIds] })" class="btn-edit"><i class="pi pi-pencil"></i></button>
                <button @click="department.removeTeacher(t.id)" class="btn-delete"><i class="pi pi-trash"></i></button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <section v-if="activeTab === 'disciplines'">
      <form @submit.prevent="addDiscipline" class="management-form management-form-wrap">
        <input v-model="newDiscipline.name" type="text" placeholder="Назва дисципліни" class="custom-input" required />
        <input v-model="newDiscipline.description" type="text" placeholder="Короткий опис" class="custom-input" />
        <button type="submit" class="btn-add"><i class="pi pi-plus"></i> Додати дисципліну</button>
      </form>
      <table class="custom-table">
        <thead><tr><th>Назва</th><th>Опис</th><th>Дії</th></tr></thead>
        <tbody>
          <tr v-for="d in disciplines" :key="d.id">
            <td>
              <input v-if="isEditing('discipline', d.id)" v-model="editForm.name" class="inline-input" />
              <template v-else>{{ d.name }}</template>
            </td>
            <td>
              <input v-if="isEditing('discipline', d.id)" v-model="editForm.description" class="inline-input" />
              <template v-else>{{ d.description }}</template>
            </td>
            <td class="actions">
              <template v-if="isEditing('discipline', d.id)">
                <button @click="saveEdit('discipline')" class="btn-save"><i class="pi pi-check"></i></button>
                <button @click="cancelEdit" class="btn-cancel"><i class="pi pi-times"></i></button>
              </template>
              <template v-else>
                <button @click="startEdit('discipline', d)" class="btn-edit"><i class="pi pi-pencil"></i></button>
                <button @click="department.removeDiscipline(d.id)" class="btn-delete"><i class="pi pi-trash"></i></button>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
.page-wide { max-width: 1100px; }
.tabs { display: flex; gap: 8px; margin: 16px 0 20px; flex-wrap: wrap; }
.tabs button {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  border-radius: 6px;
  cursor: pointer;
}
.tabs button.active { background: #22c55e; color: white; border-color: #22c55e; }
.management-form { display: flex; gap: 10px; background: #f4f6f9; padding: 15px; border-radius: 8px; margin-bottom: 16px; }
.management-form-wrap { flex-wrap: wrap; align-items: flex-start; }
.discipline-checks { display: flex; flex-wrap: wrap; gap: 8px 16px; width: 100%; }
.check-label { font-size: 0.9rem; display: flex; align-items: center; gap: 4px; }
.btn-add { background: #22c55e; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; white-space: nowrap; }
.actions { white-space: nowrap; }
.btn-edit, .btn-save, .btn-cancel, .btn-delete { background: none; border: none; cursor: pointer; font-size: 1.1rem; padding: 4px 8px; }
.btn-edit { color: #3b82f6; }
.btn-save { color: #22c55e; }
.btn-cancel { color: #64748b; }
.btn-delete { color: #ef4444; }
.inline-input { width: 100%; padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px; }
.admin-info { background: #fef3c7; border: 1px solid #fcd34d; padding: 16px; border-radius: 8px; margin-bottom: 16px; display: flex; flex-direction: column; gap: 10px; }
.admin-info label { display: flex; flex-direction: column; gap: 4px; font-weight: 500; color: #92400e; }
</style>
