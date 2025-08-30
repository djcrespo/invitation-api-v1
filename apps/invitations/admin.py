from django.contrib import admin
from .models import Invitation

@admin.register(Invitation)
class AdminInvitation(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('id', 'confirm', 'from_person', 'group_person', 'type', 'created_at', 'updated_at')
    search_fields = ('id', 'persons__full_name', )
    list_filter = ('confirm', 'from_person', 'group_person', 'type')
    readonly_fields = ('created_at', 'updated_at')
