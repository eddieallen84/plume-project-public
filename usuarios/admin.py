# PLUME-PROJECT/usuarios/admin.py
from django.contrib import admin
from .models import Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'biografia_curta', 'cidade', 'data_nascimento')
    search_fields = ('usuario__username', 'usuario__email', 'cidade')
    list_filter = ('cidade',) # Adicione 'data_nascimento' se fizer sentido

    def biografia_curta(self, obj):
        if obj.biografia:
            return obj.biografia[:50] + "..." if len(obj.biografia) > 50 else obj.biografia
        return "-"
    biografia_curta.short_description = 'Biografia'