from django.db import models
from user_service.models import Profile

class Appointment(models.Model):
    tutor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='tutor_appointments')
    student = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='student_appointments')
    appointment_datetime = models.DateTimeField()

    def __str__(self):
        return f"Appointment on {self.appointment_datetime} between tutor {self.tutor.user.username} and student {self.student.user.username}"