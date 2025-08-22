from django.contrib import admin
from .models import Person

@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    ordering = ('full_name', )
    list_display = ('id', 'full_name', 'email', 'phone', 'created_at',)
    search_fields = ('full_name', 'email',)
    
