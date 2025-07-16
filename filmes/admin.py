# PLUME-PROJECT/filmes/admin.py
from django.contrib import admin
from .models import Filme, ListaFavoritos

@admin.register(Filme)
class FilmeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'id_tmdb')
    search_fields = ('titulo', 'id_tmdb')

@admin.register(ListaFavoritos)
class ListaFavoritosAdmin(admin.ModelAdmin):
    list_display = ('nome', 'usuario', 'padrao')
    list_filter = ('padrao', 'usuario')
    search_fields = ('nome', 'usuario__username')
    filter_horizontal = ('filmes',) # Melhor interface para ManyToManyFields