# PLUME-PROJECT/filmes/views.py
from django.shortcuts import render
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime

from .utils import (
    get_filmes_populares,
    get_filmes_lancamento,
    get_filmes_por_genero,
    get_detalhes_filme,
    search_tmdb_filmes,
    get_lista_generos 
)
from .models import Filme, ListaFavoritos

SORT_BY_OPTIONS = {
    "popularity.desc": "Populares (do maior para menor)",
    "popularity.asc": "Populares (do menor para maior)",
    "release_date.desc": "Data de Lançamento (mais recentes)",
    "release_date.asc": "Data de Lançamento (mais antigos)",
    "vote_average.desc": "Avaliação (da maior para menor)",
    "vote_average.asc": "Avaliação (da menor para maior)",
    "original_title.asc": "Título (A-Z)",
    "original_title.desc": "Título (Z-A)",
}

def enrich_filmes_with_favoritos(request, lista_filmes):
    if request.user.is_authenticated:
        try:
            lista_favoritos_padrao = ListaFavoritos.objects.get(usuario=request.user, padrao=True)
            favoritos_ids = set(lista_favoritos_padrao.filmes.values_list('id_tmdb', flat=True))
        except ListaFavoritos.DoesNotExist:
            favoritos_ids = set()
        
        for filme in lista_filmes:
            filme['is_favorito'] = filme.get('id') in favoritos_ids
    return lista_filmes

def processar_resposta_api(api_response):
    if api_response:
        filmes = api_response.get("results", [])
        page = api_response.get("page", 1)
        total_pages = min(api_response.get("total_pages", 1), 500)
        return filmes, page, total_pages
    return [], 1, 1

def gerar_numeros_paginacao(pagina_atual, total_de_paginas, vizinhos=2):
    if total_de_paginas <= 1:
        return []
    numeros_paginacao = [1]
    if pagina_atual - vizinhos > 2:
        numeros_paginacao.append("...")
    inicio_janela = max(2, pagina_atual - vizinhos)
    fim_janela = min(total_de_paginas - 1, pagina_atual + vizinhos)
    for i in range(inicio_janela, fim_janela + 1):
        if i not in numeros_paginacao:
            numeros_paginacao.append(i)
    if pagina_atual + vizinhos < total_de_paginas - 1:
        if total_de_paginas not in numeros_paginacao:
            numeros_paginacao.append("...")
    if total_de_paginas > 1 and total_de_paginas not in numeros_paginacao:
        numeros_paginacao.append(total_de_paginas)
    return numeros_paginacao

def home(request):
    page_num = int(request.GET.get("page", "1"))
    sort_by_param = request.GET.get("sort_by", "popularity.desc")
    api_response = get_filmes_populares(page=page_num, sort_by=sort_by_param)
    
    lista_de_filmes, pagina_atual, total_de_paginas = processar_resposta_api(api_response)
    lista_de_filmes = enrich_filmes_with_favoritos(request, lista_de_filmes)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    base_query_string = query_params.urlencode()

    listas_personalizadas_usuario = []
    if request.user.is_authenticated:
        listas_personalizadas_usuario = list(ListaFavoritos.objects.filter(usuario=request.user, padrao=False).values('id', 'nome'))

    context = {
        "titulo_secao": "Populares", "lista_filmes": lista_de_filmes, "pagina_atual": pagina_atual,
        "total_de_paginas": total_de_paginas, "numeros_de_pagina_para_template": gerar_numeros_paginacao(pagina_atual, total_de_paginas),
        "base_poster_url": "https://image.tmdb.org/t/p/w200", "pode_ordenar": True, "sort_by_options": SORT_BY_OPTIONS,
        "sort_by_atual": sort_by_param, "base_query_string_pagination": base_query_string, "request_path": request.path,
        "listas_personalizadas_usuario": listas_personalizadas_usuario,
    }
    return render(request, "filmes/lista_filmes.html", context)

def filmes_lancamentos(request):
    page_num = int(request.GET.get("page", "1"))
    sort_by_param = request.GET.get("sort_by", "popularity.desc")
    api_response = get_filmes_lancamento(page=page_num, sort_by=sort_by_param)
    
    lista_de_filmes, pagina_atual, total_de_paginas = processar_resposta_api(api_response)
    lista_de_filmes = enrich_filmes_with_favoritos(request, lista_de_filmes)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    base_query_string = query_params.urlencode()

    listas_personalizadas_usuario = []
    if request.user.is_authenticated:
        listas_personalizadas_usuario = list(ListaFavoritos.objects.filter(usuario=request.user, padrao=False).values('id', 'nome'))

    context = {
        "titulo_secao": "Lançamentos", "lista_filmes": lista_de_filmes, "pagina_atual": pagina_atual,
        "total_de_paginas": total_de_paginas, "numeros_de_pagina_para_template": gerar_numeros_paginacao(pagina_atual, total_de_paginas),
        "base_poster_url": "https://image.tmdb.org/t/p/w200", "pode_ordenar": True, "sort_by_options": SORT_BY_OPTIONS,
        "sort_by_atual": sort_by_param, "base_query_string_pagination": base_query_string, "request_path": request.path,
        "listas_personalizadas_usuario": listas_personalizadas_usuario,
    }
    return render(request, "filmes/lista_filmes.html", context)

def view_filmes_por_genero(request, id_genero):
    page_num = int(request.GET.get("page", "1"))
    sort_by_param = request.GET.get("sort_by", "popularity.desc")
    
    generos_do_menu = get_lista_generos()
    nome_genero_atual = next((g.get('name') for g in generos_do_menu if g.get('id') == id_genero), "Gênero")
    
    api_response = get_filmes_por_genero(id_genero, page=page_num, sort_by=sort_by_param)
    lista_de_filmes, pagina_atual, total_de_paginas = processar_resposta_api(api_response)
    lista_de_filmes = enrich_filmes_with_favoritos(request, lista_de_filmes)

    query_params = request.GET.copy()
    query_params.pop("page", None)
    base_query_string = query_params.urlencode()

    listas_personalizadas_usuario = []
    if request.user.is_authenticated:
        listas_personalizadas_usuario = list(ListaFavoritos.objects.filter(usuario=request.user, padrao=False).values('id', 'nome'))

    context = {
        "titulo_secao": nome_genero_atual, "lista_filmes": lista_de_filmes, "pagina_atual": pagina_atual,
        "total_de_paginas": total_de_paginas, "numeros_de_pagina_para_template": gerar_numeros_paginacao(pagina_atual, total_de_paginas),
        "id_genero_ativo": id_genero, "base_poster_url": "https://image.tmdb.org/t/p/w200",
        "pode_ordenar": True, "sort_by_options": SORT_BY_OPTIONS, "sort_by_atual": sort_by_param,
        "base_query_string_pagination": base_query_string, "request_path": request.path,
        "listas_personalizadas_usuario": listas_personalizadas_usuario,
    }
    return render(request, "filmes/lista_filmes.html", context)

def detalhe_filme(request, filme_id):
    detalhes = get_detalhes_filme(filme_id)
    if not detalhes:
        raise Http404(f"Filme com ID {filme_id} não encontrado.")

    is_favorito_atual = False
    listas_personalizadas_usuario = []
    if request.user.is_authenticated:
        is_favorito_atual = ListaFavoritos.objects.filter(usuario=request.user, padrao=True, filmes__id_tmdb=filme_id).exists()
        listas_personalizadas_usuario = list(ListaFavoritos.objects.filter(usuario=request.user, padrao=False).values('id', 'nome'))

    release_year, formatted_release_date, formatted_runtime, trailer_key, diretores, elenco_principal, classificacao_br = "", "", "", None, [], [], "N/D"
    
    if release_date_str := detalhes.get('release_date'):
        try:
            date_obj = datetime.strptime(release_date_str, "%Y-%m-%d")
            release_year = date_obj.year
            formatted_release_date = date_obj.strftime("%d/%m/%Y")
        except ValueError: pass

    if runtime_minutos := detalhes.get("runtime", 0):
        formatted_runtime = f"{runtime_minutos // 60}h {runtime_minutos % 60}m"

    if videos := detalhes.get("videos", {}).get("results"):
        for video in videos:
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                trailer_key = video.get("key")
                if video.get("official"): break

    diretores = [m["name"] for m in detalhes.get("credits", {}).get("crew", []) if m.get("job") == "Director"]
    elenco_principal = detalhes.get("credits", {}).get("cast", [])[:12]
    
    context = {
        "filme": detalhes, "release_year": release_year, "formatted_release_date": formatted_release_date,
        "formatted_runtime": formatted_runtime, "trailer_youtube_key": trailer_key, "diretores": diretores,
        "elenco_principal": elenco_principal, "classificacao_br": classificacao_br,
        "base_poster_url_grande": "https://image.tmdb.org/t/p/w500",
        "base_backdrop_url": "https://image.tmdb.org/t/p/w1280", "base_profile_url": "https://image.tmdb.org/t/p/w185",
        "is_favorito_atual": is_favorito_atual, "listas_personalizadas_usuario": listas_personalizadas_usuario,
    }
    return render(request, "filmes/detalhe_filme.html", context)

def buscar_filmes_view(request):
    query = request.GET.get('q', '').strip()
    page_num = int(request.GET.get("page", "1"))
    
    lista_de_filmes, pagina_atual, total_de_paginas = [], 1, 1
    if query:
        api_response = search_tmdb_filmes(query, page=page_num)
        lista_de_filmes, pagina_atual, total_de_paginas = processar_resposta_api(api_response)
        lista_de_filmes = enrich_filmes_with_favoritos(request, lista_de_filmes)
    
    query_params = request.GET.copy()
    query_params.pop("page", None)
    base_query_string = query_params.urlencode()
    
    listas_personalizadas_usuario = []
    if request.user.is_authenticated:
        listas_personalizadas_usuario = list(ListaFavoritos.objects.filter(usuario=request.user, padrao=False).values('id', 'nome'))
        
    context = {
        "titulo_secao": f"Resultados para: \"{query}\"" if query else "Buscar Filmes",
        "lista_filmes": lista_de_filmes, "pagina_atual": pagina_atual, "total_de_paginas": total_de_paginas,
        "numeros_de_pagina_para_template": gerar_numeros_paginacao(pagina_atual, total_de_paginas),
        "base_poster_url": "https://image.tmdb.org/t/p/w200", "pode_ordenar": False,
        "base_query_string_pagination": base_query_string, "request_path": request.path,
        "search_query": query, "listas_personalizadas_usuario": listas_personalizadas_usuario,
    }
    return render(request, "filmes/lista_filmes.html", context)

@login_required
@require_POST
def toggle_favorito(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        filme_obj, _ = Filme.objects.get_or_create(id_tmdb=int(data.get("id_tmdb")), defaults={"titulo": data.get("titulo"), "poster_path": data.get("poster_path", "")})
        lista_favoritos_padrao, _ = ListaFavoritos.objects.get_or_create(usuario=request.user, padrao=True, defaults={"nome": "Favoritos"})
        
        is_favorito_agora = False
        if filme_obj in lista_favoritos_padrao.filmes.all():
            lista_favoritos_padrao.filmes.remove(filme_obj)
            message = f"'{filme_obj.titulo}' removido dos favoritos."
        else:
            lista_favoritos_padrao.filmes.add(filme_obj)
            message = f"'{filme_obj.titulo}' adicionado aos favoritos!"
            is_favorito_agora = True

        return JsonResponse({"status": "ok", "is_favorito": is_favorito_agora, "message": message})
    except Exception:
        return JsonResponse({"status": "error", "message": "Ocorreu um erro interno."}, status=500)

@login_required
@require_POST
def add_filme_to_list_view(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        filme_obj, _ = Filme.objects.get_or_create(id_tmdb=int(data.get("id_tmdb")), defaults={"titulo": data.get("titulo"), "poster_path": data.get("poster_path", "")})
        lista_obj = ListaFavoritos.objects.get(id=data.get("id_lista"), usuario=request.user, padrao=False)
        
        if filme_obj in lista_obj.filmes.all():
            return JsonResponse({"status": "info", "message": f"'{filme_obj.titulo}' já está na lista '{lista_obj.nome}'."})
        
        lista_obj.filmes.add(filme_obj)
        return JsonResponse({"status": "ok", "message": f"'{filme_obj.titulo}' adicionado a '{lista_obj.nome}' com sucesso!"})

    except ListaFavoritos.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Lista não encontrada ou não pertence a você."}, status=404)
    except Exception:
        return JsonResponse({"status": "error", "message": "Ocorreu um erro interno."}, status=500)

@login_required
@require_POST
def remove_filme_from_list_view(request):
    try:
        data = json.loads(request.body)
        filme_obj = Filme.objects.get(id_tmdb=data.get("id_tmdb"))
        lista_obj = ListaFavoritos.objects.get(id=data.get("id_lista"), usuario=request.user)
        lista_obj.filmes.remove(filme_obj)
        return JsonResponse({"status": "ok", "message": "Filme removido com sucesso."})
    except (Filme.DoesNotExist, ListaFavoritos.DoesNotExist):
        return JsonResponse({"status": "error", "message": "Lista ou filme não encontrado."}, status=404)
    except Exception:
        return JsonResponse({"status": "error", "message": "Um erro inesperado ocorreu"}, status=500)