class BaseGame:
    def __init__(self):
        self.icon = ""
        self._name = {"ru": "", "en": ""}
        self._rules = {"ru": "", "en": ""}
        self.game_over = False

    async def play(self, bet: int, bonus=False, send_frame=None):
        return

    def name(self, language: str):
        return self._name[language]

    def rules(self, language: str):
        return self._rules[language]