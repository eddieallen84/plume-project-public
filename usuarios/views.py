# PLUME-PROJECT/usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.templatetags.static import static
import json

from .forms import NovoUsuarioForm, PerfilForm, AvatarUploadForm
from .models import Perfil # Assumindo que Perfil está em .models
from filmes.models import ListaFavoritos, Filme # <-- Verifique e adicione esta importação para Filme e ListaFavoritos/ListaPersonalizada
from filmes.utils import get_lista_generos
from django.contrib.auth import logout 


class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'
    def form_valid(self, form):
        messages.success(self.request, f"Login bem-sucedido! Bem-vindo(a) de volta, {form.get_user().username}.")
        return super().form_valid(form)
    def form_invalid(self, form):
        messages.error(self.request, "Nome de usuário ou senha inválidos. Tente novamente.")
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "Você foi desconectado com sucesso.")
        return super().dispatch(request, *args, **kwargs)

class CadastroView(View):
    form_class = NovoUsuarioForm
    template_name = 'usuarios/cadastro.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Cadastro realizado com sucesso! Bem-vindo(a), {user.username}!")
            return redirect('home')
        else:
            error_messages = []
            if form.non_field_errors():
                for error in form.non_field_errors(): error_messages.append(str(error))
            for field in form:
                if field.errors:
                    label = field.label or field.name
                    for error_msg_obj in field.errors:
                        error_messages.append(f"{label}: {error_msg_obj}")
            if not error_messages: messages.error(request, "Por favor, corrija os erros no formulário.")
            else:
                for msg in error_messages: messages.error(request, msg)
        return render(request, self.template_name, {'form': form})


@login_required
@require_POST
def ajax_upload_avatar(request):
    perfil_obj, created = Perfil.objects.get_or_create(usuario=request.user)
    form = AvatarUploadForm(request.POST, request.FILES, instance=perfil_obj)

    if form.is_valid():
        try:
            perfil_salvo = form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Avatar atualizado com sucesso!',
                'avatar_url': perfil_salvo.get_avatar_url()
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Erro interno ao salvar o avatar.'}, status=500)
    else:
        error_data = form.errors.get_json_data(escape_html=True)
        error_message = "Não foi possível atualizar o avatar."
        if 'avatar' in error_data and error_data['avatar'] and error_data['avatar'][0].get('message'):
            error_message = error_data['avatar'][0]['message']
        elif form.non_field_errors():
             error_message = str(form.non_field_errors()[0].message)

        return JsonResponse({
            'status': 'error',
            'message': error_message,
            'errors': error_data 
        }, status=400)

@login_required
@require_POST
def ajax_remover_avatar(request):
    try:
        perfil_obj = Perfil.objects.get(usuario=request.user)
        if perfil_obj.avatar and perfil_obj.avatar.name:
            perfil_obj.avatar = None 
            perfil_obj.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Foto de perfil removida com sucesso!',
                'avatar_url': perfil_obj.get_avatar_url()
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'Você já está usando o avatar padrão.',
                'avatar_url': perfil_obj.get_avatar_url()
            })
    except Perfil.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Perfil não encontrado.'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erro ao remover o avatar: {e}'}, status=500)


@login_required
def perfil_usuario(request):
    usuario_atual = request.user
    perfil_obj, perfil_foi_criado = Perfil.objects.get_or_create(usuario=usuario_atual)
    form_perfil = PerfilForm(instance=perfil_obj)

    if request.method == 'POST':
        if 'atualizar_perfil_info' in request.POST:
            form_perfil = PerfilForm(request.POST, instance=perfil_obj) 
            if form_perfil.is_valid():
                form_perfil.save()
                messages.success(request, 'Suas informações de perfil foram atualizadas com sucesso!')
                return redirect('usuarios:perfil_usuario')
            else:
                if form_perfil.non_field_errors():
                    for error in form_perfil.non_field_errors(): messages.error(request, str(error))
                for field_name, error_list in form_perfil.errors.items():
                    label = form_perfil.fields.get(field_name).label if form_perfil.fields.get(field_name) else field_name
                    for error_msg_obj in error_list:
                        messages.error(request, f"Erro no campo '{label}': {error_msg_obj}")
        
        elif 'criar_lista' in request.POST:
            nome_nova_lista = request.POST.get('nome_nova_lista', '').strip()
            listas_existentes = ListaFavoritos.objects.filter(usuario=usuario_atual)
            if nome_nova_lista:
                count_personalizadas = listas_existentes.filter(padrao=False).count()
                if count_personalizadas < 5:
                    if not listas_existentes.filter(nome=nome_nova_lista, padrao=False).exists():
                        ListaFavoritos.objects.create(usuario=usuario_atual, nome=nome_nova_lista, padrao=False)
                        messages.success(request, f"Lista '{nome_nova_lista}' criada com sucesso!")
                    else:
                        messages.error(request, f"Você já tem uma lista chamada '{nome_nova_lista}'.")
                else:
                    messages.error(request, "Você atingiu o limite de 5 listas personalizadas.")
            else:
                messages.error(request, "O nome da lista não pode ser vazio.")
            return redirect('usuarios:perfil_usuario')
    
    listas_do_usuario = ListaFavoritos.objects.filter(usuario=usuario_atual).prefetch_related('filmes')
    favoritos_padrao, _ = ListaFavoritos.objects.get_or_create(
        usuario=usuario_atual, nome='Favoritos', defaults={'padrao': True}
    )
    listas_personalizadas = [lista for lista in listas_do_usuario if not lista.padrao]
    
    context = {
        'usuario_perfil': usuario_atual,      
        'perfil_modelo': perfil_obj,         
        'perfil_form': form_perfil,
        'favoritos_padrao': favoritos_padrao,
        'listas_personalizadas': listas_personalizadas,
        'generos_menu': get_lista_generos(),
        'request_path': request.path,
        'base_poster_url': "https://image.tmdb.org/t/p/w154",
        'avatar_default_url': static('img/avatar_default.png')
    }
    return render(request, 'usuarios/perfil_usuario.html', context)

@login_required
def excluir_conta_view(request):
    if request.method == 'POST':
        usuario_para_excluir = request.user
        try:
            username = usuario_para_excluir.username
            usuario_para_excluir.delete()
            logout(request)
            messages.success(request, f"A conta de '{username}' foi excluída com sucesso. Sentiremos sua falta!")
            return redirect('home')

        except Exception as e:
            messages.error(request, f"Ocorreu um erro ao tentar excluir sua conta: {e}")
            return redirect('usuarios:perfil_usuario')

    return render(request, 'usuarios/exclusao_conta.html')

@login_required
@require_POST
def ajax_delete_list_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        id_lista = data.get("id_lista")

        lista_obj = ListaFavoritos.objects.get(id=id_lista, usuario=request.user, padrao=False)
        
        nome_lista = lista_obj.nome
        lista_obj.delete()
        
        return JsonResponse({"status": "ok", "message": f"A lista '{nome_lista}' foi excluída com sucesso."})

    except ListaFavoritos.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Lista não encontrada, não pertence a você ou não pode ser excluída."}, status=404)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Erro interno: {e}"}, status=500)
    
@login_required
def detalhe_lista_view(request, lista_id):
    # get_object_or_404 é uma forma segura de buscar um objeto.
    # Ele garante que a lista existe e pertence ao usuário logado.
    # Se não encontrar, ele automaticamente gera um Erro 404 (Página não encontrada).
    lista = get_object_or_404(ListaFavoritos, id=lista_id, usuario=request.user)
    
    # Pega todos os filmes associados a essa listaF
    filmes_na_lista = lista.filmes.all()
    
    context = {
        'lista': lista,
        'filmes_na_lista': filmes_na_lista,
        'base_poster_url': "https://image.tmdb.org/t/p/w154", # Mesmo tamanho de poster do perfil
    }
    
    return render(request, 'usuarios/detalhe_lista.html', context)


@login_required
@require_POST
def ajax_remover_filme_da_lista(request): 
    """
    Remove um filme de uma lista personalizada ou da lista de favoritos do usuário via AJAX.
    Este endpoint agora pode ser usado para ambas as listas, dependendo do list_id.
    """
    try:
        data = json.loads(request.body)
        list_id = data.get('list_id')
        id_tmdb = data.get('id_tmdb')

        if not list_id or not id_tmdb:
            return JsonResponse({'status': 'error', 'message': 'ID da lista ou do filme não fornecido.'}, status=400)

        try:
            # Obtém a lista, garantindo que ela pertence ao usuário logado
            # 'ListaFavoritos' é o seu modelo para representar as listas, sejam elas padrão ou personalizadas.
            lista = ListaFavoritos.objects.get(id=list_id, usuario=request.user) 
            filme = Filme.objects.get(id_tmdb=id_tmdb) 
            
            if filme in lista.filmes.all():
                lista.filmes.remove(filme)
                # Não é estritamente necessário chamar .save() para ManyToManyField após remove(),
                # mas não faz mal e garante que qualquer sinal associado seja disparado.
                # lista.save() 
                return JsonResponse({'status': 'ok', 'message': 'Filme removido com sucesso.'}) 
            else:
                return JsonResponse({'status': 'error', 'message': 'Filme não encontrado nesta lista.'}, status=404) 
        except ListaFavoritos.DoesNotExist: 
            return JsonResponse({'status': 'error', 'message': 'Lista não encontrada ou não pertence ao usuário.'}, status=404)
        except Filme.DoesNotExist: 
            return JsonResponse({'status': 'error', 'message': 'Filme não encontrado.'}, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Requisição JSON inválida.'}, status=400)
    except Exception as e:
        # Logar o erro 'e' para depuração em produção
        return JsonResponse({'status': 'error', 'message': f'Um erro inesperado ocorreu: {str(e)}'}, status=500)