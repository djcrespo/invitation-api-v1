from django.contrib import admin
from .models import Invitation

@admin.register(Invitation)
class AdminInvitation(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('id', 'confirm', 'from_person', 'group_person', 'display_persons', 'type', 'created_at', 'updated_at')
    search_fields = ('id', 'persons__full_name', )
    list_filter = ('confirm', 'from_person', 'group_person', 'type')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['check_confirm_true', 'check_confirm_false', 'uncheck_confirm']

    def display_persons(self, obj):
        """Muestra la lista de personas en la relación ManyToMany"""
        # Obtener todas las personas relacionadas
        persons = obj.persons.all()
        
        # Crear una lista de nombres o identificadores
        if persons:
            # Si quieres mostrar los nombres
            person_list = [person.full_name for person in persons]
            # O si prefieres mostrar emails o IDs
            # person_list = [person.email for person in persons]
            
            # Unir la lista con comas y limitar a 3 elementos
            return ", ".join(person_list[:3]) + ("..." if len(person_list) > 3 else "")
        return "Ninguna persona"
    
    # Configuración opcional para el nombre de la columna
    display_persons.short_description = 'Personas invitadas'

    def check_confirm_true(self, request, queryset):
        for invitation in queryset:
            if invitation.confirm is None:
                invitation.confirm = True
                invitation.save()
        self.message_user(request, "Confirmación de invitaciones actualizada a Si asistirá.")

    def check_confirm_false(self, request, queryset):
        for invitation in queryset:
            if invitation.confirm is None:
                invitation.confirm = False
                invitation.save()
        self.message_user(request, "Confirmación de invitaciones actualizada a No Asistirá.")

    def uncheck_confirm(self, request, queryset):
        for invitation in queryset:
            if invitation.confirm is not None:
                invitation.confirm = None
                invitation.save()
        self.message_user(request, "Confirmación de invitaciones revertida.")

    

