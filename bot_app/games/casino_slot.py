from .base_game import BaseGame


class CasinoSlot(BaseGame):
    def __init__(self):
        super().__init__()
        self.icon = "🎰"
        self._name = {"ru": "Слот-машина", "en": "Slot machine"}
        self._rules = {
            "ru": "ℹ️ Правила слота\n"
                  "— 3× 7️⃣: ставка × 20\n"
                  "— 3× 💎: ставка × 10\n"
                  "— 3× 🔔: ставка × 5\n"
                  "— 3 одинаковых фрукта: ставка × 2–4\n"
                  "— 2 одинаковых фрукта: ставка × 1\n",
            "en": "ℹ️ Slot Rules\n"
                  "— 3× 7️⃣: bet × 20\n"
                  "— 3× 💎: bet × 10\n"
                  "— 3× 🔔: bet × 5\n"
                  "— 3 identical fruits: bet × 2–4\n"
                  "— 2 identical fruits: bet × 1\n"
        }
        self.fruits = ['🍒', '🍋', '🍊', '🍇', '🍉']
        self.symbols = {
            '🍒': 1,
            '🍋': 1,
            '🍊': 1,
            '🍇': 2,
            '🍉': 2,
            '🔔': 5,
            '💎': 8,
            '7️⃣': 15
        }
