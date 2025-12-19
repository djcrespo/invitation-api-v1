from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import *
from .models import *
import os, uuid
from botocore.exceptions import ClientError


class PhotoViewSet(viewsets.ModelViewSet):

    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticated]


    # @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    # def upload_photo(self, request, pk=None):
        # data = request.data
        # if 'photo' in request.FILES:
        #     Photo.objects.create(
        #         file=request.FILES.get('photo'),
        #         message=data['message']
        #     )

        #     return Response(
        #         data={
        #             "message": "Foto guardada"
        #         },
        #         status=status.HTTP_202_ACCEPTED
        #     )
        # elif 'files' in request.FILES:

        # return Response(
        #         data={
        #             "message": "Ocurrió un error, intente más tarde"
        #         },
        #         status=status.HTTP_406_NOT_ACCEPTABLE
        #    )

    @action(detail=False, methods=['POST'], permission_classes=[permissions.AllowAny])
    def upload_media(self, request, pk=None):
        """
        Endpoint para subir múltiples archivos (fotos y videos) con nombres UUID
        """
        data = request.data
        uploaded_files = []
        errors = []
        
        # Límites de tamaño (en bytes)
        MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
        MAX_VIDEO_SIZE = 250 * 1024 * 1024  # 250MB
        
        # Manejar archivos individuales (retrocompatibilidad)
        if 'photo' in request.FILES:
            file = request.FILES['photo']
            files_to_process = [file]
            field_name = 'photo'
        # Manejar múltiples archivos
        elif 'files' in request.FILES:
            files_to_process = request.FILES.getlist('files')
            field_name = 'files'
        else:
            return Response(
                data={
                    "message": "No se encontraron archivos para subir",
                    "detail": "Se requiere el campo 'photo' o 'files'"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for file in files_to_process:
            try:
                # Validar tipo MIME
                content_type = file.content_type
                is_image = content_type.startswith('image/')
                is_video = content_type.startswith('video/')
                
                if not (is_image or is_video):
                    errors.append({
                        "filename": file.name,
                        "error": f"Tipo de archivo no soportado: {content_type}"
                    })
                    continue
                
                # Validar tamaño según tipo
                if is_image and file.size > MAX_IMAGE_SIZE:
                    errors.append({
                        "filename": file.name,
                        "error": f"Imagen demasiado grande. Máximo: 5MB, Actual: {file.size / 1024 / 1024:.2f}MB"
                    })
                    continue
                elif is_video and file.size > MAX_VIDEO_SIZE:
                    errors.append({
                        "filename": file.name,
                        "error": f"Video demasiado grande. Máximo: 250MB, Actual: {file.size / 1024 / 1024:.2f}MB"
                    })
                    continue
                
                # Obtener extensión original
                original_filename = file.name
                file_extension = os.path.splitext(original_filename)[1].lower()
                
                # Si no tiene extensión, asignar una por defecto según tipo
                if not file_extension:
                    if is_image:
                        file_extension = '.jpg'
                    elif is_video:
                        file_extension = '.mp4'
                
                # Determinar tipo para el nombre
                file_type = 'foto' if is_image else 'video'
                
                # Generar UUID único
                unique_uuid = uuid.uuid4()
                
                # Construir nuevo nombre: archivo_uuid.extensión
                new_filename = f"{file_type}_{ str(unique_uuid)[:6]}{file_extension}"
                
                # IMPORTANTE: Django Storage manejará el guardado automáticamente
                # Solo necesitamos asignar el nuevo nombre al archivo
                file.name = new_filename
                
                # Crear instancia del modelo (Photo) con el archivo renombrado
                photo_instance = Photo.objects.create(
                    file=file,  # Django Storage guarda automáticamente
                    message=data.get('message', '')
                )
                
                uploaded_files.append({
                    "id": str(photo_instance.id),
                    "filename": new_filename,
                    "original_name": original_filename,
                    "type": file_type,
                    "size": file.size,
                    "size_formatted": f"{file.size / 1024 / 1024:.2f} MB",
                    "url": photo_instance.file.url,  # URL generada por Django Storage
                    "uploaded_at": photo_instance.created_at.isoformat() if hasattr(photo_instance, 'created_at') else None
                })
                
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code')
                if str(error_code) == '413' or 'EntityTooLarge' in str(error_code):
                    error_msg = "El archivo es demasiado grande para el servidor de almacenamiento. Por favor contacte al administrador."
                else:
                    error_msg = f"Error de almacenamiento: {str(e)}"
                
                errors.append({
                    "filename": file.name,
                    "error": error_msg
                })
            except Exception as e:
                errors.append({
                    "filename": file.name if 'file' in locals() else "Desconocido",
                    "error": str(e)
                })
                continue
        
        # Preparar respuesta
        response_data = {
            "success": len(uploaded_files) > 0,
            "uploaded_count": len(uploaded_files),
            "error_count": len(errors),
            "uploaded_files": uploaded_files,
        }
        
        # Si hay errores, incluirlos en la respuesta
        if errors:
            response_data["errors"] = errors
        
        # Determinar código de estado HTTP
        if uploaded_files:
            status_code = status.HTTP_201_CREATED
            response_data["message"] = f"Se subieron {len(uploaded_files)} archivo(s) exitosamente"
        else:
            status_code = status.HTTP_400_BAD_REQUEST
            response_data["message"] = "No se pudo subir ningún archivo"
        
        return Response(data=response_data, status=status_code)
