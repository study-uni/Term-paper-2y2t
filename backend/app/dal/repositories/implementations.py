from sqlalchemy.orm import Session

from app.dal.models import (
    DepartmentInfo,
    Discipline,
    Grade,
    Group,
    Student,
    Teacher,
    User,
)
from app.dal.repositories.base import SQLAlchemyBaseRepository


class UserRepository(SQLAlchemyBaseRepository[User]):
    def __init__(self, session: Session):
        super().__init__(session, User)

    def get_by_username(self, username: str) -> User | None:
        return self.session.query(User).filter(User.username == username).first()

    def get_by_role(self, role: str) -> list[User]:
        return self.session.query(User).filter(User.role == role).all()

    def get_by_role_and_teacher_id(self, role: str, teacher_id: int) -> User | None:
        return (
            self.session.query(User)
            .filter(User.role == role, User.teacher_id == teacher_id)
            .first()
        )

    def get_by_role_and_student_id(self, role: str, student_id: int) -> User | None:
        return (
            self.session.query(User)
            .filter(User.role == role, User.student_id == student_id)
            .first()
        )


class DepartmentInfoRepository(SQLAlchemyBaseRepository[DepartmentInfo]):
    def __init__(self, session: Session):
        super().__init__(session, DepartmentInfo)

    def get_singleton(self) -> DepartmentInfo:
        info = self.session.query(DepartmentInfo).filter(DepartmentInfo.id == 1).first()
        if not info:
            info = DepartmentInfo(id=1, name="Кафедра", description="")
            self.session.add(info)
            self.session.flush()
        return info


class GroupRepository(SQLAlchemyBaseRepository[Group]):
    def __init__(self, session: Session):
        super().__init__(session, Group)

    def get_by_name(self, name: str) -> Group | None:
        return self.session.query(Group).filter(Group.name == name).first()

    def get_all_ordered_by_name(self) -> list[Group]:
        return self.session.query(Group).order_by(Group.name).all()


class StudentRepository(SQLAlchemyBaseRepository[Student]):
    def __init__(self, session: Session):
        super().__init__(session, Student)

    def get_all_ordered_by_name(self) -> list[Student]:
        return self.session.query(Student).order_by(Student.name).all()

    def get_count_by_group_id(self, group_id: int) -> int:
        return self.session.query(Student).filter(Student.group_id == group_id).count()


class TeacherRepository(SQLAlchemyBaseRepository[Teacher]):
    def __init__(self, session: Session):
        super().__init__(session, Teacher)

    def get_all_ordered_by_name(self) -> list[Teacher]:
        return self.session.query(Teacher).order_by(Teacher.name).all()


class DisciplineRepository(SQLAlchemyBaseRepository[Discipline]):
    def __init__(self, session: Session):
        super().__init__(session, Discipline)

    def get_by_name(self, name: str) -> Discipline | None:
        return self.session.query(Discipline).filter(Discipline.name == name).first()

    def get_all_ordered_by_name(self) -> list[Discipline]:
        return self.session.query(Discipline).order_by(Discipline.name).all()


class GradeRepository(SQLAlchemyBaseRepository[Grade]):
    def __init__(self, session: Session):
        super().__init__(session, Grade)

    def get_by_student_id(self, student_id: int) -> list[Grade]:
        return self.session.query(Grade).filter(Grade.student_id == student_id).all()

    def get_by_teacher_id(self, teacher_id: int) -> list[Grade]:
        return self.session.query(Grade).filter(Grade.teacher_id == teacher_id).all()

    def get_by_student_discipline_teacher(
        self, student_id: int, discipline_id: int, teacher_id: int
    ) -> Grade | None:
        return (
            self.session.query(Grade)
            .filter(
                Grade.student_id == student_id,
                Grade.discipline_id == discipline_id,
                Grade.teacher_id == teacher_id,
            )
            .first()
        )
