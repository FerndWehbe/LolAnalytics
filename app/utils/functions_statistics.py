from collections import Counter
from itertools import chain
from statistics import mode

import numpy
import pandas
from mongo import find_matches_by_puuid

player_infos_keys = [
    "totalDamageDealt",
    "totalDamageDealtToChampions",
    "magicDamageDealt",
    "magicDamageDealtToChampions",
    "totalHealsOnTeammates",
    "visionScore",
    "goldEarned",
    "turretTakedowns",
    "visionScore",
    "wardsKilled",
    "wardsPlaced",
    "damageSelfMitigated",
    "killingSprees",
    "largestCriticalStrike",
    "largestKillingSpree",
    "objectivesStolen",
    "totalMinionsKilled",
    "totalTimeCCDealt",
    "totalAllyJungleMinionsKilled",
]

player_challenges_keys = [
    "baronTakedowns",
    "riftHeraldTakedowns",
    "perfectGame",
    "soloBaronKills",
]

team_objectives_key = ["dragon", "baron"]

timestamp_columns = [
    "info.gameCreation",
    "info.gameEndTimestamp",
    "info.gameStartTimestamp",
]

itens_keys = [
    "item0",
    "item1",
    "item2",
    "item3",
    "item4",
    "item5",
    "item6",
]


def convert_to_serializable(dict_convert: dict):
    for key in dict_convert.keys():
        if isinstance(dict_convert[key], dict):
            convert_to_serializable(dict_convert[key])
        if isinstance(dict_convert[key], numpy.float64):
            dict_convert[key] = float(dict_convert[key])
        if isinstance(dict_convert[key], numpy.int64):
            dict_convert[key] = int(dict_convert[key])
    return dict_convert


def add_total_in_dict(dict_data: dict) -> dict:
    """
    Adiciona a chave 'TOTAL' em cada subdicionário de um dicionário, representando
    a soma total dos valores no subdicionário.

    Parâmetros:
    - dict_data (dict): Um dicionário onde as chaves são identificadores e os
      valores são subdicionários.

    Retorna:
    - dict: O dicionário atualizado, onde cada subdicionário agora inclui a chave
      'TOTAL' representando a soma total dos valores no subdicionário.
    """
    for key in dict_data.keys():
        dict_data[key]["TOTAL"] = sum(dict_data[key].values())
    return dict_data


def get_info_participant_value(puuid: str, row: pandas.Series, key: str) -> int:
    """
    Obtém o valor associado à chave especificada para um participante
    específico em uma partida de League of Legends.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame pandas representando
      informações da partida.
    - key (str): O nome da chave do dicionário que representa uma estatística
      da partida de League of Legends.

    Retorna:
    - int: O valor associado à chave para o participante identificado por 'puuid'.
      Se o participante não for encontrado ou a chave não existir, retorna 0.
    """
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return participant.get(key, 0)


def get_info_participant_value_per_mode(
    puuid: str, row: pandas.Series, key: str
) -> tuple[str, int]:
    """
    Obtém o valor associado à chave para um participante específico em uma
    partida de League of Legends, juntamente com o modo de jogo correspondente.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame pandas representando
      informações da partida.
    - key (str): O nome da chave do dicionário que representa uma estatística
      da partida de League of Legends.

    Retorna:
    - tuple: Uma tupla contendo o modo de jogo (game_mode) e o valor associado
      à chave para o participante identificado por 'puuid'. Se o participante
      não for encontrado ou a chave não existir, o valor é 0.
    """
    game_mode = row.get("info.gameMode")
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return (game_mode, participant.get(key, 0))


def get_info_team_id_and_match_id_from_player(puuid: str, row: pandas.Series, key: str):
    """
    Obtém o identificador da partida (match_id) e o valor associado à chave para
    um jogador específico em uma partida de League of Legends.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame pandas representando
      informações da partida.
    - key (str): O nome da chave do dicionário que representa uma estatística
      da partida de League of Legends.

    Retorna:
    - tuple: Uma tupla contendo o identificador da partida (match_id) e o valor
      associado à chave para o jogador identificado por 'puuid'. Se o jogador
      não for encontrado ou a chave não existir, o valor é 0.
    """
    match_id = row.get("metadata.matchId")
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return (match_id, participant.get(key, 0))


def get_info_team_objectives(
    row: pandas.Series, key: str, df_team_played: pandas.DataFrame
):
    """
    Obtém a quantidade de kills associada a um objetivo específico de equipe em
    uma partida de League of Legends.

    A função utiliza as informações contidas na série de dados da partida e no
    DataFrame 'df_team_played' para identificar a equipe do jogador na partida.
    Em seguida, recupera as estatísticas associadas ao objetivo específico dessa
    equipe e retorna a quantidade de kills.

    Parâmetros:
    - row (pandas.Series): Uma linha do DataFrame contendo informações sobre a
      partida de League of Legends.
    - key (str): A chave do objetivo específico de equipe desejado
    (e.g., 'BARON_NASHOR_KILL').
    - df_team_played (pandas.DataFrame): O DataFrame contendo informações sobre
      as equipes que participaram das partidas de League of Legends.

    Retorna:
    - int: A quantidade de kills associada ao objetivo específico da equipe na partida.
    """
    match_id = row.get("metadata.matchId")
    teams = row.get("info.teams", [])
    for team in teams:
        if (
            team.get("teamId")
            == df_team_played.loc[df_team_played["matchId"] == match_id, "teamId"].iloc[
                0
            ]
        ):
            objectives = team.get("objectives", {})
            return objectives.get(key, {}).get("kills", 0)


def get_info_player_challengers_per_game_mode(
    puuid: str, row: pandas.Series, keys: list[str]
):
    """
    Obtém as estatísticas de desafios de um jogador em uma partida de League of
    Legends por modo de jogo.

    Para o jogador identificado pelo PUUID fornecido, a função procura na série de
    dados da partida por estatísticas de desafios correspondentes às chaves
    fornecidas. Retorna uma tupla contendo o modo de jogo e um dicionário com as
    estatísticas de desafios para cada chave.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame contendo informações sobre a
      partida de League of Legends.
    - keys (list): Uma lista de chaves representando os desafios desejados.

    Retorna:
    - tuple: Uma tupla contendo o modo de jogo e um dicionário com as estatísticas
      de desafios para cada chave, correspondentes ao participante identificado
      pelo PUUID na partida.
    """
    game_mode = row.get("info.gameMode")
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return (
                game_mode,
                {key: participant.get("challenges", {}).get(key, 0) for key in keys},
            )


def get_infos_parcipant_value_in_list(
    puuid: str, row: pandas.Series, keys: list[str]
) -> list:
    """
    Obtém os valores das estatísticas de um participante em uma partida de League
    of Legends, com base nas chaves especificadas.

    Para o jogador identificado pelo PUUID fornecido, a função procura na série
    de dados da partida por estatísticas correspondentes às chaves fornecidas.
    Retorna uma lista dos valores encontrados para cada chave.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame contendo informações sobre a
      partida de League of Legends.
    - keys (list): Uma lista de chaves representando as estatísticas desejadas.

    Retorna:
    - list: Uma lista contendo os valores correspondentes às estatísticas
      especificadas para o participante identificado pelo PUUID.
    """
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return [participant.get(key) for key in keys if participant.get(key)]


def get_infos_parcipant_value_in_list_per_mode(
    puuid: str, row: pandas.Series, keys: list[str]
) -> tuple:
    """
    Obtém os valores das estatísticas de um participante em uma partida de League
    of Legends, com base nas chaves especificadas, juntamente com o modo de jogo.

    Para o jogador identificado pelo PUUID fornecido, a função procura na série
    de dados da partida por estatísticas correspondentes às chaves fornecidas.
    Retorna uma tupla contendo o modo de jogo e uma lista dos valores encontrados
    para cada chave.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame contendo informações sobre a
      partida de League of Legends.
    - keys (list): Uma lista de chaves representando as estatísticas desejadas.

    Retorna:
    - tuple: Uma tupla contendo o modo de jogo e uma lista dos valores
      correspondentes às estatísticas especificadas para o participante identificado
      pelo PUUID.
    """
    game_mode = row.get("info.gameMode")
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return (
                game_mode,
                [participant.get(key) for key in keys if participant.get(key)],
            )


def get_multiple_kills(
    puuid: str, df: pandas.DataFrame, type_kills: str
) -> pandas.DataFrame:
    """
    Calcula o número total de kills de um determinado tipo por modo de jogo para
    um jogador específico.

    A função utiliza o DataFrame fornecido e o identificador único (PUUID) do
    jogador juntamente com a função auxiliar 'get_info_participant_value_per_mode'
    para obter o número de kills do tipo especificado para cada partida do jogador.
    Esses valores são somados por modo de jogo.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.
    - type_kills (str): O tipo de kills desejado (e.g., 'doubleKills', 'tripleKills').

    Retorna:
    - pandas.DataFrame: Um DataFrame contendo o número total de kills do tipo
      especificado por modo de jogo, onde as colunas são 'gameMode' e o tipo
      de kills, e as linhas representam os modos de jogo.
    """
    mult_kill = df.apply(
        lambda row: get_info_participant_value_per_mode(puuid, row, type_kills), axis=1
    ).to_list()
    return (
        pandas.DataFrame(mult_kill, columns=["gameMode", type_kills])
        .groupby(by="gameMode")
        .sum()
    )


def get_team_side_per_mode(df: pandas.DataFrame) -> dict[dict[str, int]]:
    """
    Obtém um dicionário representando o número de ocorrências de cada combinação
    de modo de jogo e lado da equipe em um DataFrame pandas.

    Parâmetros:
    - df (pandas.DataFrame): Um DataFrame pandas contendo informações sobre
      partidas de League of Legends.

    Retorna:
    - dict: Um dicionário onde as chaves são Id do Time (teamId) e os valores
      são dicionarios que as chaves são modos de jogo e os valores são
      a quantidade de partidas.
    """
    team_side = df.apply(
        lambda row: get_info_participant_value_per_mode(row, "teamId"), axis=1
    )

    return (
        pandas.DataFrame(team_side.to_list(), columns=["gameMode", "teamId"])
        .groupby(by=["gameMode", "teamId"])
        .size()
        .unstack(fill_value=0)
        .to_dict()
    )


def get_player_kda_per_mode(puuid: str, df: pandas.DataFrame) -> dict:
    """
    Calcula e retorna o KDA (Kills, Deaths, Assists) por modo de jogo para um
    jogador específico.

    Para cada estatística (Kills, Deaths, Assists), a função cria um DataFrame
    contendo a soma da estatística para cada modo de jogo. Os DataFrames
    resultantes são concatenados ao longo do eixo horizontal, gerando um
    DataFrame final com as estatísticas KDA para cada modo de jogo.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of
      Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.

    Retorna:
    - dict: Um dicionário contendo as estatísticas KDA por modo de jogo, onde
      as chaves são as estatísticas (kills, deaths, assists) e os valores são
      subdicionários com os modos de jogo como chaves e os totais de cada
      estatística para cada modo. Cada subdicionário também inclui uma chave
      'TOTAL' que representa a soma total da estatística para todos os modos
      de jogo.
    """
    list_df_kda = [
        (
            pandas.DataFrame(
                df.apply(
                    lambda row: get_info_participant_value_per_mode(
                        puuid, row, tp_stats
                    ),
                    axis=1,
                ).to_list(),
                columns=["gameMode", tp_stats],
            )
            .groupby(by="gameMode")
            .sum()
        )
        for tp_stats in ["kills", "deaths", "assists"]
    ]
    df_kda = pandas.concat(list_df_kda, axis=1, sort=True)
    dict_kda = df_kda.to_dict()
    dict_kda = add_total_in_dict(dict_kda)
    return dict_kda


def game_by_side_per_mode(puuid: str, df: pandas.DataFrame) -> dict:
    """
    Conta o número de partidas jogadas por modo de jogo e lado da equipe para um
    jogador específico.

    Para cada modo de jogo, a função cria um DataFrame contendo a contagem de
    partidas para cada lado da equipe. Os DataFrames resultantes são
    consolidados em um dicionário onde as chaves são tuplas (gameMode, teamId)
    e os valores são os totais de partidas para cada combinação. Cada subdicionário
    também inclui uma chave 'TOTAL' que representa a soma total de partidas para
    o modo de jogo correspondente.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.

    Retorna:
    - dict: Um dicionário contendo o número de partidas jogadas por modo de jogo
      e lado da equipe, onde as chaves são tuplas (gameMode, teamId) e os valores
      são subdicionários com os lados da equipe como chaves e os totais de partidas
      para cada lado. Cada subdicionário também inclui uma chave 'TOTAL' que
      representa a soma total de partidas para o modo de jogo correspondente.
    """
    dict_side = (
        pandas.DataFrame(
            df.apply(
                lambda row: get_info_participant_value_per_mode(puuid, row, "teamId"),
                axis=1,
            ).to_list(),
            columns=["gameMode", "teamId"],
        )
        .groupby(by=["gameMode", "teamId"])
        .size()
        .unstack(fill_value=0)
        .to_dict()
    )
    dict_side = add_total_in_dict(dict_side)
    return dict_side


def get_multi_kills_per_mode(puuid: str, df: pandas.DataFrame) -> dict:
    """
    Calcula o número total de multi-kills (double, triple, quadra, penta) por
    modo de jogo para um jogador específico.

    A função utiliza a função auxiliar 'get_multiple_kills' para obter o número
    de kills de cada tipo para cada modo de jogo. Os resultados são consolidados
    em um dicionário onde as chaves são os tipos de kills e os valores são
    subdicionários com os modos de jogo como chaves e os totais de cada tipo
    de kills para cada modo. Cada subdicionário também inclui uma chave 'TOTAL'
    que representa a soma total de kills para o tipo correspondente.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.

    Retorna:
    - dict: Um dicionário contendo o número total de multi-kills (double, triple,
      quadra, penta) por modo de jogo, onde as chaves são os tipos de kills e
      os valores são subdicionários com os modos de jogo como chaves e os totais
      de cada tipo de kills para cada modo. Cada subdicionário também inclui uma
      chave 'TOTAL' que representa a soma total de kills para o tipo correspondente.
    """
    list_multi_kills = [
        get_multiple_kills(puuid, df, type_kills)
        for type_kills in ["doubleKills", "tripleKills", "quadraKills", "pentaKills"]
    ]
    df_multi_kills = pandas.concat(list_multi_kills, axis=1, sort=True)

    dict_multi_kills = df_multi_kills.to_dict()
    dict_multi_kills = add_total_in_dict(dict_multi_kills)

    return dict_multi_kills


def get_first_blood_amount_per_mode(puuid: str, df: pandas.DataFrame) -> dict:
    """
    Calcula o número total de first blood kills por modo de jogo para um jogador
    específico.

    A função utiliza a função auxiliar 'get_info_participant_value_per_mode'
    para obter o número de first blood kills para cada modo de jogo. Os resultados
    são consolidados em um dicionário onde as chaves são os modos de jogo e os
    valores são os totais de first blood kills para cada modo. Cada valor também
    inclui uma chave 'TOTAL' que representa a soma total de first blood kills para
    o modo correspondente.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.

    Retorna:
    - dict: Um dicionário contendo o número total de first blood kills por modo
      de jogo, onde as chaves são os modos de jogo e os valores são os totais de
      first blood kills para cada modo. Cada valor também inclui uma chave 'TOTAL'
      que representa a soma total de first blood kills para o modo correspondente.
    """
    df_first_blood = (
        pandas.DataFrame(
            df.apply(
                lambda row: get_info_participant_value_per_mode(
                    puuid, row, "firstBloodKill"
                ),
                axis=1,
            ).to_list(),
            columns=["gameMode", "firstBloodKill"],
        )
        .groupby(by="gameMode")
        .sum()
    )
    dict_first_blood = df_first_blood.to_dict()
    dict_first_blood = add_total_in_dict(dict_first_blood)

    return dict_first_blood


def general_infos(df: pandas.DataFrame) -> dict:
    """
    Calcula informações gerais com base no DataFrame de partidas de League of Legends.

    Realiza operações como:
    1. Calcula a duração do jogo em segundos e adiciona a coluna
        'info.gameDurationSeconds' ao DataFrame.
    2. Calcula o total de horas jogadas com base na coluna 'info.gameDurationHours'
        do DataFrame.
    3. Conta o número de partidas jogadas por modo de jogo e retorna um dicionário.
    4. Adiciona a coluna 'info.date' ao DataFrame representando a data da criação
        da partida.
    5. Ordena o DataFrame com base na coluna 'info.gameCreation'.

    Retorna uma tupla com informações como total de horas jogadas,
    partidas por modo de jogo, máximo de partidas jogadas em um único dia,
    máximo de dias consecutivos com partidas jogadas,
    máximo de dias sem jogar entre partidas.

    Parâmetros:
    - df (pandas.DataFrame): DataFrame contendo informações sobre as partidas
        de League of Legends.

    Retorna:
    - dict: Dicionario contendo informações mencionadas acima.
    """

    df_infos = df.copy()
    df_infos["info.gameDurationSeconds"] = df_infos["info.gameDuration"]
    df_infos.loc[
        pandas.isnull(df_infos["info.gameEndTimestamp"]), "info.gameDurationSeconds"
    ] = (
        df_infos.loc[
            pandas.isnull(df_infos["info.gameEndTimestamp"]), "info.gameDuration"
        ]
        / 1000
    )
    df_infos["info.gameDurationHours"] = df_infos["info.gameDurationSeconds"] / 60 / 60

    hours_played = df_infos["info.gameDurationHours"].sum()

    played_per_game_mode = df_infos["info.gameMode"].value_counts().to_dict()

    df_infos["info.date"] = df_infos["info.gameCreation"].dt.date

    df_infos.sort_values(by="info.gameCreation", inplace=True)

    max_matchs_in_one_day = df_infos.groupby(by="info.date").size().max()

    df_infos["info.group"] = (
        df_infos["info.date"] != df_infos["info.date"].shift()
    ).cumsum()

    max_consecutive_days = df_infos.groupby(by="info.group").size().max()

    max_days_without_playing = df_infos["info.gameCreation"].diff().dt.days.max()
    max_days_without_playing = (
        int(max_days_without_playing)
        if max_days_without_playing
        else max_days_without_playing
    )

    return {
        "hours_played": hours_played,
        "played_per_game_mode": played_per_game_mode,
        "max_matchs_in_one_day": max_matchs_in_one_day,
        "max_consecutive_days": max_consecutive_days,
        "max_days_without_playing": max_days_without_playing,
    }


def get_itens_statistics(puuid: str, df: pandas.DataFrame) -> dict:
    """
    Calcula as estatísticas dos itens mais usados por modo de jogo para um jogador
    específico.

    A função utiliza a função auxiliar 'get_infos_participant_value_in_list_per_mode'
    para obter a lista de itens utilizados por cada jogador em cada partida.
    Os resultados são consolidados em um dicionário onde as chaves são os modos de
    jogo e os valores são as listas de itens mais utilizados para cada modo.
    Além disso, a função calcula o item mais utilizado (moda) para cada modo e
    retorna um dicionário com essas informações.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.

    Retorna:
    - dict: Um dicionário contendo as estatísticas dos itens mais usados por modo
      de jogo, onde as chaves são os modos de jogo e os valores são as listas de
      itens mais utilizados para cada modo. Cada valor também inclui uma chave
      'TOTAL' que representa a lista total de itens utilizados para o modo
      correspondente.
    """
    dict_list_itens = (
        pandas.DataFrame(
            df.apply(
                lambda row: get_infos_parcipant_value_in_list_per_mode(
                    puuid, row, itens_keys
                ),
                axis=1,
            ).to_list(),
            columns=["gameMode", "list_itens"],
        )
        .groupby(by="gameMode")
        .sum()
        .to_dict()
    )
    for key in dict_list_itens.keys():
        dict_list_itens[key]["TOTAL"] = list(chain(*dict_list_itens[key].values()))
    dict_itens_most_used = {
        key: mode(value)
        for key, value in dict_list_itens["list_itens"].items()
        if value
    }
    return dict_itens_most_used


def get_infos_by_team(df: pandas.DataFrame, df_team: pandas.DataFrame) -> dict:
    """
    Calcula estatísticas globais de objetivos por equipe em partidas de League
    of Legends.

    A função utiliza a função auxiliar 'get_info_team_objectives' para obter a
    quantidade total de kills associada a objetivos específicos de equipe para
    todas as partidas no DataFrame 'df'. Os resultados são consolidados em um
    dicionário onde as chaves são os objetivos de equipe e os valores são as
    quantidades totais de kills para cada objetivo.

    Parâmetros:
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.
    - df_team (pandas.DataFrame): O DataFrame contendo informações sobre as
      equipes que participaram das partidas de League of Legends.

    Retorna:
    - dict: Um dicionário contendo estatísticas globais de kills associadas a
      objetivos de equipe para todas as partidas, onde as chaves são os objetivos
      de equipe e os valores são as quantidades totais de kills para cada objetivo.
    """
    return {
        key: int(
            df.apply(
                lambda row: get_info_team_objectives(row, key, df_team), axis=1
            ).sum()
        )
        for key in team_objectives_key
    }


def get_players_same_team(
    puuid: str, row: pandas.Series, df_team_played: pandas.DataFrame
) -> list:
    match_id = row.get("metadata.matchId")
    participants = row.get("info.participants")
    return [
        participant.get("puuid")
        for participant in participants
        if (
            participant.get("teamId")
            == df_team_played.loc[df_team_played["matchId"] == match_id, "teamId"].iloc[
                0
            ]
        )
        and participant.get("puuid") != puuid
    ]


def get_infos_other_players_frequency(
    puuid: str, df: pandas.DataFrame, df_team_played: pandas.DataFrame
):
    most_commom_player = Counter(
        filter(
            lambda x: x != puuid,
            chain(
                *df.apply(lambda row: row.get("metadata.participants"), axis=1).tolist()
            ),
        )
    ).most_common(5)
    most_commoms_player_same_time = Counter(
        chain(
            *df.apply(
                lambda row: get_players_same_team(puuid, row, df_team_played), axis=1
            ).to_list()
        )
    ).most_common(5)

    return {
        "most_commoms_player": most_commom_player,
        "most_commoms_player_same_time": most_commoms_player_same_time,
    }


def get_player_role_win_info(puuid: str, row: pandas.Series):
    """
    Obtém informações sobre a vitória e posição de um jogador em uma partida de
    League of Legends.

    Para o jogador identificado pelo PUUID fornecido, a função procura na série de
    dados da partida por informações correspondentes à vitória e posição do
    participante. Retorna uma tupla contendo as informações de vitória e posição.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - row (pandas.Series): Uma linha do DataFrame contendo informações sobre a
      partida de League of Legends.

    Retorna:
    - tuple: Uma tupla contendo informações sobre a vitória e posição do jogador
      na partida, ou (None, None) se o jogador não for encontrado na partida.
    """
    participants = row.get("info.participants", [])
    for participant in participants:
        if participant.get("puuid") == puuid:
            return (participant.get("win", None), participant.get("teamPosition", None))


def get_player_info_per_role(puuid: str, df: pandas.DataFrame) -> dict:
    """
    Calcula estatísticas por posição de um jogador em partidas de League of Legends.

    A função utiliza a função auxiliar 'get_player_role_win_info' para obter informações
    sobre a vitória e posição de um jogador em cada partida. Os resultados são
    consolidados em um dicionário onde as chaves são as posições e os valores são
    dicionários contendo a quantidade de partidas jogadas e a taxa de vitória para
    cada posição.

    Parâmetros:
    - puuid (str): O identificador único (PUUID) do jogador de League of Legends.
    - df (pandas.DataFrame): O DataFrame contendo informações sobre as partidas
      de League of Legends.

    Retorna:
    - dict: Um dicionário contendo estatísticas por posição de um jogador em
      partidas de League of Legends. As chaves são as posições e os valores são
      dicionários contendo a quantidade de partidas jogadas e a taxa de vitória
      para cada posição.
    """
    df_roles = pandas.DataFrame(
        df.apply(lambda row: get_player_role_win_info(puuid, row), axis=1).to_list(),
        columns=["win", "role"],
    )

    df_roles = df_roles[df_roles["role"] != ""].reset_index(drop=True)
    return {
        "amount_matchs": {**df_roles.groupby("role")["win"].count().to_dict()},
        "win_rate": {**(df_roles.groupby("role")["win"].mean() * 100).to_dict()},
    }


def get_other_stats(puuid, df: pandas.DataFrame, calculation_function) -> dict:
    other_statistics = {}
    for key in player_infos_keys:
        other_statistics.update(
            add_total_in_dict(
                pandas.DataFrame(
                    df.apply(
                        lambda row: get_info_participant_value_per_mode(
                            puuid, row, key
                        ),
                        axis=1,
                    ).to_list(),
                    columns=["gameMode", key],
                )
                .groupby(by="gameMode")
                .agg(calculation_function)
                .to_dict()
            )
        )

    return other_statistics


def get_other_mean(puuid, df: pandas.DataFrame) -> dict:
    return get_other_stats(puuid, df, "mean")


def get_other_total(puuid, df: pandas.DataFrame) -> dict:
    return get_other_stats(puuid, df, "sum")


def get_challenges_per_mode(puuid: str, df: pandas.DataFrame):
    dict_challenges = df.apply(
        lambda row: get_info_player_challengers_per_game_mode(
            puuid, row, player_challenges_keys
        ),
        axis=1,
    )

    df_result = pandas.DataFrame(
        dict_challenges.to_list(), columns=["gameMode", "valores"]
    )
    df_result = (
        pandas.concat([df_result, pandas.json_normalize(df_result["valores"])], axis=1)
        .drop("valores", axis=1)
        .groupby(by="gameMode")
        .sum()
    )

    return df_result.to_dict()


def create_rewind(puuid: str, timestamp_statistic: int = None):
    list_matchs = find_matches_by_puuid(puuid, timestamp_statistic)
    matchs_data_frame = pandas.DataFrame(list_matchs)
    normalized_matchs_data_frame = pandas.json_normalize(
        matchs_data_frame["first_document"]
    )
    normalized_matchs_data_frame[timestamp_columns] = (
        normalized_matchs_data_frame[timestamp_columns]
        .apply(lambda x: pandas.to_datetime(x, unit="ms"))
        .sort_values(by="info.gameCreation")
    )
    normalized_matchs_data_frame.reset_index(drop=True, inplace=True)

    df_team_played = pandas.DataFrame(
        normalized_matchs_data_frame.apply(
            lambda row: get_info_team_id_and_match_id_from_player(puuid, row, "teamId"),
            axis=1,
        ).to_list(),
        columns=["matchId", "teamId"],
    )

    challenges = get_challenges_per_mode(puuid, normalized_matchs_data_frame)

    dict_kda = get_player_kda_per_mode(puuid, normalized_matchs_data_frame)
    dict_side = game_by_side_per_mode(puuid, normalized_matchs_data_frame)
    dict_multi_kills = get_multi_kills_per_mode(puuid, normalized_matchs_data_frame)
    dict_first_blood = get_first_blood_amount_per_mode(
        puuid, normalized_matchs_data_frame
    )

    itens_statistics = get_itens_statistics(puuid, normalized_matchs_data_frame)

    team_statistics = get_infos_by_team(normalized_matchs_data_frame, df_team_played)

    other_totals = get_other_total(puuid, normalized_matchs_data_frame)

    other_means = get_other_mean(puuid, normalized_matchs_data_frame)

    infos = general_infos(normalized_matchs_data_frame)

    other_infos_players = get_infos_other_players_frequency(
        puuid, normalized_matchs_data_frame, df_team_played
    )
    dict_player_role_win_info = get_player_info_per_role(
        puuid, normalized_matchs_data_frame
    )

    result_dict = {
        "kda_infos": dict_kda,
        "side_infos": dict_side,
        "multi_kills_infos": dict_multi_kills,
        "first_blood_infos": dict_first_blood,
        "general_infos": infos,
        "itens_statistics": itens_statistics,
        "team_statistics": team_statistics,
        "challenges": challenges,
        "other_totals": other_totals,
        "other_means": other_means,
        "other_infos_players": other_infos_players,
        "player_role_win_info": dict_player_role_win_info,
    }
    return convert_to_serializable(result_dict)
