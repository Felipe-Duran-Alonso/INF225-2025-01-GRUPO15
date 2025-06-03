from django.contrib import admin
from .models import Boletin,Requerimiento
# Register your models here.

@admin.register(Boletin)
class BoletinAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion')
    
@admin.register(Requerimiento)
class RequerimientoAdmin(admin.ModelAdmin):
    list_display = ('regiones', 'objetivo','descripcion')