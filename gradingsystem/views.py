from django.contrib.auth import logout
from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
import pyrebase
import os

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, action, authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from gradingsystem.models import Course, Semester, Lecturer, Class, Student, StudentEnrollment
from gradingsystem.permissions import IsLecturerClassOrAdmin
from gradingsystem.serializers import CourseSerializer, SemesterSerializer, LecturerSerializer, ClassSerializer, \
    StudentSerializer, SemesterPatchSerializer, StudentEnrollmentSerializer, StudentEnrollmentCompleteSerializer, \
    ClassLecturerSerializer, ClassCompleteSerializer, UserSerializer

from dotenv import load_dotenv
load_dotenv()

config = {
    "apiKey": str(os.getenv('GOOGLE_API_KEY')),
    "authDomain": str(os.getenv('GOOGLE_AUTH_DOMAIN')),
    "projectId": str(os.getenv('GOOGLE_PROJECT_ID')),
    "storageBucket": str(os.getenv('GOOGLE_STORE_BUCKET')),
    "messagingSenderId": str(os.getenv('GOOGLE_MESSENGER_SENDER_ID')),
    "appId": str(os.getenv('GOOGLE_APP_ID')),
    "measurementId": str(os.getenv('GOOGLE_MEASUREMENT_ID')),
    "databaseURL": ""
}


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsAdminUser]


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.all()
    serializer_class = SemesterSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)

        semester = Semester.objects.get(id=instance.id)

        if serializer.is_valid():
            deleted_course = list(set(semester.course.all()) - set(serializer.validated_data['course']))
            for course in deleted_course:
                classes = Class.objects.filter(course_id=course, semester_id=semester.id)
                classes.delete()
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return SemesterPatchSerializer
        return self.serializer_class


class LecturerViewSet(viewsets.ModelViewSet):
    queryset = Lecturer.objects.all()
    serializer_class = LecturerSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = User.objects.get(email=instance.email)
        user.delete()
        self.perform_destroy(instance)
        return Response(data='delete success')


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsAdminUser]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = User.objects.get(email=instance.email)
        user.delete()
        self.perform_destroy(instance)
        return Response(data='delete success')


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.all()
    serializer_class = StudentEnrollmentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsLecturerClassOrAdmin]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StudentEnrollmentCompleteSerializer
        return self.serializer_class


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def getStudentClassEnrollment(request):
    try:
        studentid = int(request.GET.get("studentid"))
        studentenrollment = StudentEnrollment.objects.filter(studentID=studentid)
        serializer = StudentEnrollmentCompleteSerializer(studentenrollment, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def getAvailableClassForStudent(request):
    try:
        studentid = int(request.GET.get("studentid"))
        studentenrollments = StudentEnrollment.objects.filter(studentID=studentid)
        all_class = Class.objects.all()
        student_class = [studentenrollment.classID for studentenrollment in studentenrollments]
        available_class = filter(lambda class_: class_ not in student_class, all_class)
        serializer = ClassSerializer(available_class, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def getClassBySemesterCourse(request):
    try:
        courseid = int(request.GET.get("courseid"))
        semesterid = int(request.GET.get("semesterid"))
        class_ = Class.objects.filter(course=courseid, semester=semesterid)
        serializer = ClassLecturerSerializer(class_, many=True)
        return Response(serializer.data)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def upload_student_file(request):
    try:
        if request.FILES['file']:
            myfile = request.FILES['file']
            fs = FileSystemStorage()
            if fs.exists(myfile.name):
                fs.delete(myfile.name)

            firebase = pyrebase.initialize_app(config)
            storage = firebase.storage()

            filename = fs.save(myfile.name, myfile)
            firebase = pyrebase.initialize_app(config)
            storage = firebase.storage()
            storage.child("files/" + myfile.name).put("media/" + myfile.name)

            import pandas as pd
            try:
                excel_data = pd.read_excel(f"media/{myfile.name}")
                data = pd.DataFrame(excel_data)
                dobs = data["DOB"].tolist()
                firstnames = data["Firstname"].tolist()
                lastnames = data["Lastname"].tolist()
                emails = data["Email"].tolist()
                ids = data["ID"].tolist()
                classes = data["Class"].tolist()
            except Exception as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            i = 0

            group = Group.objects.get(name="Student")
            while i < len(dobs):
                try:
                    first_name = firstnames[i].split(" ")[0].capitalize()
                    lastname = lastnames[i].split(" ")[-1].capitalize()
                    user = User.objects.create_user(username=f"{first_name[0]}{lastname}")
                    dob = dobs[i]
                    dob = str(dob).split(" ")[0]
                    password = dob.replace("-", "")
                    user.set_password(password)
                    user.first_name = firstnames[i]
                    user.last_name = lastnames[i]
                    user.email = emails[i]
                    user.save()
                    group.user_set.add(user)
                    student = Student(studentID=ids[i], firstname=firstnames[i], lastname=lastnames[i], email=emails[i],
                                      dob=dobs[i])
                    student.save()
                except Exception as e:
                    i += 1
                    continue

                try:
                    class_ = Class.objects.get(number=classes[i])
                    if not class_:
                        continue
                    student_enrollment = StudentEnrollment(studentID=student, classID=class_)
                    student_enrollment.save()
                except Exception as e:
                    print(e)
                    i += 1
                    continue

            return Response(status=status.HTTP_202_ACCEPTED, data={"message": "Upload Successful"})
    except Exception as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_gradeBooks(request):
    global class_
    user_group = request.user.groups.all().first()

    if user_group.name == "Lecturer":
        lecturer = Lecturer.objects.filter(email=request.user.email)[0]
        class_ = Class.objects.filter(lecturer=lecturer)

    elif user_group.name == "Student":
        student_enrolments = StudentEnrollment.objects.filter(studentID__email=request.user.email)
        class_ = []
        for enrolment in student_enrolments:
            if enrolment.classID not in class_:
                class_.append(enrolment.classID)
    elif user_group.name == "Admin":
        class_ = Class.objects.all()

    semesters = []
    for class__ in class_:
        if class__.semester not in semesters:
            semesters.append(class__.semester)

    semester_serializer = SemesterSerializer(semesters, many=True)
    class_serializer = ClassCompleteSerializer(class_, many=True)
    data = {"semesters": semester_serializer.data, "classes": class_serializer.data}
    return Response(status=status.HTTP_202_ACCEPTED, data=data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def gradebook_student(request):
    global student_enrollment
    user_group = request.user.groups.all().first()

    classid = int(request.GET.get("classid"))

    student_enrollment = StudentEnrollment.objects.filter(classID_id=classid)
    student_enrollment_serializer = StudentEnrollmentCompleteSerializer(student_enrollment, many=True)

    class_ = Class.objects.get(id=classid)
    class_serializer = ClassSerializer(class_)

    if user_group.name == "Student":
        student_enrollment = StudentEnrollment.objects.filter(classID_id=classid, studentID__email=request.user.email)
        student_enrollment_serializer = StudentEnrollmentCompleteSerializer(student_enrollment, many=True)

    return Response(status=status.HTTP_202_ACCEPTED,
                    data={"student": student_enrollment_serializer.data, "class": class_serializer.data})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [IsAuthenticated, IsAdminUser]


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        user_serializer = UserSerializer(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': user_serializer.data
        })


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user_serializer = UserSerializer(request.user)
    return Response(status=status.HTTP_202_ACCEPTED, data={"user": user_serializer.data})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_logout(request):
    logout(request)
    return Response(status=status.HTTP_202_ACCEPTED)

