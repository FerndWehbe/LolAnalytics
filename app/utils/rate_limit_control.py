import time
from collections import deque


class RateLimiter:
    def __init__(
        self,
        lower_limit: int,
        upper_limit: int,
        lower_interval: int,
        upper_interval: int,
    ) -> None:
        """
        Inicializa um limitador de taxa (Rate Limiter).

        Args:
            lower_limit (int): Limite inferior de requisições permitidas.
            upper_limit (int): Limite superior de requisições permitidas.
            lower_interval (int): Intervalo de tempo mínimo entre requisições\
            (em segundos) dentro do limite inferior.
            upper_interval (int): Intervalo de tempo mínimo entre requisições\
            (em segundos) dentro do limite superior.
        """
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.lower_interval = lower_interval
        self.upper_interval = upper_interval
        self.timestamps = deque(maxlen=upper_limit)

    def make_request(self):
        """
        Realiza uma requisição, respeitando os limites estabelecidos pelo Rate\
        Limiter.
        """
        current_time = time.time()

        if len(self.timestamps) >= self.lower_limit:
            time_passed_lower = (
                current_time - self.timestamps[-self.lower_limit]
            )
            if time_passed_lower < self.lower_interval:
                time.sleep(self.lower_interval - time_passed_lower)

        if len(self.timestamps) >= self.upper_limit:
            time_passed_upper = (
                current_time - self.timestamps[-self.upper_limit]
            )
            if time_passed_upper < self.upper_interval:
                time.sleep(self.upper_interval - time_passed_upper)

        self.timestamps.append(current_time)
