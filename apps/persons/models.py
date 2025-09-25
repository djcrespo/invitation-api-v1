from django.db import models

class Person(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    # photo = models.FileField(upload_to='persons/photos/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.full_name}"
    