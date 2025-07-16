# PLUME-PROJECT/filmes/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('lancamentos/', views.filmes_lancamentos, name='filmes_lancamentos'),
    path('genero/<int:id_genero>/', views.view_filmes_por_genero, name='filmes_por_genero'),
    path('filme/<int:filme_id>/', views.detalhe_filme, name='detalhe_filme'),
    path('buscar/', views.buscar_filmes_view, name='buscar_filmes'),
    path('ajax/toggle-favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('ajax/add-to-list/', views.add_filme_to_list_view, name='add_to_list'),
    path('ajax/remove-from-list/', views.remove_filme_from_list_view, name='remove_from_list'),
]