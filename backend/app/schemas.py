from pydantic import BaseModel, ConfigDict, Field


class DepartmentInfoBase(BaseModel):
    name: str
    description: str | None = None
    head: str | None = None
    email: str | None = None
    phone: str | None = None


class DepartmentInfoUpdate(BaseModel):
    name: str
    description: str | None = None


class DepartmentInfoResponse(DepartmentInfoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class DisciplineBase(BaseModel):
    name: str
    description: str | None = None


class DisciplineCreate(DisciplineBase):
    pass


class DisciplineUpdate(DisciplineBase):
    pass


class DisciplineResponse(DisciplineBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class GroupBase(BaseModel):
    name: str


class GroupCreate(GroupBase):
    pass


class GroupUpdate(GroupBase):
    pass


class GroupResponse(GroupBase):
    id: int
    student_count: int | None = 0
    model_config = ConfigDict(from_attributes=True)


class StudentBase(BaseModel):
    name: str
    group_id: int


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    pass


class StudentResponse(StudentBase):
    id: int
    group_name: str | None = None
    model_config = ConfigDict(from_attributes=True)


class TeacherBase(BaseModel):
    name: str
    position: str


class TeacherCreate(TeacherBase):
    discipline_ids: list[int] = []


class TeacherUpdate(TeacherBase):
    discipline_ids: list[int] = []


class TeacherResponse(TeacherBase):
    id: int
    discipline_ids: list[int] = []
    model_config = ConfigDict(from_attributes=True)


class GradeBase(BaseModel):
    student_id: int
    discipline_id: int
    teacher_id: int
    grade: int = Field(..., ge=0, le=100)


class GradeCreate(GradeBase):
    pass


class GradeEnsure(BaseModel):
    student_id: int
    discipline_id: int
    teacher_id: int


class GradeUpdate(BaseModel):
    grade: int = Field(..., ge=0, le=100)


class GradeResponse(BaseModel):
    id: int
    student_id: int
    discipline_id: int
    teacher_id: int
    grade: int
    student: str
    subject: str
    teacher: str
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str


class MockLoginRequest(BaseModel):
    role: str
    profile_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    profile_id: int | None = None
    profile_type: str | None = None
    name: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)
