from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from gradingsystem.views import CourseViewSet, SemesterViewSet, LecturerViewSet, StudentViewSet, ClassViewSet, \
    StudentEnrollmentViewSet, getStudentClassEnrollment, getAvailableClassForStudent, getClassBySemesterCourse, \
    upload_student_file, list_gradeBooks, gradebook_student, UserViewSet, CustomAuthToken, get_user_profile, user_logout

router = DefaultRouter()
router.register('course', CourseViewSet, "course")
router.register("semester", SemesterViewSet, "semester")
router.register("lecturer", LecturerViewSet, "lecturer")
router.register("class", ClassViewSet, "class")
router.register("student", StudentViewSet, "student")
router.register("studentenrollment", StudentEnrollmentViewSet, "studentenrollment")
router.register('user', UserViewSet, 'user')

urlpatterns = [
    path('api/auth/', CustomAuthToken.as_view()),
    path('api/', include(router.urls)),
    path('api/auth/logout', user_logout, name="userlogout"),
    path('api/profile', get_user_profile),
    path('api/studentenrollment/filter', getStudentClassEnrollment, name="filterstudentenrollment"),
    path('api/class/available_class', getAvailableClassForStudent, name="getAvailableClassForStudent"),
    path('api/class/filter', getClassBySemesterCourse, name="getClassBySemesterCourse"),
    path('api/student_load/', upload_student_file, name='uploadStudentFile'),
    path('api/gradebook/', list_gradeBooks, name='list_gradebook'),
    path('api/gradebook/filter',gradebook_student,name="gradebook_student")
]