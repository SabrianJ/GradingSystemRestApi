from django.contrib import admin

# Register your models here.
from gradingsystem.models import Semester, Course, Lecturer, Class, Student, StudentEnrollment

admin.site.register(Semester)
admin.site.register(Course)
admin.site.register(Lecturer)
admin.site.register(Class)
admin.site.register(Student)
admin.site.register(StudentEnrollment)