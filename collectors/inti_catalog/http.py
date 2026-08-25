import time
import requests
from .config import settings

class HttpClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.user_agent,
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.7",
        })

    def get(self, url: str) -> requests.Response:
        response = self.session.get(url, timeout=settings.timeout_seconds)
        response.raise_for_status()
        time.sleep(settings.delay_seconds)
        return response
