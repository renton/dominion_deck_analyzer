# Estate ev
# Duchy dv
# Province pv

from . import Card

class VictoryCard(Card):
    def __init__(self):
        super().__init__()
        self.is_victory = True
        self.v_points = 0

class EstateCard(VictoryCard):
    def __init__(self):
        super().__init__()
        self.code = 'ev'
        self.v_points = 1
        self.cost = 2

class DuchyCard(VictoryCard):
    def __init__(self):
        super().__init__()
        self.code = 'dv'
        self.v_points = 3
        self.cost = 5

class ProvinceCard(VictoryCard):
    def __init__(self):
        super().__init__()
        self.code = 'pv'
        self.v_points = 6
        self.cost = 8
