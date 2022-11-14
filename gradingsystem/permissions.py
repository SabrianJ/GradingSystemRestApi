from rest_framework import permissions

from gradingsystem.models import StudentEnrollment


class IsLecturerClassOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user_groups = request.user.groups.values_list('name', flat=True)
        if "Admin" in user_groups:
            return True
        if "Lecturer" in user_groups:
            student_enrollment = StudentEnrollment.objects.get(id=obj.id)
            class_ = student_enrollment.classID
            if class_.lecturer.email == request.user.email:
                return True

        return False
