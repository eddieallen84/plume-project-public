# PLUME-PROJECT/filmes/utils.py
import requests
from django.conf import settings
from datetime import datetime, timedelta

TMDB_API_KEY = getattr(settings, "TMDB_API_KEY", None)

def buscar_filmes_tmdb(endpoint, params=None):
    if not TMDB_API_KEY:
        print("Erro: TMDB_API_KEY não configurada nas settings.")
        return None

    base_url = "https://api.themoviedb.org/3/"
    url = base_url + endpoint

    default_params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR",
        "region": "BR",
        "include_adult": "false"
    }
    if params:
        default_params.update(params)

    try:
        response = requests.get(url, params=default_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da API do TMDB ({url}): {e}")
        return None

def get_filmes_populares(page=1, sort_by="popularity.desc"):
    """Busca filmes populares usando o endpoint discover/movie para permitir ordenação."""
    params = {
        "page": page, 
        "sort_by": sort_by,
        "vote_count.gte": 50
    }
    return buscar_filmes_tmdb("discover/movie", params=params)

def get_filmes_lancamento(page=1, sort_by="popularity.desc"):
    """Busca filmes em lançamento, permitindo ordenação."""
    today = datetime.now()
    future_date_limit = today + timedelta(days=45) 

    params = {
        "page": page,
        "sort_by": sort_by,
        "primary_release_date.gte": today.strftime("%Y-%m-%d"),
        "primary_release_date.lte": future_date_limit.strftime("%Y-%m-%d"),
        "vote_count.gte": 50
    }
    return buscar_filmes_tmdb("discover/movie", params=params)

def get_lista_generos():
    """Busca a lista completa de gêneros de filmes da API do TMDB."""
    data = buscar_filmes_tmdb("genre/movie/list")
    return data.get("genres", []) if data else []

def get_filmes_por_genero(id_genero, page=1, sort_by="popularity.desc"):
    """Busca filmes por gênero, permitindo ordenação."""
    params = {
        "with_genres": str(id_genero), 
        "page": page,
        "sort_by": sort_by,
        "vote_count.gte": 50
    }
    return buscar_filmes_tmdb("discover/movie", params=params)

def get_detalhes_filme(filme_id):
    """Busca detalhes de um filme específico, incluindo créditos e vídeos."""
    params = {"append_to_response": "credits,videos,images,release_dates"}
    return buscar_filmes_tmdb(f"movie/{filme_id}", params=params)

def search_tmdb_filmes(query, page=1):
    """Busca filmes na API e filtra os resultados para remover os irrelevantes."""
    params = {
        "query": query,
        "page": page,
    }
    # A API de busca não suporta filtro por 'vote_count', então filtramos manualmente.
    api_response = buscar_filmes_tmdb("search/movie", params=params)

    if api_response and "results" in api_response:
        # Cria uma nova lista apenas com filmes que têm 50 ou mais votos.
        filmes_filtrados = [
            filme for filme in api_response["results"] if filme.get("vote_count", 0) >= 50
        ]
        # Substitui a lista de resultados original pela nossa lista filtrada.
        api_response["results"] = filmes_filtrados
    
    return api_response