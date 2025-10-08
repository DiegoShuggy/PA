import time
from functools import wraps

class CircuitBreakerOpen(Exception):
    pass

class RetryManager:
    def __init__(self, retries=3, delay=1, circuit_breaker_threshold=5, fallback=None):
        self.retries = retries
        self.delay = delay
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.fallback = fallback
        self.failure_count = 0
        self.circuit_open = False

    def retry(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.circuit_open:
                if self.fallback:
                    return self.fallback(*args, **kwargs)
                raise CircuitBreakerOpen("Circuit breaker is open.")
            attempts = 0
            while attempts < self.retries:
                try:
                    result = func(*args, **kwargs)
                    self.failure_count = 0  # Reset on success
                    return result
                except Exception as e:
                    self.failure_count += 1
                    attempts += 1
                    if self.failure_count >= self.circuit_breaker_threshold:
                        self.circuit_open = True
                        if self.fallback:
                            return self.fallback(*args, **kwargs)
                        raise CircuitBreakerOpen("Circuit breaker is open.")
                    time.sleep(self.delay)
            # Si falla todos los intentos
            if self.fallback:
                return self.fallback(*args, **kwargs)
            raise Exception(f"Failed after {self.retries} retries.")
        return wrapper

    def reset_circuit(self):
        self.failure_count = 0
        self.circuit_open = False

# Ejemplo de uso:
if __name__ == "__main__":
    retry_manager = RetryManager(retries=3, delay=1, circuit_breaker_threshold=3, fallback=lambda: "Respuesta alternativa")

    intentos = {"count": 0}

    @retry_manager.retry
    def funcion_inestable():
        intentos["count"] += 1
        print(f"Intento número {intentos['count']}")
        if intentos["count"] < 2:
            raise ValueError("Error simulado")
        return "¡Éxito en el intento!"

    try:
        print(funcion_inestable())
    except Exception as e:
        print(f"Error final: {e}")