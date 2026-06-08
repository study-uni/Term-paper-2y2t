from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import require_role
from app.database import get_db
from app.models import Discipline, Grade, Student, Teacher, User
from app.schemas import GradeEnsure, GradeResponse, GradeUpdate

router = APIRouter(prefix="/grades", tags=["grades"])


def to_grade_response(grade: Grade) -> GradeResponse:
    # format teacher name
    t_name = grade.teacher.name if grade.teacher else "—"
    parts = t_name.split(" ")
    if len(parts) >= 2:
        short_t = f"{parts[0]} {parts[1][0]}."
        if len(parts) >= 3:
            short_t += f" {parts[2][0]}."
    else:
        short_t = t_name

    return GradeResponse(
        id=grade.id,
        student_id=grade.student_id,
        discipline_id=grade.discipline_id,
        teacher_id=grade.teacher_id,
        grade=grade.grade,
        student=grade.student.name if grade.student else "—",
        subject=grade.discipline.name if grade.discipline else "—",
        teacher=short_t,
    )


@router.get("/my", response_model=list[GradeResponse])
def get_my_grades(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["student"])),
):
    if not current_user.student_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with any student profile"
        )

    grades = db.query(Grade).filter(Grade.student_id == current_user.student_id).all()
    return [to_grade_response(g) for g in grades]


@router.get("/journal", response_model=list[GradeResponse])
def get_teacher_journal(
    discipline_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["teacher"])),
):
    if not current_user.teacher_id:
        raise HTTPException(
            status_code=400, detail="User is not associated with any teacher profile"
        )

    teacher = db.query(Teacher).filter(Teacher.id == current_user.teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")

    target_discipline_ids = []
    if discipline_id:
        if discipline_id not in [d.id for d in teacher.disciplines]:
            raise HTTPException(
                status_code=403, detail="You do not teach this discipline"
            )
        target_discipline_ids = [discipline_id]
    else:
        target_discipline_ids = [d.id for d in teacher.disciplines]

    # initialize empty grades for teacher's disciplines
    students = db.query(Student).all()
    for s in students:
        for d_id in target_discipline_ids:
            exists = (
                db.query(Grade)
                .filter(
                    Grade.student_id == s.id,
                    Grade.discipline_id == d_id,
                    Grade.teacher_id == teacher.id,
                )
                .first()
            )
            if not exists:
                new_grade = Grade(
                    student_id=s.id, discipline_id=d_id, teacher_id=teacher.id, grade=0
                )
                db.add(new_grade)
    db.commit()

    grades_query = db.query(Grade).filter(Grade.teacher_id == teacher.id)
    if discipline_id:
        grades_query = grades_query.filter(Grade.discipline_id == discipline_id)
    else:
        grades_query = grades_query.filter(
            Grade.discipline_id.in_(target_discipline_ids)
        )

    grades = grades_query.all()
    return [to_grade_response(g) for g in grades]


@router.post("/ensure", response_model=GradeResponse)
def ensure_grade(
    req: GradeEnsure,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager", "teacher"])),
):
    student = db.query(Student).filter(Student.id == req.student_id).first()
    discipline = db.query(Discipline).filter(Discipline.id == req.discipline_id).first()
    teacher = db.query(Teacher).filter(Teacher.id == req.teacher_id).first()
    if not student or not discipline or not teacher:
        raise HTTPException(
            status_code=404, detail="Student, Discipline or Teacher not found"
        )

    grade = (
        db.query(Grade)
        .filter(
            Grade.student_id == req.student_id,
            Grade.discipline_id == req.discipline_id,
            Grade.teacher_id == req.teacher_id,
        )
        .first()
    )

    if not grade:
        grade = Grade(
            student_id=req.student_id,
            discipline_id=req.discipline_id,
            teacher_id=req.teacher_id,
            grade=0,
        )
        db.add(grade)
        db.commit()
        db.refresh(grade)

    return to_grade_response(grade)


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade(
    grade_id: int,
    req: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "manager", "teacher"])),
):
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        raise HTTPException(status_code=404, detail="Grade record not found")

    # check teacher permission
    if current_user.role == "teacher" and grade.teacher_id != current_user.teacher_id:
        raise HTTPException(
            status_code=403, detail="You can only edit grades you issued"
        )

    grade.grade = req.grade
    db.commit()
    db.refresh(grade)
    return to_grade_response(grade)
