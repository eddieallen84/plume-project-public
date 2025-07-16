# PLUME-PROJECT/filmes/utils.py
import requests
from django.conf import settings
from datetime import datetime, timedelta

TMDB_API_KEY = getattr(settings, "TMDB_API_KEY", None)

def buscar_filmes_tmdb(endpoint, params=None):
    if not TMDB_API_KEY:
        # Considere levantar uma exceção ou logar de forma mais robusta
        print("Erro: TMDB_API_KEY não configurada nas settings.")
        return None

    base_url = "https://api.themoviedb.org/3/"
    url = base_url + endpoint

    default_params = {
        "api_key": TMDB_API_KEY,
        "language": "pt-BR", # Consistente com LANGUAGE_CODE
        "region": "BR"       # Para resultados regionalizados se aplicável
    }
    if params:
        default_params.update(params)

    try:
        response = requests.get(url, params=default_params)
        response.raise_for_status()  # Levanta um erro para status HTTP 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        # Logar o erro de forma mais robusta em produção
        print(f"Erro ao buscar dados da API do TMDB ({url}): {e}")
        return None

def get_filmes_populares(page=1, sort_by="popularity.desc"):
    """Busca filmes populares usando o endpoint discover/movie para permitir ordenação."""
    params = {"page": page, "sort_by": sort_by}
    # params['vote_count.gte'] = 200 # Opcional: filtro para popularidade mais significativa
    return buscar_filmes_tmdb("discover/movie", params=params)

def get_filmes_lancamento(page=1, sort_by="popularity.desc"): # Padrão mudado para popularidade
    """Busca filmes em lançamento, permitindo ordenação, usando discover/movie."""
    today = datetime.now()
    future_date_limit = today + timedelta(days=45) # Filmes lançados nos próximos 45 dias

    params = {
        "page": page,
        "sort_by": sort_by,
        "primary_release_date.gte": today.strftime("%Y-%m-%d"),
        "primary_release_date.lte": future_date_limit.strftime("%Y-%m-%d"),
        # "with_release_type": "2|3" # Opcional: Apenas lançamentos de cinema (limitado e geral)
    }
    return buscar_filmes_tmdb("discover/movie", params=params)

def get_lista_generos():
    """Busca a lista completa de gêneros de filmes da API do TMDB."""
    data = buscar_filmes_tmdb("genre/movie/list")
    return data.get("genres", []) if data else [] # Retorna lista vazia se falhar

def get_filmes_por_genero(id_genero, page=1, sort_by="popularity.desc"): # Padrão para popularidade
    """Busca filmes por gênero, permitindo ordenação."""
    params = {"with_genres": str(id_genero), "page": page}
    if sort_by: # Só adiciona sort_by se fornecido, senão usa o default da API (que é popularidade para discover)
        params["sort_by"] = sort_by
    else:
        params["sort_by"] = "popularity.desc" # Garante um default
    return buscar_filmes_tmdb("discover/movie", params=params)

def get_detalhes_filme(filme_id):
    """Busca detalhes de um filme específico."""
    params = {"append_to_response": "credits,videos,images,release_dates"}
    return buscar_filmes_tmdb(f"movie/{filme_id}", params=params)

def search_tmdb_filmes(query, page=1):
    """Busca filmes na API do TMDB com base em uma query de texto."""
    params = {
        "query": query,
        "page": page,
        "include_adult": "false" # Para não incluir conteúdo adulto por padrão
    }
    return buscar_filmes_tmdb("search/movie", params=params)