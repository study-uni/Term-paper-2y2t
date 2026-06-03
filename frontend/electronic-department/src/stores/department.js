import { defineStore } from "pinia";

const STORAGE_KEY = "ed-department";

const gradeToEcts = (grade) => {
  if (grade >= 90) return "A";
  if (grade >= 80) return "B";
  if (grade >= 70) return "C";
  if (grade >= 60) return "D";
  if (grade >= 50) return "E";
  return "F";
};

const formatTeacherShortName = (teachers, teacherId) => {
  const t = teachers.find((x) => x.id === teacherId);
  if (!t) return "—";
  const parts = t.name.split(" ");
  if (parts.length < 2) return t.name;
  return `${parts[0]} ${parts[1][0]}.${parts[2] ? parts[2][0] + "." : ""}`;
};

function loadStoredDepartment() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export const useDepartmentStore = defineStore("department", {
  state: () => {
    const stored = loadStoredDepartment();
    if (stored) return stored;
    return {
      info: {
        name: "Кафедра програмної інженерії",
        description:
          "Кафедра здійснює підготовку бакалаврів та магістрів зі спеціальності «Програмна інженерія». Навчання включає сучасні технології веб-розробки, архітектури ПЗ та проєктування баз даних.",
        head: "Прокопенко Андрій Васильович",
        email: "software@university.edu.ua",
        phone: "+38 (044) 000-00-00",
      },
      disciplines: [
        {
          id: 1,
          name: "Веб-програмування",
          description: "HTML, CSS, JavaScript, Vue.js",
        },
        {
          id: 2,
          name: "Архітектура ПЗ",
          description: "Патерни проєктування, UML, SOLID",
        },
        { id: 3, name: "Бази даних", description: "SQL, нормалізація, ORM" },
      ],
      teachers: [
        {
          id: 1,
          name: "Прокопенко Андрій Васильович",
          position: "Професор",
          disciplineIds: [1, 2],
        },
        {
          id: 2,
          name: "Рудий Іван Володимирович",
          position: "Асистент",
          disciplineIds: [2],
        },
        {
          id: 3,
          name: "Сидоренко Олена Миколаївна",
          position: "Доцент",
          disciplineIds: [3],
        },
      ],
      groups: [
        { id: 1, name: "Б-121-24-3" },
        { id: 2, name: "Б-121-24-4" },
      ],
      students: [
        { id: 1, name: "Рудий Іван Володимирович", groupId: 1 },
        { id: 2, name: "Коваленко Олег Петрович", groupId: 1 },
        { id: 3, name: "Сидоров Дмитро Сергійович", groupId: 2 },
      ],
      grades: [
        { id: 1, studentId: 1, disciplineId: 1, teacherId: 1, grade: 95 },
        { id: 2, studentId: 1, disciplineId: 2, teacherId: 1, grade: 88 },
        { id: 3, studentId: 1, disciplineId: 3, teacherId: 3, grade: 74 },
        { id: 4, studentId: 2, disciplineId: 1, teacherId: 1, grade: 82 },
        { id: 5, studentId: 3, disciplineId: 1, teacherId: 1, grade: 61 },
      ],
    };
  },

  getters: {
    disciplineById: (state) => (id) =>
      state.disciplines.find((d) => d.id === Number(id)),
    teacherById: (state) => (id) =>
      state.teachers.find((t) => t.id === Number(id)),
    studentById: (state) => (id) =>
      state.students.find((s) => s.id === Number(id)),
    groupById: (state) => (id) => state.groups.find((g) => g.id === Number(id)),

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
          .filter((g) => g.studentId === Number(studentId))
          .map((g) => ({
            ...g,
            discipline:
              state.disciplines.find((d) => d.id === g.disciplineId)?.name ??
              "—",
            teacher: formatTeacherShortName(state.teachers, g.teacherId),
            ECTS: gradeToEcts(g.grade),
          }));
    },

    journalForTeacher(state) {
      return (teacherId) => {
        const teacher = state.teachers.find((t) => t.id === Number(teacherId));
        if (!teacher) return [];
        return state.grades
          .filter(
            (g) =>
              g.teacherId === Number(teacherId) &&
              teacher.disciplineIds.includes(g.disciplineId),
          )
          .map((g) => ({
            ...g,
            student:
              state.students.find((s) => s.id === g.studentId)?.name ?? "—",
            subject:
              state.disciplines.find((d) => d.id === g.disciplineId)?.name ??
              "—",
          }));
      };
    },
  },

  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          info: this.info,
          disciplines: this.disciplines,
          teachers: this.teachers,
          groups: this.groups,
          students: this.students,
          grades: this.grades,
        }),
      );
    },

    formatTeacherShort(teacherId) {
      const t = this.teacherById(teacherId);
      if (!t) return "—";
      const parts = t.name.split(" ");
      if (parts.length < 2) return t.name;
      return `${parts[0]} ${parts[1][0]}.${parts[2] ? parts[2][0] + "." : ""}`;
    },

    addGroup(name) {
      this.groups.push({ id: Date.now(), name });
      this.persist();
    },
    addStudent(name, groupId) {
      this.students.push({ id: Date.now(), name, groupId: Number(groupId) });
      this.persist();
    },
    addTeacher(name, position, disciplineIds = []) {
      this.teachers.push({
        id: Date.now(),
        name,
        position,
        disciplineIds: disciplineIds.map(Number),
      });
      this.persist();
    },
    addDiscipline(name, description = "") {
      this.disciplines.push({ id: Date.now(), name, description });
      this.persist();
    },

    updateGroup(id, name) {
      const item = this.groups.find((g) => g.id === Number(id));
      if (item) {
        item.name = name;
        this.persist();
      }
    },
    updateStudent(id, data) {
      const item = this.students.find((s) => s.id === Number(id));
      if (item) {
        Object.assign(item, {
          name: data.name,
          groupId: Number(data.groupId),
        });
        this.persist();
      }
    },
    updateTeacher(id, data) {
      const item = this.teachers.find((t) => t.id === Number(id));
      if (item) {
        Object.assign(item, {
          name: data.name,
          position: data.position,
          disciplineIds: data.disciplineIds.map(Number),
        });
        this.persist();
      }
    },
    updateDiscipline(id, data) {
      const item = this.disciplines.find((d) => d.id === Number(id));
      if (item) {
        Object.assign(item, {
          name: data.name,
          description: data.description,
        });
        this.persist();
      }
    },

    removeGroup(id) {
      this.groups = this.groups.filter((g) => g.id !== Number(id));
      this.persist();
    },
    removeStudent(id) {
      const targetId = Number(id);
      this.students = this.students.filter((s) => s.id !== targetId);
      this.grades = this.grades.filter((g) => g.studentId !== targetId);
      this.persist();
    },
    removeTeacher(id) {
      const targetId = Number(id);
      this.teachers = this.teachers.filter((t) => t.id !== targetId);
      this.grades = this.grades.filter((g) => g.teacherId !== targetId);
      this.persist();
    },
    removeDiscipline(id) {
      const targetId = Number(id);
      this.disciplines = this.disciplines.filter((d) => d.id !== targetId);
      this.teachers.forEach((t) => {
        t.disciplineIds = t.disciplineIds.filter((did) => did !== targetId);
      });
      this.grades = this.grades.filter((g) => g.disciplineId !== targetId);
      this.persist();
    },

    updateGrade(gradeId, value) {
      const item = this.grades.find((g) => g.id === Number(gradeId));
      if (item) {
        item.grade = Math.min(100, Math.max(0, Number(value) || 0));
        this.persist();
      }
    },

    ensureGrade(studentId, disciplineId, teacherId) {
      const sId = Number(studentId);
      const dId = Number(disciplineId);
      const tId = Number(teacherId);

      let item = this.grades.find(
        (g) => g.studentId === sId && g.disciplineId === dId,
      );
      if (!item) {
        item = {
          id: Date.now(),
          studentId: sId,
          disciplineId: dId,
          teacherId: tId,
          grade: 0,
        };
        this.grades.push(item);
        this.persist();
      }
      return item;
    },
  },
});

export { gradeToEcts };
