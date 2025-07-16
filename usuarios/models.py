# PLUME-PROJECT/usuarios/models.py
import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.utils.text import slugify # Para limpar o nome de usuário para nome de arquivo

# Função para personalizar o nome do arquivo do avatar
def avatar_upload_path(instance, filename):
    """
    Define o caminho e o nome do arquivo para o avatar do usuário.
    O nome do arquivo será: <username_slug>.<extensao_original>
    Salvo em: mediafiles/avatares/<username_slug>.<extensao_original>
    """
    # instance é a instância do modelo Perfil
    # filename é o nome original do arquivo enviado pelo usuário (ex: minha_foto.JPG)
    
    # Pegar a extensão do arquivo original (mantendo-a)
    ext = filename.split('.')[-1].lower() # Garante extensão minúscula
    
    # Criar um nome de arquivo "limpo" e seguro usando o username
    username_slug = slugify(instance.usuario.username)
    if not username_slug: # Caso o username seja algo que resulte em slug vazio
        username_slug = f"user_{instance.usuario.pk}" # Fallback para user_ID
        
    new_filename = f"{username_slug}.{ext}"
    
    # O caminho relativo dentro de MEDIA_ROOT
    return os.path.join('avatares', new_filename)

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    # Modificar o upload_to para usar a função personalizada
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)
    biografia = models.TextField(max_length=500, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Cidade')
    data_nascimento = models.DateField(null=True, blank=True, verbose_name='Data de Nascimento')

    def __str__(self):
        return f'Perfil de {self.usuario.username}'

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url') and self.avatar.url:
            # Adiciona um timestamp para tentar evitar problemas de cache do navegador
            # return f"{self.avatar.url}?v={self.avatar.instance.pk}_{os.path.getmtime(self.avatar.path)}" # Mais complexo com path
            return f"{self.avatar.url}?v={self.pk}" # Simples timestamp baseado no PK ou um campo de data de atualização
        return static('img/avatar_default.png')

    def get_nome_completo(self):
        if self.usuario.first_name and self.usuario.last_name:
            return f"{self.usuario.first_name} {self.usuario.last_name}"
        elif self.usuario.first_name:
            return self.usuario.first_name
        return self.usuario.username

    def save(self, *args, **kwargs):
        # Lógica para remover o arquivo antigo ANTES de salvar o novo,
        # especialmente se o nome do arquivo é fixo (baseado no username).
        if self.pk: # Só executa se o objeto já existe (não é uma criação)
            try:
                old_instance = Perfil.objects.get(pk=self.pk)
                # Se havia um avatar antigo E o novo avatar (self.avatar) é diferente do antigo
                # OU se o avatar antigo existe e o novo não (significa que o avatar foi limpo no formulário)
                if old_instance.avatar and old_instance.avatar.name and \
                   (self.avatar != old_instance.avatar or not self.avatar):
                    
                    # Se o avatar antigo existe fisicamente
                    if hasattr(old_instance.avatar, 'path') and os.path.isfile(old_instance.avatar.path):
                        print(f"[DEBUG Model Save] Tentando remover avatar antigo: {old_instance.avatar.path}")
                        os.remove(old_instance.avatar.path)
                        print(f"[DEBUG Model Save] Avatar antigo '{old_instance.avatar.name}' removido.")
                    # Para django-storages (nuvem), a lógica seria:
                    # elif hasattr(old_instance.avatar, 'delete'):
                    #     old_instance.avatar.delete(save=False)
                    #     print(f"[DEBUG Model Save] Avatar antigo '{old_instance.avatar.name}' deletado do storage.")
            except Perfil.DoesNotExist:
                pass # Objeto é novo, não há instância antiga.
            except Exception as e:
                print(f"[DEBUG Model Save] Erro ao tentar remover avatar antigo: {e}")
        
        super().save(*args, **kwargs) # Salva a instância atual.
                                      # A função avatar_upload_path definirá o nome do arquivo.
                                      # Se um arquivo com esse nome já existir (porque não foi deletado acima),
                                      # o Django adicionará um hash ao nome. A deleção prévia evita isso.

@receiver(post_save, sender=User)
def criar_ou_atualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(usuario=instance)
    else:
        Perfil.objects.get_or_create(usuario=instance)