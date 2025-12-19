from django.db import models


class Photo(models.Model):
    id = models.AutoField(primary_key=True, editable=False)
    file = models.FileField(upload_to='photos/', null=True, blank=True)
    message = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

    def __str__(self):
        return f"{self.id}"
