from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_role
from app.bll.exceptions import (
    DisciplineAlreadyExistsException,
    DisciplineNotFoundException,
    GroupAlreadyExistsException,
    GroupNotFoundException,
    StudentNotFoundException,
    TeacherNotFoundException,
)
from app.bll.services.department_service import DepartmentService
from app.pl.dependencies import get_department_service
from app.pl.schemas import (
    DepartmentInfoResponse,
    DepartmentInfoUpdate,
    DisciplineCreate,
    DisciplineResponse,
    DisciplineUpdate,
    GroupCreate,
    GroupResponse,
    GroupUpdate,
    StudentCreate,
    StudentResponse,
    StudentUpdate,
    TeacherCreate,
    TeacherResponse,
    TeacherUpdate,
)

router = APIRouter(tags=["department"])


# Department Info
@router.get("/department/info", response_model=DepartmentInfoResponse)
def get_department_info(
    service: DepartmentService = Depends(get_department_service),
):
    return service.get_department_info()


@router.put(
    "/department/info",
    response_model=DepartmentInfoResponse,
    dependencies=[Depends(require_role(["admin"]))],
)
def update_department_info(
    info_data: DepartmentInfoUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    return service.update_department_info(info_data.name, info_data.description)


# Groups
@router.get("/groups", response_model=list[GroupResponse])
def get_groups(service: DepartmentService = Depends(get_department_service)):
    return service.get_groups()


@router.post(
    "/groups",
    response_model=GroupResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def create_group(
    group_data: GroupCreate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.create_group(group_data.name)
    except GroupAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.put(
    "/groups/{group_id}",
    response_model=GroupResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def update_group(
    group_id: int,
    group_data: GroupUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.update_group(group_id, group_data.name)
    except GroupNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except GroupAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.delete(
    "/groups/{group_id}", dependencies=[Depends(require_role(["admin", "manager"]))]
)
def delete_group(
    group_id: int,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        service.delete_group(group_id)
        return {"message": "Group deleted successfully"}
    except GroupNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# Students
@router.get("/students", response_model=list[StudentResponse])
def get_students(service: DepartmentService = Depends(get_department_service)):
    return service.get_students()


@router.post(
    "/students",
    response_model=StudentResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def create_student(
    student_data: StudentCreate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.create_student(student_data.name, student_data.group_id)
    except GroupNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.put(
    "/students/{student_id}",
    response_model=StudentResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.update_student(
            student_id, student_data.name, student_data.group_id
        )
    except (StudentNotFoundException, GroupNotFoundException) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/students/{student_id}", dependencies=[Depends(require_role(["admin", "manager"]))]
)
def delete_student(
    student_id: int,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        service.delete_student(student_id)
        return {"message": "Student deleted successfully"}
    except StudentNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# Teachers
@router.get("/teachers", response_model=list[TeacherResponse])
def get_teachers(service: DepartmentService = Depends(get_department_service)):
    return service.get_teachers()


@router.post(
    "/teachers",
    response_model=TeacherResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def create_teacher(
    teacher_data: TeacherCreate,
    service: DepartmentService = Depends(get_department_service),
):
    return service.create_teacher(
        teacher_data.name, teacher_data.position, teacher_data.discipline_ids
    )


@router.put(
    "/teachers/{teacher_id}",
    response_model=TeacherResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.update_teacher(
            teacher_id,
            teacher_data.name,
            teacher_data.position,
            teacher_data.discipline_ids,
        )
    except TeacherNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.delete(
    "/teachers/{teacher_id}", dependencies=[Depends(require_role(["admin", "manager"]))]
)
def delete_teacher(
    teacher_id: int,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        service.delete_teacher(teacher_id)
        return {"message": "Teacher deleted successfully"}
    except TeacherNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


# Disciplines
@router.get("/disciplines", response_model=list[DisciplineResponse])
def get_disciplines(service: DepartmentService = Depends(get_department_service)):
    return service.get_disciplines()


@router.post(
    "/disciplines",
    response_model=DisciplineResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def create_discipline(
    discipline_data: DisciplineCreate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.create_discipline(
            discipline_data.name, discipline_data.description
        )
    except DisciplineAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.put(
    "/disciplines/{discipline_id}",
    response_model=DisciplineResponse,
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def update_discipline(
    discipline_id: int,
    discipline_data: DisciplineUpdate,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        return service.update_discipline(
            discipline_id, discipline_data.name, discipline_data.description
        )
    except DisciplineNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DisciplineAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@router.delete(
    "/disciplines/{discipline_id}",
    dependencies=[Depends(require_role(["admin", "manager"]))],
)
def delete_discipline(
    discipline_id: int,
    service: DepartmentService = Depends(get_department_service),
):
    try:
        service.delete_discipline(discipline_id)
        return {"message": "Discipline deleted successfully"}
    except DisciplineNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
