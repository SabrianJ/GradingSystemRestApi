import datetime

# Create your models here.
from django.db import models
from django.urls import reverse


class Course(models.Model):
    code = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        self.name = self.name.upper()
        return super(Course, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('list_courses')


year = datetime.datetime.today().year
YEARS = range(year, year + 6, +1)
YEARS_ARRAY = []
for year in YEARS:
    YEARS_ARRAY.append((year, year))

SEMESTERS = (("S1", "S1"), ("S2", "S2"), ("S3", "S3"))


class Semester(models.Model):
    year = models.IntegerField(default=None, choices=tuple(YEARS_ARRAY))
    semester = models.CharField(default=None, choices=SEMESTERS, max_length=5)
    course = models.ManyToManyField(Course, blank=True)

    class Meta:
        unique_together = ('year', 'semester',)

    def __str__(self):
        return f"{self.year} {self.semester}"

    def get_absolute_url(self):
        return reverse('list_semesters')


class Lecturer(models.Model):
    staffID = models.IntegerField(default=None)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    dob = models.DateField()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def save(self, *args, **kwargs):
        self.firstname = self.firstname.capitalize()
        self.lastname = self.lastname.capitalize()
        return super(Lecturer, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('list_lecturers')


class Class(models.Model):
    number = models.IntegerField(default=None, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.number}"

    def get_absolute_url(self):
        return reverse('list_classes')


class Student(models.Model):
    studentID = models.IntegerField(default=None)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    dob = models.DateField()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

    def save(self, *args, **kwargs):
        self.firstname = self.firstname.capitalize()
        self.lastname = self.lastname.capitalize()
        return super(Student, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('home')


class StudentEnrollment(models.Model):
    studentID = models.ForeignKey(Student, on_delete=models.CASCADE)
    classID = models.ForeignKey(Class, on_delete=models.CASCADE)
    grade = models.IntegerField(default=0)
    enrolTime = models.DateTimeField(auto_now_add=True)
    gradeTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.classID.number} {self.studentID}"

    def get_absolute_url(self):
        return reverse('home')


