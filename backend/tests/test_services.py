from unittest.mock import MagicMock

import pytest

from app.bll.exceptions import (
    AccessDeniedException,
    GroupAlreadyExistsException,
    GroupNotFoundException,
)
from app.bll.services.department_service import DepartmentService
from app.bll.services.grade_service import GradeService
from app.dal.models import Grade, Group, Student


def test_create_group_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.groups.get_by_name.return_value = None

    # Simulate DB assigning an ID on add
    def fake_add(group):
        group.id = 1

    mock_uow.groups.add.side_effect = fake_add

    service = DepartmentService(mock_uow)

    # Act
    response = service.create_group("Б-121-24-3")

    # Assert
    assert response.id == 1
    assert response.name == "Б-121-24-3"
    mock_uow.groups.add.assert_called_once()
    mock_uow.commit.assert_called_once()


def test_create_group_already_exists():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.groups.get_by_name.return_value = Group(id=1, name="Б-121-24-3")
    service = DepartmentService(mock_uow)

    # Act & Assert
    with pytest.raises(GroupAlreadyExistsException):
        service.create_group("Б-121-24-3")

    mock_uow.groups.add.assert_not_called()
    mock_uow.commit.assert_not_called()


def test_update_group_not_found():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.groups.get_by_id.return_value = None
    service = DepartmentService(mock_uow)

    # Act & Assert
    with pytest.raises(GroupNotFoundException):
        service.update_group(99, "Нова Назва")

    mock_uow.commit.assert_not_called()


def test_get_my_grades_success():
    # Arrange
    mock_uow = MagicMock()
    mock_uow.students.get_by_id.return_value = Student(id=5, name="Олег Петров")

    mock_grade = Grade(id=10, student_id=5, discipline_id=1, teacher_id=2, grade=95)
    # mock relationships that _to_grade_response accesses
    mock_grade.student = Student(name="Олег Петров")
    mock_grade.discipline = MagicMock(name="Веб-програмування")
    mock_grade.discipline.name = "Веб-програмування"
    mock_grade.teacher = MagicMock()
    mock_grade.teacher.name = "Прокопенко Андрій Васильович"

    mock_uow.grades.get_by_student_id.return_value = [mock_grade]
    service = GradeService(mock_uow)

    # Act
    grades = service.get_my_grades(5)

    # Assert
    assert len(grades) == 1
    assert grades[0].grade == 95
    assert grades[0].subject == "Веб-програмування"
    assert grades[0].teacher == "Прокопенко А. В."


def test_update_grade_forbidden_for_other_teacher():
    # Arrange
    mock_uow = MagicMock()
    mock_grade = Grade(
        id=10,
        student_id=5,
        discipline_id=1,
        teacher_id=2,  # Owned by teacher 2
        grade=85,
    )
    mock_uow.grades.get_by_id.return_value = mock_grade
    service = GradeService(mock_uow)

    # Act & Assert (Teacher 3 tries to edit)
    with pytest.raises(AccessDeniedException):
        service.update_grade(
            grade_id=10, grade_value=90, user_role="teacher", user_teacher_id=3
        )

    mock_uow.commit.assert_not_called()
