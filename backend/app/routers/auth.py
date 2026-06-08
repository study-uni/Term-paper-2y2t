from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, verify_password
from app.database import get_db
from app.models import Student, Teacher, User
from app.schemas import MockLoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})

    name = user.username
    profile_id = None
    profile_type = None

    if user.role == "admin":
        name = "Адміністратор Системи"
    elif user.role == "manager":
        name = "Менеджер Кафедри"
    elif user.role == "teacher" and user.teacher_id:
        teacher = db.query(Teacher).filter(Teacher.id == user.teacher_id).first()
        if teacher:
            name = teacher.name
            profile_id = teacher.id
            profile_type = "teacher"
    elif user.role == "student" and user.student_id:
        student = db.query(Student).filter(Student.id == user.student_id).first()
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


@router.post("/mock-login", response_model=TokenResponse)
def mock_login(request: MockLoginRequest, db: Session = Depends(get_db)):
    role = request.role
    if role not in ["admin", "manager", "teacher", "student"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid simulator role: {role}",
        )

    user = None
    if role == "admin":
        user = db.query(User).filter(User.role == "admin").first()
    elif role == "manager":
        user = db.query(User).filter(User.role == "manager").first()
    elif role == "teacher":
        if request.profile_id:
            user = (
                db.query(User)
                .filter(User.role == "teacher", User.teacher_id == request.profile_id)
                .first()
            )
        if not user:
            # fallback to first teacher
            user = db.query(User).filter(User.role == "teacher").first()
    elif role == "student":
        if request.profile_id:
            user = (
                db.query(User)
                .filter(User.role == "student", User.student_id == request.profile_id)
                .first()
            )
        if not user:
            # fallback to first student
            user = db.query(User).filter(User.role == "student").first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"No user account found for role '{role}'. "
                "Please make sure data seeding is done."
            ),
        )

    access_token = create_access_token(data={"sub": user.username})

    name = user.username
    profile_id = None
    profile_type = None

    if user.role == "admin":
        name = "Адміністратор Системи"
    elif user.role == "manager":
        name = "Менеджер Кафедри"
    elif user.role == "teacher" and user.teacher_id:
        teacher = db.query(Teacher).filter(Teacher.id == user.teacher_id).first()
        if teacher:
            name = teacher.name
            profile_id = teacher.id
            profile_type = "teacher"
    elif user.role == "student" and user.student_id:
        student = db.query(Student).filter(Student.id == user.student_id).first()
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
