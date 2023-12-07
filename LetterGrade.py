from sqlalchemy import ForeignKey, CheckConstraint, String
from sqlalchemy.orm import mapped_column, Mapped
from Enrollment import Enrollment


class LetterGrade(Enrollment):
    __tablename__ = "letter_grade"
    # I HAD put Integer after the table name, but apparently it picks that up from the parent PK.
    letterGradeId: Mapped[int] = mapped_column('letter_grade_id',
                                               ForeignKey("enrollments.enrollment_id",
                                                          ondelete="CASCADE"), primary_key=True)
    grade: Mapped[str] = mapped_column('grade', String(2), CheckConstraint("grade IN('A', 'B', 'C', 'D', 'F')"))
    __mapper_args__ = {"polymorphic_identity": "letter_grade"}

    def __init__(self, section, student, grade: String):
        super().__init__(section, student)
        self.grade = grade

    def __str__(self):
        return f"LetterGrade Enrollment: {super().__str__()}"
