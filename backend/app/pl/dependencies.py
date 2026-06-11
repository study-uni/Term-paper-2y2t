from fastapi import Depends

from app.bll.services.auth_service import AuthService
from app.bll.services.department_service import DepartmentService
from app.bll.services.grade_service import GradeService
from app.dal.database import SessionLocal
from app.dal.uow.sqlalchemy_uow import AbstractUnitOfWork, SQLAlchemyUnitOfWork


def get_uow() -> AbstractUnitOfWork:
    return SQLAlchemyUnitOfWork(SessionLocal)


def get_auth_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> AuthService:
    return AuthService(uow)


def get_department_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> DepartmentService:
    return DepartmentService(uow)


def get_grade_service(uow: AbstractUnitOfWork = Depends(get_uow)) -> GradeService:
    return GradeService(uow)
