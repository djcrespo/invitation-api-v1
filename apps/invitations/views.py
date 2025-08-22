from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Invitation
from .serializers import InvitationSerializer
from apps.persons.models import Person
from .emailService import send_email
import json


class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]


    @action(detail=True, methods=['POST'], permission_classes=[permissions.AllowAny])
    def confirm(self, request, pk=None):
        data = request.data
        invitation = self.get_object()
        if invitation.confirm is None:
            invitation.confirm = data.get('confirm')
            invitation.message = data.get('message')
            invitation.save()
            persons = invitation.persons.all()
            if persons.count() > 1:
                if invitation.confirm is True:
                    text = "Asistirán: \n \n"
                else:
                   text = "No podrán asistir: \n \n"
            else:
                if invitation.confirm is True:
                    text = "Asistirá: \n \n"
                else:
                   text = "No podrá asistir: \n \n"
            for person in persons:
                text += f"- {person.first_name} {person.last_name} \n"
            if invitation.message != "":
                text += f"\n Mensaje de aliento: \n {invitation.message}"
            send_email(text)
            return Response({'status': 'invitation confirmed'}, status=200)
        elif invitation.confirm is True:
            return Response({'status': 'invitation already confirmed'}, status=202)
        return Response({'status': 'confirmation failed'}, status=400)


    @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    def upload_persosn(self, request):
        persons = request.FILES.get('persons')
        persons_content = persons.read().decode('utf-8')
        persons_data = json.loads(persons_content)
        try:
            for grupo in persons_data:
                hoja = grupo['hoja'].split(" ")
                group = 'FRIENDS' if hoja[0] == 'AMIGOS' else 'FAMILY'
                origin = 'DIDIER' if hoja[1] == 'DIDIER' else 'MARI'
                grupos = grupo['grupos']
                for grupo in grupos:
                    type_group = grupo['tipo']
                    type = 'FAMILY' if (type_group == 'FAMILIA' or type_group == 'Pareja') else 'INDIVIDUAL'
                    invitation = Invitation.objects.create(
                        from_person=origin,
                        group_person=group,
                        type=type,
                    )
                    miembros = grupo['miembros']
                    for miembro in miembros:
                        person = Person.objects.create(
                            full_name=miembro['nombre'],
                        )
                        invitation.persons.add(person)
                    invitation.save()

            return Response({'status': 'Save persons'}, status=200)
        except Invitation.DoesNotExist:
            return Response({'status': 'invitation not found'}, status=404)