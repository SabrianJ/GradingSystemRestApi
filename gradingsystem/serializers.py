import os

from django.contrib.auth.models import Group, User
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueTogetherValidator
from sendgrid import SendGridAPIClient, Mail

from gradingsystem.models import Course, Semester, Lecturer, Class, Student, StudentEnrollment

from dotenv import load_dotenv
load_dotenv()

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class SemesterSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True, many=True)

    class Meta:
        model = Semester
        fields = ('id', 'year', 'semester', 'course')
        validators = [
            UniqueTogetherValidator(
                queryset=Semester.objects.all(),
                fields=["year", "semester"],
                message="Semester with such semester and year already exists"
            )
        ]


class SemesterPatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = ('course',)

    @transaction.atomic
    def update(self, instance, validated_data):
        semester = instance
        return super().update(instance, validated_data)


class LecturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lecturer
        fields = "__all__"

    def create(self, validated_data):
        lecturer = Lecturer.objects.create(**validated_data)

        group = Group.objects.get(name="Lecturer")
        username = f"{lecturer.firstname[0].capitalize()}{lecturer.lastname.capitalize()}"
        password = lecturer.dob.strftime('%Y%m%d')
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.first_name = lecturer.firstname
        user.last_name = lecturer.lastname
        user.email = lecturer.email
        user.save()
        group.user_set.add(user)

        return lecturer


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"

    def create(self, validated_data):
        student = Student.objects.create(**validated_data)

        group = Group.objects.get(name="Student")
        username = f"{student.firstname[0].capitalize()}{student.lastname.capitalize()}"
        password = student.dob.strftime('%Y%m%d')
        user = User.objects.create_user(username=username)
        user.set_password(password)
        user.first_name = student.firstname
        user.last_name = student.lastname
        user.email = student.email
        user.save()
        group.user_set.add(user)

        return user


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollment
        fields = "__all__"

    def update(self, instance, validated_data):
        student_enrolment = StudentEnrollment.objects.get(id=instance.id)
        if instance.grade != validated_data.get('grade'):
            student = student_enrolment.studentID
            content = f'Kia Ora <strong>{student.firstname} {student.lastname},</strong><br/><br/>' \
                      f'<p>Your grade for class {student_enrolment.classID.number} is updated. You can check it in the website ' \
                      f'</p><br/><p>Kind regards, </p><br/>Grading team'
            message = Mail(
                from_email='jr1242390@gmail.com',
                to_emails=student_enrolment.studentID.email,
                subject='Grade Update',
                html_content=content)
            try:
                sg = SendGridAPIClient(str(os.getenv('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')))
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
        return super().update(instance,validated_data)


class ClassCompleteSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    semester = SemesterSerializer(read_only=True)

    class Meta:
        model = Class
        fields = "__all__"


class StudentEnrollmentCompleteSerializer(serializers.ModelSerializer):
    classID = ClassSerializer(read_only=True)
    studentID = StudentSerializer(read_only=True)

    class Meta:
        model = StudentEnrollment
        fields = "__all__"


class ClassLecturerSerializer(serializers.ModelSerializer):
    lecturer = LecturerSerializer(read_only=True)

    class Meta:
        model = Class
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'groups']

        extra_kwargs = {'password': {
            'write_only': True,
            'required': True
        }}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        user.groups.add(1)
        return user
