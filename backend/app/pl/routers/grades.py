from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_role
from app.bll.exceptions import (
    AccessDeniedException,
    DisciplineNotFoundException,
    GradeNotFoundException,
    StudentNotFoundException,
    TeacherNotFoundException,
)
from app.bll.services.grade_service import GradeService
from app.dal.models import User
from app.pl.dependencies import get_grade_service
from app.pl.schemas import GradeEnsure, GradeResponse, GradeUpdate

router = APIRouter(prefix="/grades", tags=["grades"])


@router.get("/my", response_model=list[GradeResponse])
def get_my_grades(
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_role(["student"])),
):
    if not current_user.student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any student profile",
        )
    try:
        return service.get_my_grades(current_user.student_id)
    except StudentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/journal", response_model=list[GradeResponse])
def get_teacher_journal(
    discipline_id: int | None = None,
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_role(["teacher"])),
):
    if not current_user.teacher_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any teacher profile",
        )
    try:
        return service.get_teacher_journal(current_user.teacher_id, discipline_id)
    except TeacherNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post("/ensure", response_model=GradeResponse)
def ensure_grade(
    req: GradeEnsure,
    service: GradeService = Depends(get_grade_service),
    _current_user: User = Depends(require_role(["admin", "manager", "teacher"])),
):
    try:
        return service.ensure_grade(req.student_id, req.discipline_id, req.teacher_id)
    except (
        StudentNotFoundException,
        DisciplineNotFoundException,
        TeacherNotFoundException,
    ) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: int,
    req: GradeUpdate,
    service: GradeService = Depends(get_grade_service),
    current_user: User = Depends(require_role(["admin", "manager", "teacher"])),
):
    try:
        return service.update_grade(
            grade_id, req.grade, current_user.role, current_user.teacher_id
        )
    except GradeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AccessDeniedException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
