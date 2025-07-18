from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # A LINHA DE 'lancamentos' FOI REMOVIDA
    path('genero/<int:id_genero>/', views.view_filmes_por_genero, name='filmes_por_genero'),
    path('filme/<int:filme_id>/', views.detalhe_filme, name='detalhe_filme'),
    path('buscar/', views.buscar_filmes_view, name='buscar_filmes'),
    path('toggle_favorito/', views.toggle_favorito, name='toggle_favorito'),
    path('add_to_list/', views.add_filme_to_list_view, name='add_to_list'),
    path('remove_from_list/', views.remove_filme_from_list_view, name='remove_from_list'),
]