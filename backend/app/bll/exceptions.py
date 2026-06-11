class BllException(Exception):
    """Base exception for all business logic layer errors."""

    pass


class AuthenticationException(BllException):
    pass


class UserNotFoundException(BllException):
    pass


class InvalidRoleException(BllException):
    pass


class GroupAlreadyExistsException(BllException):
    pass


class GroupNotFoundException(BllException):
    pass


class StudentNotFoundException(BllException):
    pass


class TeacherNotFoundException(BllException):
    pass


class DisciplineAlreadyExistsException(BllException):
    pass


class DisciplineNotFoundException(BllException):
    pass


class GradeNotFoundException(BllException):
    pass


class AccessDeniedException(BllException):
    pass
