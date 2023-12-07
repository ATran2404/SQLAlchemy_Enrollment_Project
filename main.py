import logging
from constants import *
from datetime import time, datetime
from menu_definitions import menu_main, add_menu, delete_menu, list_menu, debug_select, introspection_select
from IntrospectionFactory import IntrospectionFactory
from db_connection import engine, Session
from orm_base import metadata
# Note that until you import your SQLAlchemy declarative classes, such as Student, Python
# will not execute that code, and SQLAlchemy will be unaware of the mapped table.
from Department import Department
from Course import Course
from Major import Major
from Student import Student
from StudentMajor import StudentMajor
from Enrollment import Enrollment
from Section import Section
from Option import Option
from Menu import Menu
from sqlalchemy.sql import and_
from PassFail import PassFail
from LetterGrade import LetterGrade

def add(sess: Session):
    add_action: str = ''
    while add_action != add_menu.last_action():
        add_action = add_menu.menu_prompt()
        exec(add_action)


def delete(sess: Session):
    delete_action: str = ''
    while delete_action != delete_menu.last_action():
        delete_action = delete_menu.menu_prompt()
        exec(delete_action)


def list_objects(sess: Session):
    list_action: str = ''
    while list_action != list_menu.last_action():
        list_action = list_menu.menu_prompt()
        exec(list_action)


def add_department(session: Session):
    """
    Prompt the user for the information for a new Department and validate
    the input to make sure that we do not create any duplicates .
    :param session: The connection to the database.
    :return:        None
    """
    unique: bool = False
    name: str = ''
    abbreviation: str = ''
    chair_name: str = ''
    building: str = ''
    office: int = 0
    description: str = ''
    # Make sure new department is uniqueness constraints
    while not unique:
        name = input("Department name--> ")
        abbreviation = input("Department abbreviation--> ")
        chair_name = input("Department chair--> ")
        building = input("Department building--> ")
        office = input("Department office--> ")
        description = input("Department description--> ")

        unique_name: str = sess.query(Department).filter(Department.name == name).first()
        if unique_name is not None:
            print("We already have a department with that name.  Try again.")
        else:
            unique_abbreviation: str = sess.query(Department).filter(Department.abbreviation == abbreviation).first()
            if unique_abbreviation is not None:
                print("We already have a department with that abbreviation.  Try again.")
            else:
                unique_chair_name: str = sess.query(Department).filter(Department.chair_name == chair_name).first()
                if unique_chair_name is not None:
                    print("We already have a Department with that chair.  Try again.")
                else:
                    unique_room: int = sess.query(Department).filter(Department.building == building,
                                                                     Department.office == office).count()
                    if unique_room != 0:
                        print("We already have a department with that room.  Try again.")
                    else:
                        unique_description: str = sess.query(Department).filter(
                            Department.description == description).first()
                        if unique_description is not None:
                            print("We already have a Department with that description.  Try again.")
                        else:
                            unique = True

    newDepartment = Department(name, abbreviation, chair_name, building, office, description)
    session.add(newDepartment)


def add_course(session: Session):
    """
    Prompt the user for the information for a new course and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    print("Which department offers this course?")
    department: Department = select_department(sess)
    unique_number: bool = False
    unique_name: bool = False
    number: int = -1
    name: str = ''
    while not unique_number or not unique_name:
        name = input("Course full name--> ")
        number = int(input("Course number--> "))
        name_count: int = session.query(Course).filter(Course.departmentAbbreviation == department.abbreviation,
                                                       Course.name == name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a course by that name in that department.  Try again.")
        if unique_name:
            number_count = session.query(Course). \
                filter(Course.departmentAbbreviation == department.abbreviation,
                       Course.courseNumber == number).count()
            unique_number = number_count == 0
            if not unique_number:
                print("We already have a course in this department with that number.  Try again.")
    description: str = input('Please enter the course description-->')
    units: int = int(input('How many units for this course-->'))
    course = Course(department, number, name, description, units)
    session.add(course)


def add_section(session):
    # Primary key: {department_abbreviation, course_number, section_number, section_year,
    #       semester}
    print("Which department offers this course?")
    course: Course = select_course(sess)

    unique_section: bool = False
    unique_room: bool = False
    unique_instructor: bool = False
    section_number: int = -1
    semester: str = ''  # Find a way to make sure that this never takes on a value other than (‘Fall’, ‘Spring’,
    # ‘Winter’, ‘Summer I’, ‘Summer II’
    section_year: int = -1
    building: str = ''  # Make sure that the database will only accept a value for building from the list: {VEC, ECS,
    # EN2, EN3, EN4, ET and SSPA
    room: int = -1
    schedule: str = ''  # Make sure that this only takes on one of the values: (‘MW’, ‘TuTh’, ‘MWF’, ‘F’, ‘S’)
    start_time: str = ''
    instructor: str = ''

    while not unique_room or not unique_instructor or not unique_section:

        section_number = input("Section Number--> ")
        semester = input("Semester--> ")
        section_year = input("Section year--> ")
        building = input("Building--> ")
        room = input("Room--> ")
        schedule = input("Schedule--> ")
        start_time = input("Start time--> ")
        instructor = input("Instructor--> ")

        name_count: int = session.query(Section). \
            filter(Section.department_abbreviation == course.departmentAbbreviation,
                   Section.course_number == course.courseNumber,
                   Section.section_number == section_number,
                   Section.semester == semester,
                   Section.section_year == section_year).count()

        room_count: int = session.query(Section).filter(Section.section_year == section_year,
                                                        Section.semester == semester,
                                                        Section.schedule == schedule,
                                                        Section.start_time == start_time,
                                                        Section.building == building,
                                                        Section.room == room).count()

        instructor_count: int = session.query(Section).filter(Section.section_year == section_year,
                                                              Section.semester == semester,
                                                              Section.schedule == schedule,
                                                              Section.start_time == start_time,
                                                              Section.instructor == instructor).count()

        unique_section = name_count == 0
        unique_room = room_count == 0
        unique_instructor = instructor_count == 0
        if not unique_section:
            print("We already have a section in that department at that semester.  Try again.")
        elif not unique_room:
            print("We already have a class in that room at that time.  Try again.")
        elif not unique_instructor:
            print("We already have an instructor work at that time.  Try again.")
    section = Section(course, section_number, semester, section_year,
                      building, room, schedule, start_time, instructor)
    session.add(section)


def add_major(session: Session):
    """
    Prompt the user for the information for a new major and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    print("Which department offers this major?")
    department: Department = select_department(sess)
    unique_name: bool = False
    name: str = ''
    while not unique_name:
        name = input("Major name--> ")
        name_count: int = session.query(Major).filter(Major.departmentAbbreviation == department.abbreviation,
                                                      Major.name == name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a major by that name in that department.  Try again.")
    description: str = input('Please give this major a description -->')
    major: Major = Major(department, name, description)
    session.add(major)


def add_student(session: Session):
    """
    Prompt the user for the information for a new student and validate
    the input to make sure that we do not create any duplicates.
    :param session: The connection to the database.
    :return:        None
    """
    unique_name: bool = False
    unique_email: bool = False
    last_name: str = ''
    first_name: str = ''
    email: str = ''
    while not unique_email or not unique_name:
        last_name = input("Student last name--> ")
        first_name = input("Student first name-->")
        email = input("Student e-mail address--> ")
        name_count: int = session.query(Student).filter(Student.lastName == last_name,
                                                        Student.firstName == first_name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a student by that name.  Try again.")
        if unique_name:
            email_count = session.query(Student).filter(Student.email == email).count()
            unique_email = email_count == 0
            if not unique_email:
                print("We already have a student with that email address.  Try again.")
    new_student = Student(last_name, first_name, email)
    session.add(new_student)


def add_student_section(sess):
    unique_student_section: bool = False
    while not unique_student_section:
        student: Student = select_student(sess)
        section: Section = select_section(sess)
        student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentID,
                                                                   Enrollment.department_abbreviation == section.department_abbreviation,
                                                                   Enrollment.course_number == section.course_number,
                                                                   Enrollment.section_number == section.section_number,
                                                                   Enrollment.section_year == section.section_year,
                                                                   Enrollment.semester == section.semester).count()
        unique_student_section = student_section_count == 0
        if not unique_student_section:
            print("That course section already has that student.  Try again.")
    else:
        student.add_section(section)
    """The student object instance is mapped to a specific row in the Student table.  But adding
    the new major to its list of majors does not add the new StudentMajor instance to this session.
    That StudentMajor instance was created and added to the Student's majors list inside of the
    add_major method, but we don't have easy access to it from here.  And I don't want to have to 
    pass sess to the add_major method.  So instead, I add the student to the session.  You would
    think that would cause an insert, but SQLAlchemy is smart enough to know that this student 
    has already been inserted, so the add method takes this to be an update instead, and adds
    the new instance of StudentMajor to the session.  THEN, when we flush the session, that 
    transient instance of StudentMajor gets inserted into the database, and is ready to be 
    committed later (which happens automatically when we exit the application)."""
    sess.add(student)  # add the StudentSection to the session
    sess.flush()


def add_section_student(sess):
    unique_student_section: bool = False
    while not unique_student_section:
        section: Section = select_section(sess)
        student: Student = select_student(sess)
        student_section_count: int = sess.query(Enrollment).filter(Enrollment.studentId == student.studentID,
                                                                   Enrollment.department_abbreviation == section.department_abbreviation,
                                                                   Enrollment.course_number == section.course_number,
                                                                   Enrollment.section_number == section.section_number,
                                                                   Enrollment.section_year == section.section_year,
                                                                   Enrollment.semester == section.semester).count()
        unique_student_section = student_section_count == 0
        if not unique_student_section:
            print("That course section already has that student.  Try again.")
        else:
            section.add_student(student)
    """The major object instance is mapped to a specific row in the Major table.  But adding
    the new student to its list of students does not add the new StudentMajor instance to this session.
    That StudentMajor instance was created and added to the Major's students list inside of the
    add_student method, but we don't have easy access to it from here.  And I don't want to have to 
    pass sess to the add_student method.  So instead, I add the major to the session.  You would
    think that would cause an insert, but SQLAlchemy is smart enough to know that this major 
    has already been inserted, so the add method takes this to be an update instead, and adds
    the new instance of StudentMajor to the session.  THEN, when we flush the session, that 
    transient instance of StudentMajor gets inserted into the database, and is ready to be 
    committed later (which happens automatically when we exit the application)."""
    sess.add(section)  # add the StudentMajor to the session
    sess.flush()


def add_student_major(sess):
    student: Student = select_student(sess)
    major: Major = select_major(sess)
    student_major_count: int = sess.query(StudentMajor).filter(StudentMajor.studentId == student.studentID,
                                                               StudentMajor.majorName == major.name).count()
    unique_student_major: bool = student_major_count == 0
    while not unique_student_major:
        print("That student already has that major.  Try again.")
        student = select_student(sess)
        major = select_major(sess)
    student.add_major(major)
    """The student object instance is mapped to a specific row in the Student table.  But adding
    the new major to its list of majors does not add the new StudentMajor instance to this session.
    That StudentMajor instance was created and added to the Student's majors list inside of the
    add_major method, but we don't have easy access to it from here.  And I don't want to have to 
    pass sess to the add_major method.  So instead, I add the student to the session.  You would
    think that would cause an insert, but SQLAlchemy is smart enough to know that this student 
    has already been inserted, so the add method takes this to be an update instead, and adds
    the new instance of StudentMajor to the session.  THEN, when we flush the session, that 
    transient instance of StudentMajor gets inserted into the database, and is ready to be 
    committed later (which happens automatically when we exit the application)."""
    sess.add(student)  # add the StudentMajor to the session
    sess.flush()


def add_major_student(sess):
    major: Major = select_major(sess)
    student: Student = select_student(sess)
    student_major_count: int = sess.query(StudentMajor).filter(StudentMajor.studentId == student.studentID,
                                                               StudentMajor.majorName == major.name).count()
    unique_student_major: bool = student_major_count == 0
    while not unique_student_major:
        print("That major already has that student.  Try again.")
        major = select_major(sess)
        student = select_student(sess)
    major.add_student(student)
    """The major object instance is mapped to a specific row in the Major table.  But adding
    the new student to its list of students does not add the new StudentMajor instance to this session.
    That StudentMajor instance was created and added to the Major's students list inside of the
    add_student method, but we don't have easy access to it from here.  And I don't want to have to 
    pass sess to the add_student method.  So instead, I add the major to the session.  You would
    think that would cause an insert, but SQLAlchemy is smart enough to know that this major 
    has already been inserted, so the add method takes this to be an update instead, and adds
    the new instance of StudentMajor to the session.  THEN, when we flush the session, that 
    transient instance of StudentMajor gets inserted into the database, and is ready to be 
    committed later (which happens automatically when we exit the application)."""
    sess.add(major)  # add the StudentMajor to the session
    sess.flush()


def select_department(sess: Session) -> Department:
    """
    Prompt the user for a specific department by the department abbreviation.
    :param sess:    The connection to the database.
    :return:        The selected department.
    """
    found: bool = False
    abbreviation: str = ''
    while not found:
        abbreviation = input("Enter the department abbreviation--> ")
        abbreviation_count: int = sess.query(Department). \
            filter(Department.abbreviation == abbreviation).count()
        found = abbreviation_count == 1
        if not found:
            print("No department with that abbreviation.  Try again.")
    return_department: Department = sess.query(Department). \
        filter(Department.abbreviation == abbreviation).first()
    return return_department


def select_section(sess) -> Section:
    found: bool = False
    department_abbreviation: str = ''
    course_number: int = -1
    section_number: int = -1
    semester: str = ''
    section_year: int = -1

    while not found:
        department_abbreviation = input("Enter the department abbreviation--> ")
        course_number = int(input("Course Number--> "))
        section_number = int(input("Section Number--> "))
        semester = input("Semester--> ")
        section_year = int(input("Section Year--> "))
        name_count: int = sess.query(Section).filter(Section.department_abbreviation == department_abbreviation,
                                                     Section.course_number == course_number,
                                                     Section.section_number == section_number,
                                                     Section.section_year == section_year,
                                                     Section.semester == semester).count()
        found = name_count == 1
        if not found:
            print("No section in that course.  Try again.")

    return_section: Section = sess.query(Section).filter(Section.department_abbreviation == department_abbreviation,
                                                         Section.course_number == course_number,
                                                         Section.section_number == section_number,
                                                         Section.semester == semester,
                                                         Section.section_year == section_year).first()
    return return_section


def select_course(sess: Session) -> Course:
    """
    Select a course by the combination of the department abbreviation and course number.
    Note, a similar query would be to select the course on the basis of the department
    abbreviation and the course name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    department_abbreviation: str = ''
    course_number: int = -1
    while not found:
        department_abbreviation = input("Department abbreviation--> ")
        course_number = int(input("Course Number--> "))
        name_count: int = sess.query(Course).filter(Course.departmentAbbreviation == department_abbreviation,
                                                    Course.courseNumber == course_number).count()
        found = name_count == 1
        if not found:
            print("No course by that number in that department.  Try again.")
    return_course: Course = sess.query(Course).filter(Course.departmentAbbreviation == department_abbreviation,
                                                      Course.courseNumber == course_number).first()
    return return_course


def select_student(sess) -> Student:
    """
    Select a student by the combination of the last and first.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    last_name: str = ''
    first_name: str = ''
    while not found:
        last_name = input("Student's last name--> ")
        first_name = input("Student's first name--> ")
        name_count: int = sess.query(Student).filter(Student.lastName == last_name,
                                                     Student.firstName == first_name).count()
        found = name_count == 1
        if not found:
            print("No student found by that name.  Try again.")
    student: Student = sess.query(Student).filter(Student.lastName == last_name,
                                                  Student.firstName == first_name).first()
    return student


def select_major(sess) -> Major:
    """
    Select a major by its name.
    :param sess:    The connection to the database.
    :return:        The selected student.
    """
    found: bool = False
    name: str = ''
    while not found:
        name = input("Major's name--> ")
        name_count: int = sess.query(Major).filter(Major.name == name).count()
        found = name_count == 1
        if not found:
            print("No major found by that name.  Try again.")
    major: Major = sess.query(Major).filter(Major.name == name).first()
    return major


def delete_department(session: Session):
    """
    Prompt the user for a department by the abbreviation and delete it.
    :param session: The connection to the database.
    :return:        None
    """
    print("deleting a department")
    department = select_department(session)
    n_courses = session.query(Course).filter(Course.departmentAbbreviation == department.abbreviation).count()
    if n_courses > 0:
        print(f"Sorry, there are {n_courses} courses in that department.  Delete them first, "
              "then come back here to delete the department.")
    else:
        session.delete(department)


def delete_course(session):
    print("deleting a course")
    course = select_course(session)
    n_sections = session.query(Section).filter(Section.course_number == course.courseNumber).count()
    if n_sections > 0:
        print(f"Sorry, there are {n_sections} courses in that department.  Delete them first, "
              "then come back here to delete the department.")
    else:
        session.delete(course)


def delete_student(session: Session):
    """
    Prompt the user for a student to delete and delete them.
    :param session:     The current connection to the database.
    :return:            None
    """
    student: Student = select_student(session)
    n_sections = session.query(Enrollment).filter(and_(student.studentID == Enrollment.studentId,
                                                       Enrollment.department_abbreviation == Section.department_abbreviation,
                                                       Enrollment.course_number == Section.course_number,
                                                       Enrollment.section_number == Section.section_number,
                                                       Enrollment.section_year == Section.section_year,
                                                       Enrollment.semester == Section.semester
                                                       )).count()
    if n_sections > 0:
        print(f"Sorry, there are {n_sections} sections in that student.  Delete them first, "
              "then come back here to delete the student.")
    else:
        session.delete(student)
    """This is a bit ghetto.  The relationship from Student to StudentMajor has 
    cascade delete, so this delete will work even if a student has declared one
    or more majors.  I could write a method on Student that would return some
    indication of whether it has any children, and use that to let the user know
    that they cannot delete this particular student.  But I'm too lazy at this
    point.
    """


def delete_section(session):
    print("deleting a section")
    select = select_section(session)
    n_students = session.query(Enrollment).filter(and_(Student.studentID == Enrollment.studentId,
                                                       Enrollment.department_abbreviation == select.department_abbreviation,
                                                       Enrollment.course_number == select.course_number,
                                                       Enrollment.section_number == select.section_number,
                                                       Enrollment.section_year == select.section_year,
                                                       Enrollment.semester == select.semester
                                                       )).count()
    if n_students > 0:
        print(f"Sorry, there are {n_students} students in that section.  Delete them first, "
              "then come back here to delete the section.")
    else:
        session.delete(select)


def delete_student_section(sess):
    """Undeclare a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the student and the course section that they no longer have.")
    find = False
    while not find:
        student: Student = select_student(sess)
        section: Section = select_section(sess)
        result = student.remove_section(section)
        if result:
            return
        else:
            print("The student do not have that section. Please try again")


def delete_section_student(sess):
    """Remove a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the major and the student who no longer has that course section.")
    find = False
    while not find:
        section: Section = select_section(sess)
        student: Student = select_student(sess)
        result = section.remove_student(student)
        if result:
            return
        else:
            print("The section do not have that study. Please try again")


def delete_student_major(sess):
    """Undeclare a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the student and the major that they no longer have.")
    student: Student = select_student(sess)
    major: Major = select_major(sess)
    student.remove_major(major)


def delete_major_student(sess):
    """Remove a student from a particular major.
    :param sess:    The current database session.
    :return:        None
    """
    print("Prompting you for the major and the student who no longer has that major.")
    major: Major = select_major(sess)
    student: Student = select_student(sess)
    major.remove_student(student)


def list_department(session: Session):
    """
    List all departments, sorted by the abbreviation.
    :param session:     The connection to the database.
    :return:            None
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    departments: [Department] = list(session.query(Department).order_by(Department.abbreviation))
    for department in departments:
        print(department)


def list_course(sess: Session):
    """
    List all courses currently in the database.
    :param sess:    The connection to the database.
    :return:        None
    """
    # session.query returns an iterator.  The list function converts that iterator
    # into a list of elements.  In this case, they are instances of the Student class.
    courses: [Course] = list(sess.query(Course).order_by(Course.courseNumber))
    for course in courses:
        print(course)


def list_student(sess: Session):
    """
    List all Students currently in the database.
    :param sess:    The current connection to the database.
    :return:
    """
    students: [Student] = list(sess.query(Student).order_by(Student.lastName, Student.firstName))
    for student in students:
        print(student)


def list_major(sess: Session):
    """
    List all majors in the database.
    :param sess:    The current connection to the database.
    :return:
    """
    majors: [Major] = list(sess.query(Major).order_by(Major.departmentAbbreviation))
    for major in majors:
        print(major)


def list_course_sections(sess):
    course = select_course(sess)
    course_sections: [Section] = course.get_sections()
    print("Sections for Course: " + str(course))
    for course_section in course_sections:
        print(course_section)


def list_student_section(sess: Session):
    """Prompt the user for the student, and then list the majors that the student has declared.
    :param sess:    The connection to the database
    :return:        None
    """
    student: Student = select_student(sess)
    recs = sess.query(Student).join(Enrollment, Student.studentID == Enrollment.studentId).join(
        Section, and_(Enrollment.department_abbreviation == Section.department_abbreviation,
                      Enrollment.course_number == Section.course_number,
                      Enrollment.section_number == Section.section_number,
                      Enrollment.section_year == Section.section_year,
                      Enrollment.semester == Section.semester)).filter(
        Student.studentID == student.studentID).add_columns(
        Student.lastName, Student.firstName,
        Section.department_abbreviation, Section.course_number, Section.section_number,
        Section.section_year, Section.semester).all()
    if not recs:
        print("Empty")
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Department: {stu.department_abbreviation}, "
              f"Course: {stu.course_number}, Section: {stu.section_number}, Section year: {stu.section_year}, Semester: {stu.semester}")


def list_section_student(sess: Session):
    """Prompt the user for the major, then list the students who have that major declared.
    :param sess:    The connection to the database.
    :return:        None
    """
    section: Section = select_section(sess)
    recs = sess.query(Section).join(Enrollment,
                                    and_(Enrollment.department_abbreviation == Section.department_abbreviation,
                                         Enrollment.course_number == Section.course_number,
                                         Enrollment.section_number == Section.section_number,
                                         Enrollment.section_year == Section.section_year,
                                         Enrollment.semester == Section.semester)). \
        join(Student,
             Student.studentID == Enrollment.studentId
             ).filter(
        Enrollment.department_abbreviation == section.department_abbreviation,
        Enrollment.course_number == section.course_number,
        Enrollment.section_number == section.section_number,
        Enrollment.section_year == section.section_year,
        Enrollment.semester == section.semester).add_columns(
        Student.lastName, Student.firstName,
        Section.department_abbreviation, Section.course_number, Section.section_number,
        Section.section_year, Section.semester).all()
    if not recs:
        print("Empty")
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Department: {stu.department_abbreviation}, "
              f"Course: {stu.course_number}, Section: {stu.section_number}, Section year: {stu.section_year}, Semester: {stu.semester}")


def list_student_major(sess: Session):
    """Prompt the user for the student, and then list the majors that the student has declared.
    :param sess:    The connection to the database
    :return:        None
    """
    student: Student = select_student(sess)
    recs = sess.query(Student).join(StudentMajor, Student.studentID == StudentMajor.studentId).join(
        Major, StudentMajor.majorName == Major.name).filter(
        Student.studentID == student.studentID).add_columns(
        Student.lastName, Student.firstName, Major.description, Major.name).all()
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Major: {stu.name}, Description: {stu.description}")


def list_major_student(sess: Session):
    """Prompt the user for the major, then list the students who have that major declared.
    :param sess:    The connection to the database.
    :return:        None
    """
    major: Major = select_major(sess)
    recs = sess.query(Major).join(StudentMajor, StudentMajor.majorName == Major.name).join(
        Student, StudentMajor.studentId == Student.studentID).filter(
        Major.name == major.name).add_columns(
        Student.lastName, Student.firstName, Major.description, Major.name).all()
    for stu in recs:
        print(f"Student name: {stu.lastName}, {stu.firstName}, Major: {stu.name}, Description: {stu.description}")


def move_course_to_new_department(sess: Session):
    """
    Take an existing course and move it to an existing department.  The course has to
    have a department when the course is created, so this routine just moves it from
    one department to another.

    The change in department has to occur from the Course end of the association because
    the association is mandatory.  We cannot have the course not have any department for
    any time the way that we would if we moved it to a new department from the department
    end.

    Also, the change in department requires that we make sure that the course will not
    conflict with any existing courses in the new department by name or number.
    :param sess:    The connection to the database.
    :return:        None
    """
    print("Input the course to move to a new department.")
    course = select_course(sess)
    old_department = course.department
    print("Input the department to move that course to.")
    new_department = select_department(sess)
    if new_department == old_department:
        print("Error, you're not moving to a different department.")
    else:
        # check to be sure that we are not violating the {departmentAbbreviation, name} UK.
        name_count: int = sess.query(Course).filter(Course.departmentAbbreviation == new_department.abbreviation,
                                                    Course.name == course.name).count()
        unique_name = name_count == 0
        if not unique_name:
            print("We already have a course by that name in that department.  Try again.")
        if unique_name:
            # Make sure that moving the course will not violate the {departmentAbbreviation,
            # course number} uniqueness constraint.
            number_count = sess.query(Course). \
                filter(Course.departmentAbbreviation == new_department.abbreviation,
                       Course.courseNumber == course.courseNumber).count()
            if number_count != 0:
                print("We already have a course by that number in that department.  Try again.")
            else:
                course.set_department(new_department)


def select_student_from_list(session):
    """
    This is just a cute little use of the Menu object.  Basically, I create a
    menu on the fly from data selected from the database, and then use the
    menu_prompt method on Menu to display characteristic descriptive data, with
    an index printed out with each entry, and prompt the user until they select
    one of the Students.
    :param session:     The connection to the database.
    :return:            None
    """
    # query returns an iterator of Student objects, I want to put those into a list.  Technically,
    # that was not necessary, I could have just iterated through the query output directly.
    students: [Department] = list(sess.query(Department).order_by(Department.lastName, Department.firstName))
    options: [Option] = []  # The list of menu options that we're constructing.
    for student in students:
        # Each time we construct an Option instance, we put the full name of the student into
        # the "prompt" and then the student ID (albeit as a string) in as the "action".
        options.append(Option(student.lastName + ', ' + student.firstName, student.studentId))
    temp_menu = Menu('Student list', 'Select a student from this list', options)
    # text_studentId is the "action" corresponding to the student that the user selected.
    text_studentId: str = temp_menu.menu_prompt()
    # get that student by selecting based on the int version of the student id corresponding
    # to the student that the user selected.
    returned_student = sess.query(Department).filter(Department.studentId == int(text_studentId)).first()
    # this is really just to prove the point.  Ideally, we would return the student, but that
    # will present challenges in the exec call, so I didn't bother.
    print("Selected student: ", returned_student)


def list_department_courses(sess):
    department = select_department(sess)
    dept_courses: [Course] = department.get_courses()
    print("Course for department: " + str(department))
    for dept_course in dept_courses:
        print(dept_course)


def boilerplate(sess):
    """
    Add boilerplate data initially to jump start the testing.  Remember that there is no
    checking of this data, so only run this option once from the console, or you will
    get a uniqueness constraint violation from the database.
    :param sess:    The session that's open.
    :return:        None
    """
    department: Department = Department('CECS', 'Computer Engineering Computer Science')
    major1: Major = Major(department, 'Computer Science', 'Fun with blinking lights')
    major2: Major = Major(department, 'Computer Engineering', 'Much closer to the silicon')
    student1: Student = Student('Brown', 'David', 'david.brown@gmail.com')
    student2: Student = Student('Brown', 'Mary', 'marydenni.brown@gmail.com')
    student3: Student = Student('Disposable', 'Bandit', 'disposable.bandit@gmail.com')
    student1.add_major(major1)
    student2.add_major(major1)
    student2.add_major(major2)
    sess.add(department)
    sess.add(major1)
    sess.add(major2)
    sess.add(student1)
    sess.add(student2)
    sess.add(student3)
    sess.flush()  # Force SQLAlchemy to update the database, although not commit


def session_rollback(sess):
    """
    Give the user a chance to roll back to the most recent commit point.
    :param sess:    The connection to the database.
    :return:        None
    """
    confirm_menu = Menu('main', 'Please select one of the following options:', [
        Option("Yes, I really want to roll back this session", "sess.rollback()"),
        Option("No, I hit this option by mistake", "pass")
    ])
    exec(confirm_menu.menu_prompt())


def count_student_section(sess, student: Student, section: Section):
    """Count the number of Enrollment instances for a given student & section.
    :param  sess        The current session.
    :param  student     The enrolling student.
    :param  section     The section that we want to see whether that student is enrolled."""
    pk_count: int = sess.query(Enrollment).filter(
        Enrollment.department_abbreviation == section.department_abbreviation,
        Enrollment.course_number == section.course_number,
        Enrollment.section_number == section.section_number,
        Enrollment.section_year == section.section_year,
        Enrollment.semester == section.semester,
        Enrollment.studentId == student.studentID).count()
    return pk_count


def add_student_PassFail(sess):
    """
    Add a student to a section as a pass/fail.
    :param sess: The current database connection.
    :return:    None
    """
    unique_student_section: bool = False
    while not unique_student_section:
        student = select_student(sess)
        section = select_section(sess)
        pk_count: int = count_student_section(sess, student, section)
        unique_student_section = pk_count == 0
        if not unique_student_section:
            print("That section already has that student enrolled in it.  Try again.")
    pass_fail = PassFail(section, student, datetime.now())
    sess.add(pass_fail)
    sess.flush()


def add_student_LetterGrade(sess):
    """
    Add a student to a section as a pass/fail.
    :param sess: The current database connection.
    :return:    None
    """
    unique_student_section: bool = False
    while not unique_student_section:
        student = select_student(sess)
        section = select_section(sess)
        pk_count: int = count_student_section(sess, student, section)
        unique_student_section = pk_count == 0
        if not unique_student_section:
            print("That section already has that student enrolled in it.  Try again.")
        else:
            correct_input = False
            while not correct_input:
                grade = input("Enter Student Grade: ")
                if grade not in ['A', 'B', 'C', 'D', 'F']:
                    print("Please enter again")
                else:
                    correct_input = True

    letter_grade = LetterGrade(section, student, grade)
    sess.add(letter_grade)
    sess.flush()


def list_enrollment(sess: Session):
    """
    List out all enrollment records sorted by department, course,
    section number.
    :param sess:    The current connection.
    :return:        None
    """
    recs = sess.query(Enrollment).order_by(Enrollment.department_abbreviation,
                                           Enrollment.course_number,
                                           Enrollment.section_year).all()
    for rec in recs:
        print(rec)


if __name__ == '__main__':
    print('Starting off')
    logging.basicConfig()
    # use the logging factory to create our first logger.
    # for more logging messages, set the level to logging.DEBUG.
    # logging_action will be the text string name of the logging level, for instance 'logging.INFO'
    # logging_action = debug_select.menu_prompt()
    # # eval will return the integer value of whichever logging level variable name the user selected.
    # logging.getLogger("sqlalchemy.engine").setLevel(eval(logging_action))
    # # use the logging factory to create our second logger.
    # # for more logging messages, set the level to logging.DEBUG.
    # logging.getLogger("sqlalchemy.pool").setLevel(eval(logging_action))

    # Prompt the user for whether they want to introspect the tables or create all over again.
    introspection_mode: int = IntrospectionFactory().introspection_type
    if introspection_mode == START_OVER:
        print("starting over")
        # create the SQLAlchemy structure that contains all the metadata, regardless of the introspection choice.
        metadata.drop_all(bind=engine)  # start with a clean slate while in development

        # Create whatever tables are called for by our "Entity" classes that we have imported.
        metadata.create_all(bind=engine)
    elif introspection_mode == REUSE_NO_INTROSPECTION:
        print("Assuming tables match class definitions")

    with Session() as sess:
        main_action: str = ''
        while main_action != menu_main.last_action():
            main_action = menu_main.menu_prompt()
            print('next action: ', main_action)
            exec(main_action)
        sess.commit()
    print('Ending normally')
