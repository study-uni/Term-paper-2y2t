from app.bll.exceptions import (
    AuthenticationException,
    InvalidRoleException,
    UserNotFoundException,
)
from app.dal.uow.sqlalchemy_uow import AbstractUnitOfWork
from app.security import create_access_token, verify_password


class AuthService:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def login(self, username: str, password: str) -> dict:
        with self.uow:
            user = self.uow.users.get_by_username(username)
            if not user or not verify_password(password, user.hashed_password):
                raise AuthenticationException("Incorrect username or password")
            return self._build_token_response(user)

    def mock_login(self, role: str, profile_id: int | None = None) -> dict:
        if role not in ["admin", "manager", "teacher", "student"]:
            raise InvalidRoleException(f"Invalid simulator role: {role}")

        with self.uow:
            user = None
            if role == "admin":
                admins = self.uow.users.get_by_role("admin")
                user = admins[0] if admins else None
            elif role == "manager":
                managers = self.uow.users.get_by_role("manager")
                user = managers[0] if managers else None
            elif role == "teacher":
                if profile_id:
                    user = self.uow.users.get_by_role_and_teacher_id(
                        "teacher", profile_id
                    )
                if not user:
                    teachers = self.uow.users.get_by_role("teacher")
                    user = teachers[0] if teachers else None
            elif role == "student":
                if profile_id:
                    user = self.uow.users.get_by_role_and_student_id(
                        "student", profile_id
                    )
                if not user:
                    students = self.uow.users.get_by_role("student")
                    user = students[0] if students else None

            if not user:
                raise UserNotFoundException(f"No user account found for role '{role}'.")

            return self._build_token_response(user)

    def _build_token_response(self, user) -> dict:
        access_token = create_access_token(data={"sub": user.username})

        name = user.username
        profile_id = None
        profile_type = None

        if user.role == "admin":
            name = "Адміністратор Системи"
        elif user.role == "manager":
            name = "Менеджер Кафедри"
        elif user.role == "teacher" and user.teacher_id:
            teacher = self.uow.teachers.get_by_id(user.teacher_id)
            if teacher:
                name = teacher.name
                profile_id = teacher.id
                profile_type = "teacher"
        elif user.role == "student" and user.student_id:
            student = self.uow.students.get_by_id(user.student_id)
            if student:
                name = student.name
                profile_id = student.id
                profile_type = "student"

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": user.role,
            "profile_id": profile_id,
            "profile_type": profile_type,
            "name": name,
        }
