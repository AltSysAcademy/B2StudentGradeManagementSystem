'''
✅ /login     - POST   (Generate access, refresh)
✅ /logout    - POST   (Revoke access token)
✅ /refresh   - POST   (Generate non-fresh token)
✅ /register  - POST   (Create a new student model)

JWT Based - Identity (user.id)
✅ /student - GET (Student info)
✅ /student - DELETE (Delete account)

✅ /student/subject/<id> - GET (Get subject info by ID)
✅ /student/subject/<id> - POST (Enroll to a subject by ID)
✅ /student/subject/<id> - DELETE (Unenroll to a subject by ID)

✅ /student/subject/<id>/grades - GET (Get grades from a single subject)
✅ /student/subject/<id>/grades - PUT (Edit Grades)

✅ /student/subjects/grades - GET ALL SUBJECTS AND THEIR GRADES

✅ /student/subjects         - GET (GET ALL SUBJECTS)
'''

from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, create_refresh_token, create_access_token, get_jwt, get_jti
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import StudentModel, SubjectModel, StudentSubject, BlocklistModel
from schemas import SubjectSchema, StudentSchema, StudentSubjectSchema, UnenrollmentSchema, StudentLoginSchema, PlainStudentSchema, PlainSubjectSchema
from passlib.hash import pbkdf2_sha256

blp = Blueprint("students", __name__, description="Operation on students.")

@blp.route("/student/subjects")
class GetAllSubjects(MethodView):
    @jwt_required
    @blp.response(200, PlainSubjectSchema(many=True))
    def get(self):
        student_id = get_jwt()["sub"]
        student = StudentModel.query.get_or_404(student_id)
        return student.subjects

@blp.route('/register')
class StudentRegister(MethodView):
    @blp.arguments(PlainStudentSchema)
    def post(self, student_info):
        if StudentModel.query.filter(
            StudentModel.email == student_info["email"]
        ).first():
            abort(400, message="A student with that email already exists.")
        
        student = StudentModel(
            name=student_info["name"],
            email=student_info["email"],
            password=pbkdf2_sha256.hash(student_info["password"]),
            course=student_info["course"]
        )

        try:
            db.session.add(student)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while creating a new user.")

        return {"message": "Student registered successfully."}, 201


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(StudentLoginSchema)
    def post(self, login_cred):
        student = StudentModel.query.filter(
            StudentModel.email == login_cred["email"]
        ).first()

        if student and pbkdf2_sha256.verify(login_cred["password"], student.password):
            # Create access token
            access_token = create_access_token(identity=student.id, fresh=True)
            refresh_token = create_refresh_token(identity=student.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        
        abort(401, message="Invalid credentials.")


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        # GET JTI
        jwt_jti = get_jwt()["jti"]
        new_blocked_jti = BlocklistModel(jti=jwt_jti)
        db.session.add(new_blocked_jti)
        db.session.commit()

        return {"message": "Successfully logged out."}

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt()["sub"]
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
    
@blp.route("/student")
class Student(MethodView):
    @jwt_required()
    @blp.response(200, StudentSchema)
    def get(self):
        student_id = get_jwt()["sub"]
        student = StudentModel.query.get_or_404(student_id)
        return student
    
    @jwt_required(fresh=True)
    def delete(self):
        student_id = get_jwt()["sub"]
        student = StudentModel.query.get_or_404(student_id)
        
        db.session.delete(student)
        db.session.commit()

        return {"message": "Your account has been successfully deleted."}
    

# JWT - id=1
# GET /student/subject/1 - get the info
@blp.route("/student/subject/<int:subject_id>")
class EnrolledSubject(MethodView):
    @jwt_required()
    @blp.response(200, PlainSubjectSchema)
    def get(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])
        subject = SubjectModel.query.get_or_404(subject_id)

        if subject not in student.subjects:
            abort(400, message="Student not enrolled in the subject.")

        return subject

    @jwt_required()
    @blp.response(201, PlainSubjectSchema)
    def post(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])
        subject = SubjectModel.query.get_or_404(subject_id)

        # Before linking, make sure that the item and the tag is inside the same store
        if subject in student.subjects:
            abort(400, message="You are already enrolled in that subject.")

        student.subjects.append(subject)
    
        try:
            db.session.add(student)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while enrolling on the subject.")
        
        return subject
    
    @jwt_required(fresh=True)
    @blp.response(204, UnenrollmentSchema)
    def delete(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])
        subject = SubjectModel.query.get_or_404(subject_id)

        if subject not in student.subjects:
            abort(400, message="You are not enrolled on that subject.")
        
        student.subjects.remove(subject)

        try:
            db.session.add(student)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while unenrolling from the subject.")

        return {"message": "Subject was successfully unenrolled.", "student": student, "subject": subject}

# /student/subject/1/grades
@blp.route("/student/subject/<int:subject_id>/grades")
class SubjectGrades(MethodView):
    @jwt_required()
    @blp.response(200, StudentSubjectSchema)
    def get(self, subject_id):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])   # 1
        subject = SubjectModel.query.get_or_404(subject_id)         # 1

        if subject not in student.subjects:
            abort(400, message="Student is not enrolled in that subject")
        
        # CONJUNCTION TABLE
        grades = StudentSubject.query.filter(
            StudentSubject.student_id == student.id,
            StudentSubject.subject_id == subject.id
        ).first()

        return grades
    
    
    @jwt_required()
    @blp.arguments(StudentSubjectSchema)
    @blp.response(200, StudentSubjectSchema)
    def put(self, grade_data, subject_id):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])
        subject = SubjectModel.query.get_or_404(subject_id)      

        if subject not in student.subjects:
            abort(400, message="Student not enrolled in that subject")
        
        # CONJUNCTION
        grades = StudentSubject.query.filter(
            StudentSubject.student_id == student.id,
            StudentSubject.subject_id == subject.id
        ).first()

        if 'prelims_grade' in grade_data:
            grades.prelims_grade = grade_data['prelims_grade']
        if 'midterms_grade' in grade_data:
            grades.midterms_grade = grade_data['midterms_grade']
        if 'finals_grade' in grade_data:
            grades.finals_grade = grade_data['finals_grade']

        db.session.add(grades)
        db.session.commit()

        return grades


@blp.route("/student/subjects")
class EnrolledSubjects(MethodView):
    @jwt_required()
    @blp.response(200, PlainSubjectSchema(many=True))
    def get(self):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])
        
        return student.subjects
    
@blp.route("/student/subjects/grades")
class AllSubjectsGrades(MethodView):
    @jwt_required()
    @blp.response(200, StudentSubjectSchema(many=True))
    def get(self):
        student = StudentModel.query.get_or_404(get_jwt()["sub"])
        # Conjuction Tables
        grades = []
        for subject in student.subjects:
            grade = StudentSubject.query.filter(
                StudentSubject.student_id == student.id,
                StudentSubject.subject_id == subject.id
            ).first()
            grades.append(grade)
        
        return grades
