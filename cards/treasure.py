from . import Card

class TreasureCard(Card):
    def __init__(self, value):
        super().__init__()
        self.value = value
        self.is_treasure = True

class CopperCard(TreasureCard):
    def __init__(self):
        super().__init__(1)
        self.code = '1'
        self.cost = 0

class SilverCard(TreasureCard):
    def __init__(self):
        super().__init__(2)
        self.code = '2'
        self.cost = 3

class GoldCard(TreasureCard):
    def __init__(self):
        super().__init__(3)
        self.code = '3'
        self.cost = 6

