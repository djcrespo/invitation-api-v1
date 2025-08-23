from django.db import models
from uuid import uuid4
from apps.persons.models import Person


TYPE_CHOICES = (
    ('GROUP', 'GROUP'),
    ('INDIVIDUAL', 'INDIVIDUAL'),
)

FROM_CHOICES = (
    ('DIDIER', 'DIDIER'),
    ('MARI', 'MARI'),
)

LIST_CHOICES = (
    ('FAMILY', 'FAMILY'),
    ('FRIENDS', 'FRIENDS'),
)

class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    persons = models.ManyToManyField(Person, related_name='persons_invitations', blank=False)
    confirm = models.BooleanField(default=None, null=True)
    message = models.TextField(blank=True, null=True)
    from_person = models.CharField(max_length=255, blank=True, null=True, choices=FROM_CHOICES)
    group_person = models.CharField(max_length=255, blank=True, null=True, choices=LIST_CHOICES)
    type = models.CharField(max_length=255, blank=True, null=True, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"
