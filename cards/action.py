from . import Card

class ActionCard(Card):
    def __init__(self):
        super().__init__()
        self.is_action = True
        self.add_actions = 0
        self.add_cards = 0
        self.add_buys = 0
        self.add_money = 0

        self.is_attack = False
        self.is_gain4 = False

    # TODO what if a cont. was played first than a terminal?
    @property
    def consider_deck(self):
        return self.add_cards > 0

    def is_terminal(self):
        return self.add_actions <= 0

class MilitiaCard(ActionCard):
    def __init__(self):
        super().__init__()
        self.add_money = 2
        self.is_attack = True
        self.code = 'Mt'

class WorkshopCard(ActionCard):
    def __init__(self):
        super().__init__()
        self.code = 'WS'
        self.is_gain4 = True

class FestivalCard(ActionCard):
    def __init__(self):
        super().__init__()
        self.code = 'Fv'
        self.add_actions = 2
        self.add_money = 2
        self.add_buys = 1

class VillageCard(ActionCard):
    def __init__(self):
        super().__init__()
        self.code = 'V'
        self.add_actions = 2
        self.add_cards = 1
