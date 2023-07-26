from django.db import models

class MedicalRecord(models.Model):
    text = models.TextField()
    name = models.CharField(max_length=200, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.text[:50]
