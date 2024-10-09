from db import db

class StudentModel(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    course = db.Column(db.String(200), unique=False, nullable=False)

    subjects = db.relationship("SubjectModel", back_populates="students", secondary="student_subject")


'''
GET student/1 

{
    id:
    name:
    email:
    password:

    subject: [
        subject1{
            id,
            code,
            desc,
            unit
        }, 
        subject2{
            id,
            code,
            desc,
            unit
        }
    ]
}
'''