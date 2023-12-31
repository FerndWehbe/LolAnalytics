from statistics import mode
from typing import Any, Dict, List

import pandas as pd

dataframe = pd.read_json('dados_3.json')
df = pd.json_normalize(dataframe['first_document'])

desired_puuid = 'iky0yLxZGmaRShc8AqqvDQu_reHaEFFL3nlmles8jYCJGJ4CcGJxR69Ndsns3PTCJ2iVd4Mw_K-xeA'


def calculate_baron_takedowns(participants: List[Dict[str, Any]], desired_puuid: str) -> int:
    """
    Calcula o total de baronTakedowns para um participante específico.
    
    Args:
    - participants: Lista de participantes em uma partida.
    - desired_puuid: UUID do participante desejado.
    
    Returns:
    - int: Total de baronTakedowns para o participante especificado.
    """
    return sum(p.get('challenges', {}).get('baronTakedowns', 0) 
               for p in participants if p.get('puuid') == desired_puuid)


def calculate_participant_totals(df: pd.DataFrame, keys: List[str], desired_puuid: str) -> Dict[str, int]:
    """
    Calcula os totais para chaves específicas de um participante em todas as partidas.
    
    Args:
    - df: DataFrame com os dados.
    - keys: Lista de chaves para calcular os totais.
    - desired_puuid: UUID do participante desejado.
    
    Returns:
    - dict: Dicionário com os totais calculados para cada chave.
    """
    for key in keys:
        if key == 'baronTakedowns':
            df[key] = df['info.participants'].apply(lambda x: calculate_baron_takedowns(x, desired_puuid))
        else:
            df[key] = df['info.participants'].apply(lambda x: sum(p.get(key, 0) for p in x if p.get('puuid') == desired_puuid))
    return df[keys].sum().to_dict()


def extract_participant_items(df: pd.DataFrame, desired_puuid: str, keys: List[str]) -> List[Any]:
    """
    Extrai itens específicos de um participante em todas as partidas.
    
    Args:
    - df: DataFrame com os dados.
    - desired_puuid: UUID do participante desejado.
    - keys: Lista de chaves dos itens a serem extraídos.
    
    Returns:
    - list: Lista de itens específicos do participante.
    """
    items = []
    for index, row in df.iterrows():
        participants = row.get('info.participants', [])
        for participant in participants:
            if participant.get('puuid') == desired_puuid:
                items.extend([participant.get(key, None) for key in keys if participant.get(key) is not None])
    return items


def get_champions_lost_most(df: pd.DataFrame, desired_puuid: str) -> List[str]:
    """
    Obtém campeões mais frequentemente perdidos por um participante em todas as partidas.
    
    Args:
    - df: DataFrame com os dados.
    - desired_puuid: UUID do participante desejado.
    
    Returns:
    - list: Lista dos nomes dos campeões mais frequentemente perdidos pelo participante.
    """
    losing_team_champions = []
    for _, row in df.iterrows():
        participants = row.get('info.participants', [])
        participant_data = next((p for p in participants if p.get('puuid') == desired_puuid and p.get('win')), None)
        if participant_data:
            losing_team_champions.extend([p.get('championName', '') for p in participants 
                                          if not p.get('win') and p.get('puuid') != desired_puuid])
    return losing_team_champions


if __name__ == "__main__":
    keys_to_find_mode = ['item0', 'item1', 'item2', 'item3', 'item4', 'item5', 'item6']

    keys_to_calculate = [
        'totalDamageDealt', 'totalDamageDealtToChampions', 'magicDamageDealt',
        'magicDamageDealtToChampions', 'totalHealsOnTeammates', 'visionScore',
        'goldEarned', 'turretTakedowns', 'baronTakedowns'
    ]

    totals = calculate_participant_totals(df, keys_to_calculate, desired_puuid)
    participant_items = extract_participant_items(df, desired_puuid, keys_to_find_mode)
    mode_result = mode(participant_items)
    lost_champions_mode = mode(get_champions_lost_most(df, desired_puuid))

    print(totals, mode_result, lost_champions_mode)
