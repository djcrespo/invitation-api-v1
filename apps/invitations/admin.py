from django.contrib import admin
from .models import Invitation

@admin.register(Invitation)
class AdminInvitation(admin.ModelAdmin):
    ordering = ('-created_at',)
    list_display = ('id', 'confirm', 'from_person', 'group_person', 'type', 'persons', 'created_at', 'updated_at')
    search_fields = ('id', 'persons__full_name', )
    filter_vertical = ('confirm',)
    filter_horizontal = ('persons',)
    readonly_fields = ('created_at', 'updated_at')
