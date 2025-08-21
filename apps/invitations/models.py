from django.db import models
from uuid import uuid4
from apps.persons.models import Person


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    persons = models.ManyToManyField(Person, related_name='persons_invitations', blank=False)
    confirm = models.BooleanField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"
