from rest_framework import viewsets, permissions
from .models import Invitation
from .serializers import InvitationSerializer


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]
