# PLUME-PROJECT/core/urls.py
from django.contrib import admin
from django.urls import path, include
# Adicione estas importações se você for servir arquivos de media (como avatares) durante o desenvolvimento
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('filmes.urls')), 
    path('conta/', include('usuarios.urls')), # Modificado para incluir a app 'usuarios'
    
]

# Adicione estas linhas SE for usar ImageField (avatares) e estiver em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)