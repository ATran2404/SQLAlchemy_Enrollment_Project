from orm_base import Base
from db_connection import engine
from IntrospectionFactory import IntrospectionFactory
from sqlalchemy import UniqueConstraint, ForeignKeyConstraint, Enum, CheckConstraint
from sqlalchemy import String, Integer
from sqlalchemy import Time
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from sqlalchemy import Table
from constants import START_OVER, REUSE_NO_INTROSPECTION, INTROSPECT_TABLES
from enum import Enum as PythonEnum
from typing import List
from Enrollment import Enrollment
from Course import Course
table_name: str = "sections"  # The physical name of this table
# Find out whether the user is introspecting or starting over
introspection_type = IntrospectionFactory().introspection_type
if introspection_type == START_OVER or introspection_type == REUSE_NO_INTROSPECTION:
    class Section(Base):
        __tablename__ = table_name
        department_abbreviation: Mapped[str] = mapped_column('department_abbreviation', String(10), nullable=False,
                                                             primary_key=True)

        course_number: Mapped[int] = mapped_column('course_number', Integer, nullable=False, primary_key=True)
        section_number: Mapped[int] = mapped_column('section_number', Integer, primary_key=True)

        semester: Mapped[str] = mapped_column('semester', String(10), CheckConstraint("semester IN('Fall', 'Spring', 'Winter',\
 'Summer I', 'Summer II', 'Summer III')", name="sections_semester_constraint"), primary_key=True)
        section_year: Mapped[int] = mapped_column('section_year', Integer, nullable=False, primary_key=True)

        class Building(PythonEnum):
            VEC = 'VEC'
            ECS = 'ECS'
            EN2 = 'EN2'
            EN3 = 'EN3'
            EN4 = 'EN4'
            ET = 'ET'
            SSPA = 'SSPA'

        building: Mapped[str] = mapped_column('building', Enum(Building), nullable=False)
        room: Mapped[int] = mapped_column('room', Integer, nullable=False)

        class Schedule(PythonEnum):
            MW = 'MW'
            TuTh = 'TuTh'
            MWF = 'MWF'
            F = 'F'
            S = 'S'

        schedule: Mapped[str] = mapped_column('schedule', Enum(Schedule), nullable=False)
        start_time: Mapped["Time"] = mapped_column('start_time', Time, nullable=False)
        instructor: Mapped[str] = mapped_column('instructor', String(80), nullable=False)

        __table_args__ = (
            UniqueConstraint('section_year', 'semester', 'department_abbreviation', 'course_number', 'section_number',
                             name="sections_uk_03"),
            UniqueConstraint('section_year', 'semester', 'schedule', 'start_time', 'building', 'room',
                             name="sections_uk_01"),
            UniqueConstraint('section_year', 'semester', 'schedule', 'start_time', 'instructor', name="sections_uk_02"),
            ForeignKeyConstraint([department_abbreviation, course_number],
                                 [Course.departmentAbbreviation, Course.courseNumber])
        )

        courses: Mapped["Course"] = relationship(back_populates="sections")

        students: Mapped[List["Enrollment"]] = relationship(back_populates="sections",
                                                            cascade="all, save-update, delete-orphan")

        def __init__(self, course: Course, section_number: int,
                     semester: str, section_year: int, building: str, room: int, schedule: str, start_time: Time,
                     instructor: str):
            self.set_course(course)
            self.section_number = section_number
            self.semester = semester
            self.section_year = section_year
            self.building = building
            self.room = room
            self.schedule = schedule
            self.start_time = start_time
            self.instructor = instructor
elif introspection_type == INTROSPECT_TABLES:

    class Section(Base):
        __table__ = Table(table_name, Base.metadata, autoload_with=engine)
        # Otherwise, this property will be named department_abbreviation
        department_abbreviation: Mapped[str] = column_property(__table__.c.department_abbreviation)
        # This back_populates will not be created by the introspection.
        departments: Mapped["Course"] = relationship(back_populates="sections")
        # Otherwise, this property will be named course_number
        courseNumber: Mapped[int] = column_property(__table__.c.course_number)
        students: Mapped[List["Enrollment"]] = relationship(back_populates="sections",
                                                            cascade="all, save-update, delete-orphan")
        courses: Mapped["Course"] = relationship(back_populates="sections")
        section_number: Mapped[int] = column_property(__table__.c.course_number)

        def __init__(self, department_abbreviation: str, course_number: str, section_number: int,
                     semester: str, section_year: int, building: str, room: int, schedule: str, start_time: Time,
                     instructor: str):
            self.department_abbreviation = department_abbreviation
            self.course_number = course_number
            self.section_number = section_number
            self.semester = semester
            self.section_year = section_year
            self.building = building
            self.room = room
            self.schedule = schedule
            self.start_time = start_time
            self.instructor = instructor


def set_course(self, course: Course):
    """
    Accept a new department withoug checking for any uniqueness.
    I'm going to assume that either a) the caller checked that first
    and/or b) the database will raise its own exception.
    :param course:  The new department for the course.
    :return:            None
    """
    self.course = course
    self.department_abbreviation = course.departmentAbbreviation
    self.course_number = course.courseNumber


def add_student(self, student):
    """Add a new student to the list of students in the major.  We are not adding a
    Student per se, but rather creating an instance of StudentMajor, and adding that
    new instance to our list of "students".  A parallel construct will exist on the
    Student side to manage instances of StudentMajor to keep track of the various
    major(s) that the student has.
    """
    # Make sure that this Major does not already have this Student.
    for next_student in self.students:
        if next_student.students == student:
            return  # This student is already in this major.
    # create the necessary Association Class instance that connects This major to
    # the supplied student.
    student_major = Enrollment(self, student)


def remove_student(self, student):
    """Remove a student from this major, and remove this major from that student.
    :param student:     The Student to be removed from this major.
    :return:            None
    """
    for next_student in self.students:
        if next_student.students == student:
            # Remove this major from the student's list of majors.
            self.students.remove(next_student)
            return True
    return False


def __str__(self):
    return f"Section {self.department_abbreviation} {self.course_number}-{self.section_number} ({self.semester} {self.section_year})"


"""Add the two instance methods to the class, regardless of whether we introspect or not."""
setattr(Section, 'set_course', set_course)
setattr(Section, 'add_student', add_student)
setattr(Section, 'remove_student', remove_student)
setattr(Section, '__str__', __str__)
