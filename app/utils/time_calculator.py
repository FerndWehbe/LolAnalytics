from datetime import datetime


def get_timestamp_from_year(year: int) -> int:
    """
    Obtém o tempo UNIX a partir de um ano específico, representando \
    o início do ano.

    Args:
        year (int): Ano para o qual se deseja obter o tempo.

    Returns:
        int: Carimbo de tempo UNIX correspondente ao início do ano fornecido.
    """
    return int(datetime(year=year, month=1, day=1).timestamp())
