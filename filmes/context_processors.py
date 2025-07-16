# PLUME-PROJECT/filmes/context_processors.py
from .utils import get_lista_generos

def custom_genres_processor(request):
    all_tmdb_genres_list = get_lista_generos() # Função que busca todos os gêneros da TMDB

    # Defina a ordem e os nomes de exibição desejados para os gêneros principais
    # Os IDs são importantes para gerar os links corretos.
    # IDs comuns da TMDB:
    # Ação: 28, Aventura: 12, Animação: 16, Comédia: 35, Crime: 80, Drama: 18,
    # Terror (Horror): 27, Ficção Científica (Science Fiction): 878, Suspense (Thriller): 53
    desired_genres_config = [
        {'tmdb_id': 28, 'display_name': 'Ação'},
        {'tmdb_id': 12, 'display_name': 'Aventura'},
        {'tmdb_id': 16, 'display_name': 'Animação'},
        {'tmdb_id': 35, 'display_name': 'Comédia'},
        {'tmdb_id': 18, 'display_name': 'Drama'},
        {'tmdb_id': 80, 'display_name': 'Policial'},      # "Crime" (80) renomeado
        {'tmdb_id': 53, 'display_name': 'Suspense'},    # "Thriller" (53)
        {'tmdb_id': 878, 'display_name': 'Ficção Científica'}, # "Science Fiction" (878)
        {'tmdb_id': 27, 'display_name': 'Terror'},        # "Horror" (27)
    ]

    generos_menu_para_exibir = []
    if all_tmdb_genres_list: # Verifica se a API retornou algo
        for desired_config in desired_genres_config:
            # Confirma se o ID do gênero desejado existe na lista completa da TMDB
            # para garantir que estamos lidando com um gênero válido
            found_genre_from_tmdb = next((g for g in all_tmdb_genres_list if g['id'] == desired_config['tmdb_id']), None)
            if found_genre_from_tmdb:
                generos_menu_para_exibir.append({
                    'id': desired_config['tmdb_id'],
                    'name': desired_config['display_name'] # Usa o nome de exibição que você definiu
                })
            # else:
            #     print(f"Aviso: Gênero com ID {desired_config['tmdb_id']} não encontrado na lista da TMDB.")

    # Se, por algum motivo, a lista processada estiver vazia mas a API retornou gêneros,
    # podemos usar um fallback, mas o ideal é que a configuração acima funcione.
    # if not generos_menu_para_exibir and all_tmdb_genres_list:
    #     generos_menu_para_exibir = all_tmdb_genres_list

    return {'generos_menu_para_exibir': generos_menu_para_exibir}