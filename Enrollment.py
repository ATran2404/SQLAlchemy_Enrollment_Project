from orm_base import Base
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, String, Integer, Enum, Identity, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum as PythonEnum


# We canNOT import Student and Major here because Student and Major
# are both importing StudentMajor.  So we have to go without the
# ability to validate the Student or Major class references in
# this class.  Otherwise, we get a circular import.
# from Student import Student
# from Major import Major


class Enrollment(Base):
    """The association class between Student and Major.  I resorted to using
    this style of implementing a Many to Many because I feel that it is the
    most versatile approach, and we only have time for one Many to Many
    protocol in this class."""
    __tablename__ = "enrollments"
    enrollmentId: Mapped[int] = mapped_column('enrollment_id', Integer, Identity(start=1, cycle=True),
                                              primary_key=True)
    sections: Mapped["Section"] = relationship(back_populates="students")
    students: Mapped["Student"] = relationship(back_populates="sections")
    studentId: Mapped[int] = mapped_column("student_id", ForeignKey("students.student_id"),
                                           nullable=False)

    department_abbreviation: Mapped[str] = \
        mapped_column('department_abbreviation', String(10), nullable=False)
    # department_abbreviation, course_number, section_year, semester
    course_number: Mapped[str] = \
        mapped_column('course_number', Integer, nullable=False)
    section_number: Mapped[str] = \
        mapped_column('section_number', Integer, nullable=False)
    section_year: Mapped[str] = \
        mapped_column('section_year', Integer, nullable=False)

    class Semester(PythonEnum):
        Fall = 'Fall'
        Spring = 'Spring'
        Winter = 'Winter'
        Summer1 = 'Summer1'
        Summer2 = 'Summer2'

    semester: Mapped[str] = \
        mapped_column('semester', String(10), nullable=False)
    type: Mapped[str] = mapped_column("type", String(50), nullable=False)

    __table_args__ = (UniqueConstraint("department_abbreviation", "course_number",
                                       "section_number", "section_year", "semester",
                                       "student_id", name="enrollment_uk_01"),
                      ForeignKeyConstraint(["department_abbreviation", "course_number",
                                            "section_number", "semester", "section_year"],
                                           ["sections.department_abbreviation",
                                            "sections.course_number", "sections.section_number",
                                            "sections.semester", "sections.section_year"],
                                           name="enrollments_sections_fk_01"),)

    __mapper_args__ = {"polymorphic_identity": "enrollment",
                       "polymorphic_on": "type"}

    def __init__(self, sections, students):
        self.students = students
        self.sections = sections
        self.studentId = students.studentID
        self.department_abbreviation = sections.department_abbreviation
        self.course_number = sections.course_number
        self.section_number = sections.section_number
        self.section_year = sections.section_year
        self.semester = sections.semester

    def __str__(self):
        return f"{self.students}. Section: {self.sections}"
