from db import db

class SubjectModel(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(250), unique=True, nullable=False)
    unit = db.Column(db.Integer, unique=False, nullable=False)

    students = db.relationship("StudentModel", back_populates="subjects", secondary="student_subject")


'''
GET subject/1 

{
    id:
    code:
    desc:
    unit:

    students: [
        student1{
            id,
            name,
            email
        }, 
        student2{
            id,
            name,
            email
        }
    ]
}
'''