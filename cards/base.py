# Abstract ?
# Curse !

class Card:
    def __init__(self):
        self.code = '?'

        self.is_action = False
        self.is_treasure = False
        self.is_attack = False

        self.is_curse = False
        self.is_victory = False

        self.cost = None

        self.value = 0

    @property
    def consider_deck(self):
        return False

    @property
    def consider_discard(self):
        return False

    def __repr__(self):
        return f"<{self.code}>"

class CurseCard(Card):
    def __init__(self):
        super().__init__()
        self.code = '!'
        self.is_curse = True

        self.cost = 0

