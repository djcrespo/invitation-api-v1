from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Invitation
from .serializers import InvitationSerializer
from apps.persons.models import Person
from .emailService import send_email
import json
import pandas as pd
from django.http import HttpResponse
import io


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
                text += f"- {person.full_name} \n"
            if invitation.message != "":
                text += f"\n Mensaje de aliento: \n {invitation.message}"
            send_email(text)
            return Response({'status': 'invitation confirmed'}, status=200)
        elif invitation.confirm is not None:
            if invitation.confirm != data['confirm']:
                invitation.confirm = data.get('confirm')
                if data['message'] != "" or data['message'] is not None:
                    invitation.message = data.get('message')
                invitation.save()
                persons = invitation.persons.all()
                text = "Cambio en la confirmación de asistencia: \n \n"
                if persons.count() > 1:
                    if invitation.confirm is True:
                        text += "Asistirán: \n \n"
                    else:
                        text += "No podrán asistir: \n \n"
                else:
                    if invitation.confirm is True:
                        text += "Asistirá: \n \n"
                    else:
                        text += "No podrá asistir: \n \n"
                for person in persons:
                    text += f"- {person.full_name} \n"
                if invitation.message != "":
                    text += f"\n Mensaje de aliento: \n {invitation.message}"
                send_email(text)
            return Response({'status': 'invitation already confirmed'}, status=202)
        return Response({'status': 'confirmation failed'}, status=400)


    @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def get_urls(self, request):
        data = request.data
        invitations = Invitation.objects.filter(
            group_person=data['group'], 
            from_person=data['from']
        )
        
        # Preparar datos para Excel
        excel_data = []
        
        for invitation in invitations:
            persons = invitation.persons.all()
            persons_list = ", ".join([person.full_name for person in persons])
            link = f"https://envetia-myd.djcrespo.dev/#/{invitation.id}"
            
            excel_data.append({
                'Tipo': invitation.type,
                'Personas': persons_list,
                'Enlace': link,
                # 'ID Invitación': str(invitation.id),
                # 'Grupo': invitation.group_person if invitation.group_person else '',
                # 'Creado por': invitation.from_person if invitation.from_person else '',
                # 'Fecha Creación': invitation.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                # 'Confirmado': 'Sí' if invitation.confirm else 'No'
            })
        
        # Crear DataFrame de pandas
        df = pd.DataFrame(excel_data)
        
        # Crear archivo Excel en memoria
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Invitaciones', index=False)
            
            # Autoajustar columnas
            worksheet = writer.sheets['Invitaciones']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="invitaciones.xlsx"'
        return response
    

    @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def upload_persons(self, request):
        listUrls = []
        persons = request.FILES.get('persons')
        persons_content = persons.read().decode('utf-8')
        persons_data = json.loads(persons_content)
        try:
            for grupo in persons_data:
                hoja = grupo['hoja'].split(" ")
                group = 'FRIENDS' if hoja[0] == 'AMIGOS' else 'FAMILY'
                origin = 'DIDIER' if hoja[1] == 'DIDIER' else 'MARI'
                group_url = {
                    "type_group_url": group,
                    "origin_persons": origin,
                    "invitations": []
                }
                grupos = grupo['grupos']
                for grupo in grupos:
                    persons = []
                    type_group = grupo['tipo']
                    type = 'GROUP' if (type_group == 'FAMILIA' or type_group == 'Pareja') else 'INDIVIDUAL'
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
                        persons.append(miembro['nombre'])
                        invitation.persons.add(person)
                    invitation.save()
                    link = f"https://envetia-myd.djcrespo.dev/#/{invitation.id}"
                    group_generate = {
                        'type': type,
                        'persons': persons,
                        'link': link
                    }
                    group_url["invitations"].append(group_generate)
                listUrls.append(group_url)
            return Response({'list': listUrls}, status=200)
        except Invitation.DoesNotExist:
            return Response({'status': 'invitation not found'}, status=404)
        

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def list_confirmed(self, request):
        confirmed_invitations = Invitation.objects.filter(confirm=True)
        count = 0
        for invitation in confirmed_invitations:
            count += invitation.persons.count()
        return Response({'confirmed_count': count}, status=200)
