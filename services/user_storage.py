import json
import os


class UserStorage:
    def __init__(self, db_file = "user_settings.json"):
        self.db_file = db_file

    def _load(self):
        if not os.path.exists(self.db_file):
            return {}
        with open(self.db_file, 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)

    def _save(self, data):
        with open(self.db_file, 'w', encoding='utf-8') as file:
            json.dumps(data, indent=2, ensure_ascii=False)

    def set_calendar(self, user_id: int, calendar_id: str):
        data = self._load()
        data[str(user_id)] = calendar_id
        self._save(data)

    def get_calendar(self, user_id: int) -> str:
        data = self._load()
        return data.get(str(user_id))