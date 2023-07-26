from django.db import models


class MedicalRecord(models.Model):
    name = models.CharField(max_length=100, default='Unnamed')
    birthdate = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)  # Added
    home_phone = models.CharField(max_length=15, blank=True, null=True)  # Added
    mobile_phone = models.CharField(max_length=15, blank=True, null=True)  # Added
    work_phone = models.CharField(max_length=15, blank=True, null=True)  # Added
    text = models.TextField()
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.text[:50]

    def update_fields(self, name, birthdate, age, address=None, home_phone=None, mobile_phone=None, work_phone=None):  # Updated
        self.name = name
        self.birthdate = birthdate
        self.age = age
        self.address = address  # Added
        self.home_phone = home_phone  # Added
        self.mobile_phone = mobile_phone  # Added
        self.work_phone = work_phone  # Added
        self.save()
