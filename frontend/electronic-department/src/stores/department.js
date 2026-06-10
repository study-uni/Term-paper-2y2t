import { defineStore } from "pinia";
import api from "../api";

const normalizeStudent = (student) => ({
  ...student,
  groupId: student.group_id ?? student.groupId,
});

const normalizeTeacher = (teacher) => ({
  ...teacher,
  disciplineIds: teacher.discipline_ids ?? teacher.disciplineIds,
});

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

export const useDepartmentStore = defineStore("department", {
  state: () => ({
    info: {
      name: "",
      description: "",
      head: "",
      email: "",
      phone: "",
    },
    disciplines: [],
    teachers: [],
    groups: [],
    students: [],
    grades: [],
  }),

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
          .filter((g) => g.student_id === Number(studentId))
          .map((g) => ({
            ...g,
            discipline:
              state.disciplines.find((d) => d.id === g.discipline_id)?.name ??
              "—",
            teacher: formatTeacherShortName(state.teachers, g.teacher_id),
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
              g.teacher_id === Number(teacherId) &&
              teacher.disciplineIds.includes(g.discipline_id),
          )
          .map((g) => ({
            ...g,
            student:
              state.students.find((s) => s.id === g.student_id)?.name ?? "—",
            subject:
              state.disciplines.find((d) => d.id === g.discipline_id)?.name ??
              "—",
          }));
      };
    },
  },

  actions: {
    // --- Public API Inits ---
    async initPublic() {
      try {
        await Promise.all([
          this.fetchInfo(),
          this.fetchTeachers(),
          this.fetchDisciplines(),
        ]);
      } catch (e) {
        console.error("Error initializing public department data:", e);
      }
    },

    async initPrivate(role) {
      try {
        await Promise.all([this.fetchGroups(), this.fetchStudents()]);
        if (role === "student") {
          await this.fetchGradesForStudent();
        } else if (role === "teacher") {
          await this.fetchGradesForTeacher();
        }
      } catch (e) {
        console.error("Error initializing private department data:", e);
      }
    },

    // --- Department Info ---
    async fetchInfo() {
      const response = await api.get("/department/info");
      this.info = response.data;
    },

    async updateInfo(name, description) {
      const response = await api.put("/department/info", { name, description });
      this.info = response.data;
    },

    async persist() {
      // In the legacy code, this saved changes to localStorage.
      // Now, since the admin editing is tied to changes, we persist it directly.
      if (this.info && this.info.name) {
        try {
          await api.put("/department/info", {
            name: this.info.name,
            description: this.info.description,
          });
        } catch (e) {
          console.error("Failed to persist department info:", e);
        }
      }
    },

    // --- Groups ---
    async fetchGroups() {
      const response = await api.get("/groups");
      this.groups = response.data;
    },

    async addGroup(name) {
      await api.post("/groups", { name });
      await this.fetchGroups();
    },

    async updateGroup(id, name) {
      await api.put(`/groups/${id}`, { name });
      await this.fetchGroups();
    },

    async removeGroup(id) {
      await api.delete(`/groups/${id}`);
      await this.fetchGroups();
    },

    // --- Students ---
    async fetchStudents() {
      const response = await api.get("/students");
      this.students = response.data.map(normalizeStudent);
    },

    async addStudent(name, groupId) {
      await api.post("/students", { name, group_id: Number(groupId) });
      await Promise.all([this.fetchStudents(), this.fetchGroups()]);
    },

    async updateStudent(id, data) {
      await api.put(`/students/${id}`, {
        name: data.name,
        group_id: Number(data.groupId),
      });
      await Promise.all([this.fetchStudents(), this.fetchGroups()]);
    },

    async removeStudent(id) {
      await api.delete(`/students/${id}`);
      await Promise.all([this.fetchStudents(), this.fetchGroups()]);
    },

    // --- Teachers ---
    async fetchTeachers() {
      const response = await api.get("/teachers");
      this.teachers = response.data.map(normalizeTeacher);
    },

    async addTeacher(name, position, disciplineIds = []) {
      await api.post("/teachers", {
        name,
        position,
        discipline_ids: disciplineIds.map(Number),
      });
      await this.fetchTeachers();
    },

    async updateTeacher(id, data) {
      await api.put(`/teachers/${id}`, {
        name: data.name,
        position: data.position,
        discipline_ids: data.disciplineIds.map(Number),
      });
      await this.fetchTeachers();
    },

    async removeTeacher(id) {
      await api.delete(`/teachers/${id}`);
      await this.fetchTeachers();
    },

    // --- Disciplines ---
    async fetchDisciplines() {
      const response = await api.get("/disciplines");
      this.disciplines = response.data;
    },

    async addDiscipline(name, description = "") {
      await api.post("/disciplines", { name, description });
      await this.fetchDisciplines();
    },

    async updateDiscipline(id, data) {
      await api.put(`/disciplines/${id}`, {
        name: data.name,
        description: data.description,
      });
      await this.fetchDisciplines();
    },

    async removeDiscipline(id) {
      await api.delete(`/disciplines/${id}`);
      await this.fetchDisciplines();
    },

    // --- Grades ---
    async fetchGradesForStudent() {
      const response = await api.get("/grades/my");
      this.grades = response.data;
    },

    async fetchGradesForTeacher(disciplineId = null) {
      const params = {};
      if (disciplineId) params.discipline_id = disciplineId;
      const response = await api.get("/grades/journal", { params });
      this.grades = response.data;
    },

    async updateGrade(gradeId, value) {
      const val = Math.min(100, Math.max(0, Number(value) || 0));
      await api.put(`/grades/${gradeId}`, { grade: val });
      // Update locally
      const item = this.grades.find((g) => g.id === Number(gradeId));
      if (item) {
        item.grade = val;
      }
    },

    async ensureGrade(studentId, disciplineId, teacherId) {
      const response = await api.post("/grades/ensure", {
        student_id: Number(studentId),
        discipline_id: Number(disciplineId),
        teacher_id: Number(teacherId),
      });
      const newGrade = response.data;

      const idx = this.grades.findIndex((g) => g.id === newGrade.id);
      if (idx >= 0) {
        this.grades[idx] = newGrade;
      } else {
        this.grades.push(newGrade);
      }
      return newGrade;
    },

    clearPrivate() {
      this.groups = [];
      this.students = [];
      this.grades = [];
    },
  },
});

export { gradeToEcts };
