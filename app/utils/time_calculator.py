from datetime import datetime


def get_timestamp_from_year(year: int) -> int:
    return int(datetime(year=year, month=1, day=1).timestamp())
