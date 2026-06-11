from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.dal.database import Base

# Teacher-Discipline junction table
teacher_discipline_association = Table(
    "teacher_discipline_association",
    Base.metadata,
    Column(
        "teacher_id",
        Integer,
        ForeignKey("teachers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "discipline_id",
        Integer,
        ForeignKey("disciplines.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(Base):
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    username: str = Column(String, unique=True, index=True, nullable=False)
    hashed_password: str = Column(String, nullable=False)
    role: str = Column(String, nullable=False)  # admin, manager, teacher, student

    teacher_id: int | None = Column(
        Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    student_id: int | None = Column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True
    )

    teacher: "Teacher" = relationship("Teacher", back_populates="user")
    student: "Student" = relationship("Student", back_populates="user")


class DepartmentInfo(Base):
    __tablename__ = "department_info"

    id: int = Column(Integer, primary_key=True, default=1)
    name: str = Column(String, nullable=False)
    description: str | None = Column(Text, nullable=True)
    head: str | None = Column(String, nullable=True)
    email: str | None = Column(String, nullable=True)
    phone: str | None = Column(String, nullable=True)


class Group(Base):
    __tablename__ = "groups"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, index=True, nullable=False)

    students: list["Student"] = relationship(
        "Student", back_populates="group", cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    group_id: int = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    group: "Group" = relationship("Group", back_populates="students")
    grades: list["Grade"] = relationship(
        "Grade", back_populates="student", cascade="all, delete-orphan"
    )
    user: "User" = relationship("User", back_populates="student", uselist=False)


class Teacher(Base):
    __tablename__ = "teachers"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, nullable=False)
    position: str = Column(
        String, nullable=False
    )  # Professor, Associate Professor, Assistant

    disciplines: list["Discipline"] = relationship(
        "Discipline",
        secondary=teacher_discipline_association,
        back_populates="teachers",
    )
    grades: list["Grade"] = relationship(
        "Grade", back_populates="teacher", cascade="all, delete-orphan"
    )
    user: "User" = relationship("User", back_populates="teacher", uselist=False)


class Discipline(Base):
    __tablename__ = "disciplines"

    id: int = Column(Integer, primary_key=True, index=True)
    name: str = Column(String, unique=True, index=True, nullable=False)
    description: str | None = Column(Text, nullable=True)

    teachers: list["Teacher"] = relationship(
        "Teacher",
        secondary=teacher_discipline_association,
        back_populates="disciplines",
    )
    grades: list["Grade"] = relationship(
        "Grade", back_populates="discipline", cascade="all, delete-orphan"
    )


class Grade(Base):
    __tablename__ = "grades"

    id: int = Column(Integer, primary_key=True, index=True)
    student_id: int = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    discipline_id: int = Column(
        Integer, ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: int = Column(
        Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    grade: int = Column(Integer, nullable=False, default=0)

    student: "Student" = relationship("Student", back_populates="grades")
    discipline: "Discipline" = relationship("Discipline", back_populates="grades")
    teacher: "Teacher" = relationship("Teacher", back_populates="grades")
