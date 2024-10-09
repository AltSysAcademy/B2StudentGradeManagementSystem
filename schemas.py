from marshmallow import Schema, fields


class PlainStudentSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    course = fields.Str(required=True)

class StudentLoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class PlainSubjectSchema(Schema):
    id = fields.Int(dump_only=True)
    code = fields.Str(required=True)
    description = fields.Str(required=True)
    unit = fields.Int(required=True)

class StudentSchema(PlainStudentSchema):
    subjects = fields.List(fields.Nested(PlainSubjectSchema), dump_only=True)

class SubjectSchema(PlainSubjectSchema):
    students = fields.List(fields.Nested(PlainStudentSchema), dump_only=True)


class StudentSubjectSchema(Schema):
    id = fields.Int(dump_only=True)
    student_id = fields.Int(dump_only=True)
    subject_id = fields.Int(dump_only=True)

    prelims_grade = fields.Float(required=False)
    midterms_grade = fields.Float(required=False)
    finals_grade = fields.Float(required=False)

    average_grade = fields.Float(required=False, dump_only=True)

# Used when unenrolling student to a subject
class UnenrollmentSchema(Schema):
    message = fields.Str()
    student = fields.Nested(PlainStudentSchema)
    subject = fields.Nested(PlainSubjectSchema)