import time
import random
from functools import wraps
from google.api_core.exceptions import ResourceExhausted

def retry_with_exponential_backoff(
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 5,
):
    """
    A decorator to retry a function with exponential backoff.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay
            while True:
                try:
                    return func(*args, **kwargs)
                except ResourceExhausted as e:
                    num_retries += 1
                    if num_retries > max_retries:
                        raise Exception(
                            f"Maximum number of retries ({max_retries}) exceeded."
                        ) from e
                    
                    delay *= exponential_base * (1 + jitter * random.random())
                    print(f"Rate limit exceeded. Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                except Exception as e:
                    raise e
        return wrapper
    return decorator
