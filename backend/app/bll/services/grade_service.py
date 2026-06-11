from app.bll.exceptions import (
    AccessDeniedException,
    DisciplineNotFoundException,
    GradeNotFoundException,
    StudentNotFoundException,
    TeacherNotFoundException,
)
from app.dal.models import Grade
from app.dal.uow.sqlalchemy_uow import AbstractUnitOfWork
from app.pl.schemas import GradeResponse


class GradeService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def _to_grade_response(self, grade: Grade) -> GradeResponse:
        t_name = grade.teacher.name if grade.teacher else "—"
        parts = t_name.split(" ")
        if len(parts) >= 2:
            short_t = f"{parts[0]} {parts[1][0]}."
            if len(parts) >= 3:
                short_t += f" {parts[2][0]}."
        else:
            short_t = t_name

        return GradeResponse(
            id=grade.id,
            student_id=grade.student_id,
            discipline_id=grade.discipline_id,
            teacher_id=grade.teacher_id,
            grade=grade.grade,
            student=grade.student.name if grade.student else "—",
            subject=grade.discipline.name if grade.discipline else "—",
            teacher=short_t,
        )

    def get_my_grades(self, student_id: int) -> list[GradeResponse]:
        with self.uow:
            student = self.uow.students.get_by_id(student_id)
            if not student:
                raise StudentNotFoundException("Student profile not found")
            grades = self.uow.grades.get_by_student_id(student_id)
            return [self._to_grade_response(g) for g in grades]

    def get_teacher_journal(
        self, teacher_id: int, discipline_id: int | None = None
    ) -> list[GradeResponse]:
        with self.uow:
            teacher = self.uow.teachers.get_by_id(teacher_id)
            if not teacher:
                raise TeacherNotFoundException("Teacher profile not found")

            # determine target disciplines
            target_ids = []
            if discipline_id:
                if discipline_id not in [d.id for d in teacher.disciplines]:
                    raise AccessDeniedException("You do not teach this discipline")
                target_ids = [discipline_id]
            else:
                target_ids = [d.id for d in teacher.disciplines]

            # initialize empty grades for teacher's disciplines
            students = self.uow.students.get_all()
            for s in students:
                for d_id in target_ids:
                    exists = self.uow.grades.get_by_student_discipline_teacher(
                        s.id, d_id, teacher.id
                    )
                    if not exists:
                        new_grade = Grade(
                            student_id=s.id,
                            discipline_id=d_id,
                            teacher_id=teacher.id,
                            grade=0,
                        )
                        self.uow.grades.add(new_grade)
            self.uow.commit()

            # query results
            grades = self.uow.grades.get_by_teacher_id(teacher.id)
            if discipline_id:
                grades = [g for g in grades if g.discipline_id == discipline_id]
            else:
                grades = [g for g in grades if g.discipline_id in target_ids]

            return [self._to_grade_response(g) for g in grades]

    def ensure_grade(
        self, student_id: int, discipline_id: int, teacher_id: int
    ) -> GradeResponse:
        with self.uow:
            student = self.uow.students.get_by_id(student_id)
            discipline = self.uow.disciplines.get_by_id(discipline_id)
            teacher = self.uow.teachers.get_by_id(teacher_id)

            if not student:
                raise StudentNotFoundException("Student not found")
            if not discipline:
                raise DisciplineNotFoundException("Discipline not found")
            if not teacher:
                raise TeacherNotFoundException("Teacher not found")

            grade = self.uow.grades.get_by_student_discipline_teacher(
                student_id, discipline_id, teacher_id
            )
            if not grade:
                grade = Grade(
                    student_id=student_id,
                    discipline_id=discipline_id,
                    teacher_id=teacher_id,
                    grade=0,
                )
                self.uow.grades.add(grade)
                self.uow.commit()

            return self._to_grade_response(grade)

    def update_grade(
        self,
        grade_id: int,
        grade_value: int,
        user_role: str,
        user_teacher_id: int | None,
    ) -> GradeResponse:
        with self.uow:
            grade = self.uow.grades.get_by_id(grade_id)
            if not grade:
                raise GradeNotFoundException("Grade record not found")

            # teacher permissions check
            if user_role == "teacher" and grade.teacher_id != user_teacher_id:
                raise AccessDeniedException("You can only edit grades you issued")

            grade.grade = grade_value
            self.uow.commit()
            return self._to_grade_response(grade)
