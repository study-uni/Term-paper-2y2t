from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.models import DepartmentInfo, Discipline, Grade, Group, Student, Teacher, User


def seed_db(db: Session):
    if db.query(User).first() is not None:
        print("Database already seeded.")
        return

    print("Seeding database with default academic data...")

    dept_info = DepartmentInfo(
        id=1,
        name="Кафедра програмної інженерії",
        description=(
            "Кафедра здійснює підготовку бакалаврів та магістрів "
            "зі спеціальності «Програмна інженерія». Навчання включає "
            "сучасні технології веб-розробки, архітектури ПЗ та "
            "проєктування баз даних."
        ),
        head="Прокопенко Андрій Васильович",
        email="software@university.edu.ua",
        phone="+38 (044) 000-00-00",
    )
    db.add(dept_info)

    d1 = Discipline(
        id=1, name="Веб-програмування", description="HTML, CSS, JavaScript, Vue.js"
    )
    d2 = Discipline(
        id=2, name="Архітектура ПЗ", description="Патерни проєктування, UML, SOLID"
    )
    d3 = Discipline(id=3, name="Бази даних", description="SQL, нормалізація, ORM")
    db.add_all([d1, d2, d3])
    db.flush()

    g1 = Group(id=1, name="Б-121-24-3")
    g2 = Group(id=2, name="Б-121-24-4")
    db.add_all([g1, g2])
    db.flush()

    t1 = Teacher(id=1, name="Прокопенко Андрій Васильович", position="Професор")
    t2 = Teacher(id=2, name="Рудий Іван Володимирович", position="Асистент")
    t3 = Teacher(id=3, name="Сидоренко Олена Миколаївна", position="Доцент")

    # associate disciplines
    t1.disciplines = [d1, d2]
    t2.disciplines = [d2]
    t3.disciplines = [d3]

    db.add_all([t1, t2, t3])
    db.flush()

    s1 = Student(id=1, name="Рудий Іван Володимирович", group_id=1)
    s2 = Student(id=2, name="Коваленко Олег Петрович", group_id=1)
    s3 = Student(id=3, name="Сидоров Дмитро Сергійович", group_id=2)
    db.add_all([s1, s2, s3])
    db.flush()

    grades = [
        Grade(id=1, student_id=1, discipline_id=1, teacher_id=1, grade=95),
        Grade(id=2, student_id=1, discipline_id=2, teacher_id=1, grade=88),
        Grade(id=3, student_id=1, discipline_id=3, teacher_id=3, grade=74),
        Grade(id=4, student_id=2, discipline_id=1, teacher_id=1, grade=82),
        Grade(id=5, student_id=3, discipline_id=1, teacher_id=1, grade=61),
    ]
    db.add_all(grades)
    db.flush()

    users = [
        User(
            username="admin",
            hashed_password=get_password_hash("adminpassword"),
            role="admin",
        ),
        User(
            username="manager",
            hashed_password=get_password_hash("managerpassword"),
            role="manager",
        ),
        User(
            username="andrii_prokopenko",
            hashed_password=get_password_hash("teacherpassword"),
            role="teacher",
            teacher_id=1,
        ),
        User(
            username="ivan_rudyi",
            hashed_password=get_password_hash("teacherpassword"),
            role="teacher",
            teacher_id=2,
        ),
        User(
            username="olena_sydorenko",
            hashed_password=get_password_hash("teacherpassword"),
            role="teacher",
            teacher_id=3,
        ),
        User(
            username="ivan_rudyi_stud",
            hashed_password=get_password_hash("studentpassword"),
            role="student",
            student_id=1,
        ),
        User(
            username="oleh_kovalenko",
            hashed_password=get_password_hash("studentpassword"),
            role="student",
            student_id=2,
        ),
        User(
            username="dmytro_sydorov",
            hashed_password=get_password_hash("studentpassword"),
            role="student",
            student_id=3,
        ),
    ]
    db.add_all(users)
    db.commit()
    print("Database seeding completed successfully.")
