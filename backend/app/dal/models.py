from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(
        String, nullable=False
    )  # admin, manager, teacher, student

    teacher_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    student_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True
    )

    teacher: Mapped[Optional["Teacher"]] = relationship(back_populates="user")
    student: Mapped[Optional["Student"]] = relationship(back_populates="user")


class DepartmentInfo(Base):
    __tablename__ = "department_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    head: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    students: Mapped[list["Student"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )

    group: Mapped[Optional["Group"]] = relationship(back_populates="students")
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    user: Mapped[Optional["User"]] = relationship(
        back_populates="student", uselist=False
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[str] = mapped_column(
        String, nullable=False
    )  # Professor, Associate Professor, Assistant

    disciplines: Mapped[list["Discipline"]] = relationship(
        secondary=teacher_discipline_association,
        back_populates="teachers",
    )
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )
    user: Mapped[Optional["User"]] = relationship(
        back_populates="teacher", uselist=False
    )


class Discipline(Base):
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    teachers: Mapped[list["Teacher"]] = relationship(
        secondary=teacher_discipline_association,
        back_populates="disciplines",
    )
    grades: Mapped[list["Grade"]] = relationship(
        back_populates="discipline", cascade="all, delete-orphan"
    )


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False
    )
    discipline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("disciplines.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False
    )
    grade: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    student: Mapped[Optional["Student"]] = relationship(back_populates="grades")
    discipline: Mapped[Optional["Discipline"]] = relationship(back_populates="grades")
    teacher: Mapped[Optional["Teacher"]] = relationship(back_populates="grades")
