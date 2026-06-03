import { defineStore } from 'pinia';

const gradeToEcts = (grade) => {
  if (grade >= 90) return 'A';
  if (grade >= 80) return 'B';
  if (grade >= 70) return 'C';
  if (grade >= 60) return 'D';
  if (grade >= 50) return 'E';
  return 'F';
};

const formatTeacherShortName = (teachers, teacherId) => {
  const t = teachers.find((x) => x.id === teacherId);
  if (!t) return '—';
  const parts = t.name.split(' ');
  if (parts.length < 2) return t.name;
  return `${parts[0]} ${parts[1][0]}.${parts[2] ? parts[2][0] + '.' : ''}`;
};

export const useDepartmentStore = defineStore('department', {
  state: () => ({
    info: {
      name: 'Кафедра програмної інженерії',
      description:
        'Кафедра здійснює підготовку бакалаврів та магістрів зі спеціальності «Програмна інженерія». Навчання включає сучасні технології веб-розробки, архітектури ПЗ та проєктування баз даних.',
      head: 'Прокопенко Андрій Васильович',
      email: 'software@university.edu.ua',
      phone: '+38 (044) 000-00-00',
    },
    disciplines: [
      { id: 1, name: 'Веб-програмування', description: 'HTML, CSS, JavaScript, Vue.js' },
      { id: 2, name: 'Архітектура ПЗ', description: 'Патерни проєктування, UML, SOLID' },
      { id: 3, name: 'Бази даних', description: 'SQL, нормалізація, ORM' },
    ],
    teachers: [
      {
        id: 1,
        name: 'Прокопенко Андрій Васильович',
        position: 'Професор',
        disciplineIds: [1, 2],
      },
      {
        id: 2,
        name: 'Рудий Іван Володимирович',
        position: 'Асистент',
        disciplineIds: [2],
      },
      {
        id: 3,
        name: 'Сидоренко Олена Миколаївна',
        position: 'Доцент',
        disciplineIds: [3],
      },
    ],
    groups: [
      { id: 1, name: 'Б-121-24-3' },
      { id: 2, name: 'Б-121-24-4' },
    ],
    students: [
      { id: 1, name: 'Рудий Іван Володимирович', groupId: 1 },
      { id: 2, name: 'Коваленко Олег Петрович', groupId: 1 },
      { id: 3, name: 'Сидоров Дмитро Сергійович', groupId: 2 },
    ],
    grades: [
      { id: 1, studentId: 1, disciplineId: 1, teacherId: 1, grade: 95 },
      { id: 2, studentId: 1, disciplineId: 2, teacherId: 1, grade: 88 },
      { id: 3, studentId: 1, disciplineId: 3, teacherId: 3, grade: 74 },
      { id: 4, studentId: 2, disciplineId: 1, teacherId: 1, grade: 82 },
      { id: 5, studentId: 3, disciplineId: 1, teacherId: 1, grade: 61 },
    ],
  }),

  getters: {
    disciplineById: (state) => (id) => state.disciplines.find((d) => d.id === id),
    teacherById: (state) => (id) => state.teachers.find((t) => t.id === id),
    studentById: (state) => (id) => state.students.find((s) => s.id === id),
    groupById: (state) => (id) => state.groups.find((g) => g.id === id),

    teacherDisciplineNames() {
      return (teacherId) => {
        const teacher = this.teacherById(teacherId);
        if (!teacher) return [];
        return teacher.disciplineIds
          .map((id) => this.disciplineById(id)?.name)
          .filter(Boolean);
      };
    },

    studentGrades(state) {
      return (studentId) =>
        state.grades
          .filter((g) => g.studentId === studentId)
          .map((g) => ({
            ...g,
            discipline: state.disciplines.find((d) => d.id === g.disciplineId)?.name ?? '—',
            teacher: formatTeacherShortName(state.teachers, g.teacherId),
            ECTS: gradeToEcts(g.grade),
          }));
    },

    journalForTeacher(state) {
      return (teacherId) => {
        const teacher = state.teachers.find((t) => t.id === teacherId);
        if (!teacher) return [];
        return state.grades
          .filter((g) => g.teacherId === teacherId && teacher.disciplineIds.includes(g.disciplineId))
          .map((g) => ({
            ...g,
            student: state.students.find((s) => s.id === g.studentId)?.name ?? '—',
            subject: state.disciplines.find((d) => d.id === g.disciplineId)?.name ?? '—',
          }));
      };
    },
  },

  actions: {
    formatTeacherShort(teacherId) {
      const t = this.teacherById(teacherId);
      if (!t) return '—';
      const parts = t.name.split(' ');
      if (parts.length < 2) return t.name;
      return `${parts[0]} ${parts[1][0]}.${parts[2] ? parts[2][0] + '.' : ''}`;
    },

    addGroup(name) {
      this.groups.push({ id: Date.now(), name });
    },
    addStudent(name, groupId) {
      this.students.push({ id: Date.now(), name, groupId });
    },
    addTeacher(name, position, disciplineIds = []) {
      this.teachers.push({ id: Date.now(), name, position, disciplineIds });
    },
    addDiscipline(name, description = '') {
      this.disciplines.push({ id: Date.now(), name, description });
    },

    updateGroup(id, name) {
      const item = this.groups.find((g) => g.id === id);
      if (item) item.name = name;
    },
    updateStudent(id, data) {
      const item = this.students.find((s) => s.id === id);
      if (item) Object.assign(item, data);
    },
    updateTeacher(id, data) {
      const item = this.teachers.find((t) => t.id === id);
      if (item) Object.assign(item, data);
    },
    updateDiscipline(id, data) {
      const item = this.disciplines.find((d) => d.id === id);
      if (item) Object.assign(item, data);
    },

    removeGroup(id) {
      this.groups = this.groups.filter((g) => g.id !== id);
    },
    removeStudent(id) {
      this.students = this.students.filter((s) => s.id !== id);
      this.grades = this.grades.filter((g) => g.studentId !== id);
    },
    removeTeacher(id) {
      this.teachers = this.teachers.filter((t) => t.id !== id);
      this.grades = this.grades.filter((g) => g.teacherId !== id);
    },
    removeDiscipline(id) {
      this.disciplines = this.disciplines.filter((d) => d.id !== id);
      this.teachers.forEach((t) => {
        t.disciplineIds = t.disciplineIds.filter((did) => did !== id);
      });
      this.grades = this.grades.filter((g) => g.disciplineId !== id);
    },

    updateGrade(gradeId, value) {
      const item = this.grades.find((g) => g.id === gradeId);
      if (item) item.grade = Math.min(100, Math.max(0, value));
    },

    ensureGrade(studentId, disciplineId, teacherId) {
      let item = this.grades.find(
        (g) => g.studentId === studentId && g.disciplineId === disciplineId
      );
      if (!item) {
        item = { id: Date.now(), studentId, disciplineId, teacherId, grade: 0 };
        this.grades.push(item);
      }
      return item;
    },
  },
});

export { gradeToEcts };
