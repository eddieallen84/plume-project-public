# PLUME-PROJECT/usuarios/urls.py
from django.urls import path, reverse_lazy # <-- ADICIONE reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    CadastroView, CustomLoginView, CustomLogoutView, perfil_usuario,
    ajax_upload_avatar,
    ajax_remover_avatar,
    excluir_conta_view,
    ajax_delete_list_view,
    detalhe_lista_view,
)

app_name = 'usuarios'

urlpatterns = [
    # Suas URLs existentes
    path('cadastro/', CadastroView.as_view(), name='cadastro'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('perfil/', perfil_usuario, name='perfil_usuario'),
    path('perfil/ajax-upload-avatar/', ajax_upload_avatar, name='ajax_upload_avatar'),
    path('perfil/ajax-remover-avatar/', ajax_remover_avatar, name='ajax_remover_avatar'),
    path('perfil/excluir-conta/', excluir_conta_view, name='excluir_conta'),
    path('perfil/ajax-delete-list/', ajax_delete_list_view, name='ajax_delete_list'),
    path('lista/<int:lista_id>/', detalhe_lista_view, name='detalhe_lista'),

    # --- BLOCO DE URLS PARA RECUPERAÇÃO DE SENHA (COM CORREÇÃO) ---
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset_form.html", 
            email_template_name="registration/password_reset_email.html", 
            subject_template_name="registration/password_reset_subject.txt",
            # CORREÇÃO 1: Informa a URL de sucesso correta
            success_url=reverse_lazy('usuarios:password_reset_done')
         ), 
         name='password_reset'),
    
    path('reset_password/sent/', 
         auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
         ), 
         name='password_reset_done'),
         
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            # CORREÇÃO 2: Informa a URL de sucesso correta para esta etapa também
            success_url=reverse_lazy('usuarios:password_reset_complete')
         ), 
         name='password_reset_confirm'),
         
    path('reset_password/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
         ), 
         name='password_reset_complete'),
]