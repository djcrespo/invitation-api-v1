from django.contrib import admin
from .models import Person

@admin.register(Person)
class AdminPerson(admin.ModelAdmin):
    ordering = ('first_name', 'last_name', )
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'created_at',)
    search_fields = ('first_name', 'last_name', 'email',)
    
