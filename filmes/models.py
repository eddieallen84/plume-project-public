# PLUME-PROJECT/filmes/models.py
from django.db import models
from django.contrib.auth.models import User

class Filme(models.Model):
    id_tmdb = models.IntegerField(unique=True) 
    titulo = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, blank=True, null=True)
    # Você pode adicionar mais campos aqui que deseja salvar do TMDB
    # data_lancamento = models.DateField(blank=True, null=True)
    # sinopse = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.titulo} (TMDB ID: {self.id_tmdb})"

class ListaFavoritos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listas_de_filmes')
    nome = models.CharField(max_length=255, default='Favoritos')
    filmes = models.ManyToManyField(Filme, related_name='listas_onde_esta', blank=True)
    padrao = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'nome')
        verbose_name = "Lista de Filmes do Usuário"
        verbose_name_plural = "Listas de Filmes dos Usuários"

    def __str__(self):
        return f"'{self.nome}' de {self.usuario.username}"