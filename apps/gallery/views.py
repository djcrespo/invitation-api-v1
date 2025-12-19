from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from .models import *


class PhotoViewSet(viewsets.ModelViewSet):

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]


    @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    def upload_photo(self, request, pk=None):
        data = request.data
        if 'photo' in request.FILES:
            Photo.objects.create(
                file=request.FILES.get('photo'),
                message=data['message']
            )
            
            return Response(
                data={
                    "message": "Foto guardada"
                },
                status=status.HTTP_202_ACCEPTED
            )
        return Response(
                data={
                    "message": "Ocurrió un error, intente más tarde"
                },
                status=status.HTTP_406_NOT_ACCEPTABLE
            )
