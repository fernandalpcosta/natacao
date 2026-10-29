"""Cliente mínimo da Garmin Connect Personal API (somente leitura)."""
import json
import os
import urllib.request

BASE = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"


class Garmin:
    def __init__(self, api_key=None):
        # Sem chave, assume que um proxy injeta o cabeçalho ApiKey (sessões do Claude Code).
        self.api_key = api_key if api_key is not None else os.environ.get("GARMIN_PERSONAL_API_KEY")
        self._token = None

    def _request(self, path, method="GET", headers=None):
        req = urllib.request.Request(BASE + path, method=method, headers=headers or {})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read()

    def token(self):
        if self._token is None:
            headers = {"Authorization": f"ApiKey {self.api_key}"} if self.api_key else {}
            self._token = self._request(TOKEN_PATH, method="POST", headers=headers).decode().strip()
        return self._token

    def get(self, path):
        return self._request(path, headers={"Authorization": f"Bearer {self.token()}"})

    def activities(self, start=0, limit=100):
        path = f"/activitylist-service/activities/search/activities?start={start}&limit={limit}"
        return json.loads(self.get(path))

    def all_activities(self, page=100):
        start = 0
        while True:
            batch = self.activities(start, page)
            yield from batch
            if len(batch) < page:
                return
            start += page

    def download(self, activity_id):
        """Arquivo original da atividade, como ZIP (contém o .FIT)."""
        return self.get(f"/download-service/files/activity/{activity_id}")
