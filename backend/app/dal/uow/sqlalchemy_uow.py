from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.dal.repositories.implementations import (
    DepartmentInfoRepository,
    DisciplineRepository,
    GradeRepository,
    GroupRepository,
    StudentRepository,
    TeacherRepository,
    UserRepository,
)


class AbstractUnitOfWork(ABC):
    users: UserRepository
    groups: GroupRepository
    students: StudentRepository
    teachers: TeacherRepository
    disciplines: DisciplineRepository
    grades: GradeRepository
    department_info: DepartmentInfoRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: Optional[Session] = None

    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()
        self.users = UserRepository(self.session)
        self.groups = GroupRepository(self.session)
        self.students = StudentRepository(self.session)
        self.teachers = TeacherRepository(self.session)
        self.disciplines = DisciplineRepository(self.session)
        self.grades = GradeRepository(self.session)
        self.department_info = DepartmentInfoRepository(self.session)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                self.rollback()
            else:
                self.commit()
        finally:
            if self.session:
                self.session.close()

    def commit(self):
        if self.session:
            self.session.commit()

    def rollback(self):
        if self.session:
            self.session.rollback()
