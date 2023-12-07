from sqlalchemy import Column, Integer, UniqueConstraint, Identity
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List  # Use this for the list of courses offered by the department

"""This is the guts of the department class that needs to be defined
regardless whether we introspect or not."""
__tablename__ = "departments"  # Give SQLAlchemy th name of the table.
name: Mapped[str] = mapped_column('name', String(50), nullable=False, primary_key=True)
abbreviation: Mapped[str] = mapped_column('abbreviation', String(6), nullable=False)
chair_name: Mapped[str] = mapped_column('chair_name', String(80), nullable=False)
building: Mapped[str] = mapped_column('building', String(10), nullable=False)
office: Mapped[int] = mapped_column('office', Integer, nullable=False)
description: Mapped[str] = mapped_column('description', String(80), nullable=False)

# Uniqueness constraints
__table_args__ = (UniqueConstraint('abbreviation', name='department_uk_01'),
                  UniqueConstraint('chair_name', name='department_uk_02'),
                  UniqueConstraint('building', 'office', name='department_uk_03'),
                  UniqueConstraint('description', name='department_uk_04'))


# constructor __init__ method
def __init__(self, name: str, abbreviation: str, chair_name: str, building: str, office: int, description: str):
    self.name = name
    self.abbreviation = abbreviation
    self.chair_name = chair_name
    self.building = building
    self.office = office
    self.description = description


courses: Mapped[List["Course"]] = relationship(back_populates="departments")


def add_course(self, course):
    if course not in self.courses:
        self.courses.add(course)  # I believe this will update the course as well.


def remove_course(self, course):
    if course in self.courses:
        self.courses.remove(course)


def get_courses(self):
    return self.courses


def __str__(self):
    return f"Department abbreviation: {self.abbreviation} name: {self.name} number course offered: {len(self.courses)}"
