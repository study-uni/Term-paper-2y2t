from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models import DepartmentInfo, Discipline, Group, Student, Teacher, User
from app.schemas import (
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


def to_student_response(student: Student) -> StudentResponse:
    return StudentResponse(
        id=student.id,
        name=student.name,
        group_id=student.group_id,
        group_name=student.group.name if student.group else "—",
    )


def to_teacher_response(teacher: Teacher) -> TeacherResponse:
    return TeacherResponse(
        id=teacher.id,
        name=teacher.name,
        position=teacher.position,
        discipline_ids=[d.id for d in teacher.disciplines],
    )


@router.get("/department/info", response_model=DepartmentInfoResponse)
def get_department_info(db: Session = Depends(get_db)):
    info = db.query(DepartmentInfo).filter(DepartmentInfo.id == 1).first()
    if not info:
        info = DepartmentInfo(id=1, name="Кафедра", description="")
        db.add(info)
        db.commit()
        db.refresh(info)
    return info


@router.put("/department/info", response_model=DepartmentInfoResponse)
def update_department_info(
    info_data: DepartmentInfoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"])),
):
    info = db.query(DepartmentInfo).filter(DepartmentInfo.id == 1).first()
    if not info:
        info = DepartmentInfo(id=1)
        db.add(info)

    info.name = info_data.name
    info.description = info_data.description
    db.commit()
    db.refresh(info)
    return info


@router.get("/groups", response_model=list[GroupResponse])
def get_groups(db: Session = Depends(get_db)):
    groups = db.query(Group).order_by(Group.name).all()

    response = []
    for g in groups:
        count = db.query(Student).filter(Student.group_id == g.id).count()
        response.append(GroupResponse(id=g.id, name=g.name, student_count=count))
    return response


@router.post("/groups", response_model=GroupResponse)
def create_group(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    existing = db.query(Group).filter(Group.name == group_data.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Group with this name already exists"
        )

    group = Group(name=group_data.name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return GroupResponse(id=group.id, name=group.name, student_count=0)


@router.put("/groups/{group_id}", response_model=GroupResponse)
def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    existing = (
        db.query(Group)
        .filter(Group.name == group_data.name, Group.id != group_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Group with this name already exists"
        )

    group.name = group_data.name
    db.commit()
    db.refresh(group)
    count = db.query(Student).filter(Student.group_id == group.id).count()
    return GroupResponse(id=group.id, name=group.name, student_count=count)


@router.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()
    return {"message": "Group deleted successfully"}


@router.get("/students", response_model=list[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    students = db.query(Student).order_by(Student.name).all()
    return [to_student_response(s) for s in students]


@router.post("/students", response_model=StudentResponse)
def create_student(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    group = db.query(Group).filter(Group.id == student_data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    student = Student(name=student_data.name, group_id=student_data.group_id)
    db.add(student)
    db.commit()
    db.refresh(student)

    # create student simulator user
    username = student.name.lower().replace(" ", "_")
    base_username = username
    idx = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{idx}"
        idx += 1

    from app.auth import get_password_hash

    hashed_pwd = get_password_hash("studentpassword")
    new_user = User(
        username=username,
        hashed_password=hashed_pwd,
        role="student",
        student_id=student.id,
    )
    db.add(new_user)
    db.commit()

    return to_student_response(student)


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    group = db.query(Group).filter(Group.id == student_data.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    student.name = student_data.name
    student.group_id = student_data.group_id
    db.commit()
    db.refresh(student)
    return to_student_response(student)


@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    user = db.query(User).filter(User.student_id == student_id).first()
    if user:
        db.delete(user)

    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}


@router.get("/teachers", response_model=list[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
    teachers = db.query(Teacher).order_by(Teacher.name).all()
    return [to_teacher_response(t) for t in teachers]


@router.post("/teachers", response_model=TeacherResponse)
def create_teacher(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    teacher = Teacher(name=teacher_data.name, position=teacher_data.position)

    if teacher_data.discipline_ids:
        disciplines = (
            db.query(Discipline)
            .filter(Discipline.id.in_(teacher_data.discipline_ids))
            .all()
        )
        teacher.disciplines = disciplines

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    # create teacher simulator user
    username = teacher.name.lower().replace(" ", "_")
    base_username = username
    idx = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{idx}"
        idx += 1

    from app.auth import get_password_hash

    hashed_pwd = get_password_hash("teacherpassword")
    new_user = User(
        username=username,
        hashed_password=hashed_pwd,
        role="teacher",
        teacher_id=teacher.id,
    )
    db.add(new_user)
    db.commit()

    return to_teacher_response(teacher)


@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    teacher.name = teacher_data.name
    teacher.position = teacher_data.position

    if teacher_data.discipline_ids is not None:
        disciplines = (
            db.query(Discipline)
            .filter(Discipline.id.in_(teacher_data.discipline_ids))
            .all()
        )
        teacher.disciplines = disciplines

    db.commit()
    db.refresh(teacher)
    return to_teacher_response(teacher)


@router.delete("/teachers/{teacher_id}")
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    user = db.query(User).filter(User.teacher_id == teacher_id).first()
    if user:
        db.delete(user)

    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}


@router.get("/disciplines", response_model=list[DisciplineResponse])
def get_disciplines(db: Session = Depends(get_db)):
    disciplines = db.query(Discipline).order_by(Discipline.name).all()
    return disciplines


@router.post("/disciplines", response_model=DisciplineResponse)
def create_discipline(
    discipline_data: DisciplineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    existing = (
        db.query(Discipline).filter(Discipline.name == discipline_data.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Discipline with this name already exists"
        )

    discipline = Discipline(
        name=discipline_data.name, description=discipline_data.description
    )
    db.add(discipline)
    db.commit()
    db.refresh(discipline)
    return discipline


@router.put("/disciplines/{discipline_id}", response_model=DisciplineResponse)
def update_discipline(
    discipline_id: int,
    discipline_data: DisciplineUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    discipline = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")

    existing = (
        db.query(Discipline)
        .filter(Discipline.name == discipline_data.name, Discipline.id != discipline_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Discipline with this name already exists"
        )

    discipline.name = discipline_data.name
    discipline.description = discipline_data.description
    db.commit()
    db.refresh(discipline)
    return discipline


@router.delete("/disciplines/{discipline_id}")
def delete_discipline(
    discipline_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager"])),
):
    discipline = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    db.delete(discipline)
    db.commit()
    return {"message": "Discipline deleted successfully"}
