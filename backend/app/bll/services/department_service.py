from app.bll.exceptions import (
    DisciplineAlreadyExistsException,
    DisciplineNotFoundException,
    GroupAlreadyExistsException,
    GroupNotFoundException,
    StudentNotFoundException,
    TeacherNotFoundException,
)
from app.dal.models import Discipline, Group, Student, Teacher, User
from app.dal.uow.sqlalchemy_uow import AbstractUnitOfWork
from app.pl.schemas import (
    DepartmentInfoResponse,
    DisciplineResponse,
    GroupResponse,
    StudentResponse,
    TeacherResponse,
)
from app.security import get_password_hash


class DepartmentService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def _to_student_response(self, student: Student) -> StudentResponse:
        return StudentResponse(
            id=student.id,
            name=student.name,
            group_id=student.group_id,
            group_name=student.group.name if student.group else "—",
        )

    def _to_teacher_response(self, teacher: Teacher) -> TeacherResponse:
        return TeacherResponse(
            id=teacher.id,
            name=teacher.name,
            position=teacher.position,
            discipline_ids=[d.id for d in teacher.disciplines],
        )

    # Department Info
    def get_department_info(self) -> DepartmentInfoResponse:
        with self.uow:
            info = self.uow.department_info.get_singleton()
            return DepartmentInfoResponse.model_validate(info)

    def update_department_info(
        self, name: str, description: str | None
    ) -> DepartmentInfoResponse:
        with self.uow:
            info = self.uow.department_info.get_singleton()
            info.name = name
            info.description = description
            self.uow.commit()
            return DepartmentInfoResponse.model_validate(info)

    # Groups
    def get_groups(self) -> list[GroupResponse]:
        with self.uow:
            groups = self.uow.groups.get_all_ordered_by_name()
            result = []
            for g in groups:
                count = self.uow.students.get_count_by_group_id(g.id)
                result.append(GroupResponse(id=g.id, name=g.name, student_count=count))
            return result

    def create_group(self, name: str) -> GroupResponse:
        with self.uow:
            existing = self.uow.groups.get_by_name(name)
            if existing:
                raise GroupAlreadyExistsException("Group with this name already exists")
            group = Group(name=name)
            self.uow.groups.add(group)
            self.uow.commit()
            return GroupResponse(id=group.id, name=group.name, student_count=0)

    def update_group(self, group_id: int, name: str) -> GroupResponse:
        with self.uow:
            group = self.uow.groups.get_by_id(group_id)
            if not group:
                raise GroupNotFoundException("Group not found")
            existing = self.uow.groups.get_by_name(name)
            if existing and existing.id != group_id:
                raise GroupAlreadyExistsException("Group with this name already exists")
            group.name = name
            self.uow.commit()
            count = self.uow.students.get_count_by_group_id(group.id)
            return GroupResponse(id=group.id, name=group.name, student_count=count)

    def delete_group(self, group_id: int) -> None:
        with self.uow:
            group = self.uow.groups.get_by_id(group_id)
            if not group:
                raise GroupNotFoundException("Group not found")
            self.uow.groups.delete(group)
            self.uow.commit()

    # Students
    def get_students(self) -> list[StudentResponse]:
        with self.uow:
            students = self.uow.students.get_all_ordered_by_name()
            return [self._to_student_response(s) for s in students]

    def create_student(self, name: str, group_id: int) -> StudentResponse:
        with self.uow:
            group = self.uow.groups.get_by_id(group_id)
            if not group:
                raise GroupNotFoundException("Group not found")

            student = Student(name=name, group_id=group_id)
            self.uow.students.add(student)
            self.uow.commit()  # commit to get student ID

            # generate simulator user
            base_username = student.name.lower().replace(" ", "_")
            username = base_username
            idx = 1
            while self.uow.users.get_by_username(username):
                username = f"{base_username}_{idx}"
                idx += 1

            hashed_pwd = get_password_hash("studentpassword")
            new_user = User(
                username=username,
                hashed_password=hashed_pwd,
                role="student",
                student_id=student.id,
            )
            self.uow.users.add(new_user)
            self.uow.commit()
            return self._to_student_response(student)

    def update_student(
        self, student_id: int, name: str, group_id: int
    ) -> StudentResponse:
        with self.uow:
            student = self.uow.students.get_by_id(student_id)
            if not student:
                raise StudentNotFoundException("Student not found")
            group = self.uow.groups.get_by_id(group_id)
            if not group:
                raise GroupNotFoundException("Group not found")

            student.name = name
            student.group_id = group_id
            self.uow.commit()
            return self._to_student_response(student)

    def delete_student(self, student_id: int) -> None:
        with self.uow:
            student = self.uow.students.get_by_id(student_id)
            if not student:
                raise StudentNotFoundException("Student not found")

            user = self.uow.users.get_by_role_and_student_id("student", student_id)
            if user:
                self.uow.users.delete(user)

            self.uow.students.delete(student)
            self.uow.commit()

    # Teachers
    def get_teachers(self) -> list[TeacherResponse]:
        with self.uow:
            teachers = self.uow.teachers.get_all_ordered_by_name()
            return [self._to_teacher_response(t) for t in teachers]

    def create_teacher(
        self, name: str, position: str, discipline_ids: list[int]
    ) -> TeacherResponse:
        with self.uow:
            teacher = Teacher(name=name, position=position)
            if discipline_ids:
                disciplines = []
                for d_id in discipline_ids:
                    d = self.uow.disciplines.get_by_id(d_id)
                    if d:
                        disciplines.append(d)
                teacher.disciplines = disciplines

            self.uow.teachers.add(teacher)
            self.uow.commit()  # commit to get teacher ID

            # generate simulator user
            base_username = teacher.name.lower().replace(" ", "_")
            username = base_username
            idx = 1
            while self.uow.users.get_by_username(username):
                username = f"{base_username}_{idx}"
                idx += 1

            hashed_pwd = get_password_hash("teacherpassword")
            new_user = User(
                username=username,
                hashed_password=hashed_pwd,
                role="teacher",
                teacher_id=teacher.id,
            )
            self.uow.users.add(new_user)
            self.uow.commit()
            return self._to_teacher_response(teacher)

    def update_teacher(
        self, teacher_id: int, name: str, position: str, discipline_ids: list[int]
    ) -> TeacherResponse:
        with self.uow:
            teacher = self.uow.teachers.get_by_id(teacher_id)
            if not teacher:
                raise TeacherNotFoundException("Teacher not found")

            teacher.name = name
            teacher.position = position

            if discipline_ids is not None:
                disciplines = []
                for d_id in discipline_ids:
                    d = self.uow.disciplines.get_by_id(d_id)
                    if d:
                        disciplines.append(d)
                teacher.disciplines = disciplines

            self.uow.commit()
            return self._to_teacher_response(teacher)

    def delete_teacher(self, teacher_id: int) -> None:
        with self.uow:
            teacher = self.uow.teachers.get_by_id(teacher_id)
            if not teacher:
                raise TeacherNotFoundException("Teacher not found")

            user = self.uow.users.get_by_role_and_teacher_id("teacher", teacher_id)
            if user:
                self.uow.users.delete(user)

            self.uow.teachers.delete(teacher)
            self.uow.commit()

    # Disciplines
    def get_disciplines(self) -> list[DisciplineResponse]:
        with self.uow:
            disciplines = self.uow.disciplines.get_all_ordered_by_name()
            return [DisciplineResponse.model_validate(d) for d in disciplines]

    def create_discipline(
        self, name: str, description: str | None
    ) -> DisciplineResponse:
        with self.uow:
            existing = self.uow.disciplines.get_by_name(name)
            if existing:
                raise DisciplineAlreadyExistsException(
                    "Discipline with this name already exists"
                )

            discipline = Discipline(name=name, description=description)
            self.uow.disciplines.add(discipline)
            self.uow.commit()
            return DisciplineResponse.model_validate(discipline)

    def update_discipline(
        self, discipline_id: int, name: str, description: str | None
    ) -> DisciplineResponse:
        with self.uow:
            discipline = self.uow.disciplines.get_by_id(discipline_id)
            if not discipline:
                raise DisciplineNotFoundException("Discipline not found")

            existing = self.uow.disciplines.get_by_name(name)
            if existing and existing.id != discipline_id:
                raise DisciplineAlreadyExistsException(
                    "Discipline with this name already exists"
                )

            discipline.name = name
            discipline.description = description
            self.uow.commit()
            return DisciplineResponse.model_validate(discipline)

    def delete_discipline(self, discipline_id: int) -> None:
        with self.uow:
            discipline = self.uow.disciplines.get_by_id(discipline_id)
            if not discipline:
                raise DisciplineNotFoundException("Discipline not found")
            self.uow.disciplines.delete(discipline)
            self.uow.commit()
