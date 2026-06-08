from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from app.database import Base

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

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # admin, manager, teacher, student

    teacher_id = Column(
        Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True
    )

    teacher = relationship("Teacher", back_populates="user")
    student = relationship("Student", back_populates="user")


class DepartmentInfo(Base):
    __tablename__ = "department_info"

    id = Column(Integer, primary_key=True, default=1)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    head = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    students = relationship(
        "Student", back_populates="group", cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    group = relationship("Group", back_populates="students")
    grades = relationship(
        "Grade", back_populates="student", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="student", uselist=False)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False)  # Професор, Доцент, Асистент

    disciplines = relationship(
        "Discipline",
        secondary=teacher_discipline_association,
        back_populates="teachers",
    )
    grades = relationship(
        "Grade", back_populates="teacher", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="teacher", uselist=False)


class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)

    teachers = relationship(
        "Teacher",
        secondary=teacher_discipline_association,
        back_populates="disciplines",
    )
    grades = relationship(
        "Grade", back_populates="discipline", cascade="all, delete-orphan"
    )


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    discipline_id = Column(
        Integer, ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id = Column(
        Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    grade = Column(Integer, nullable=False, default=0)

    student = relationship("Student", back_populates="grades")
    discipline = relationship("Discipline", back_populates="grades")
    teacher = relationship("Teacher", back_populates="grades")
