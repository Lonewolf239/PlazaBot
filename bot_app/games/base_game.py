class BaseGame:
    def __init__(self):
        self.icon = ""
        self.name = {"ru": "", "en": ""}
        self._rules = {"ru": "", "en": ""}
        self.min_bet = 10
        self.max_bet = 200
        self.game_over = False

    async def play(self, bet: int, bonus=False, send_frame=None):
        return

    def rules(self, language: str):
        return self._rules[language]