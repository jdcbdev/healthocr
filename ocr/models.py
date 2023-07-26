from django.db import models

class MedicalRecord(models.Model):
    name = models.CharField(max_length=100, default='Unnamed')
    birthdate = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    text = models.TextField()
    task_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.text[:50]
