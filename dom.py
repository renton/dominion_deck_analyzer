from itertools import combinations, permutations, combinations_with_replacement
import operator as op
from functools import reduce
from math import factorial

def npr(n, r):
    return int(factorial(n)/factorial(n-r))

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom  # or / in Python 2

class Card:
    def __init__(self, value=None):
        self.value = value
        self.code = str(value)

        self.consider_discard = False

        self.is_action = False
        self.is_treasure = False
        self.is_victory = False
        self.is_attack = False

    @property
    def consider_deck(self):
        return False

    def __repr__(self):
        return f"<{self.code}>"

class VictoryCard(Card):
    def __init__(self):
        super().__init__(None)
        self.is_victory = True

class TreasureCard(Card):
    def __init__(self, value):
        super().__init__(value)
        self.is_treasure = True

class ActionCard(Card):
    def __init__(self):
        super().__init__()
        self.is_action = True
        self.add_actions = 0
        self.add_cards = 0
        self.add_buys = 0
        self.add_money = 0
        self.is_attack = False

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
        self.code = 'M'

class VillageCard(ActionCard):
    def __init__(self):
        super().__init__()
        self.code = 'V'
        self.add_actions = 2
        self.add_cards = 1

class EstateCard(VictoryCard):
    def __init__(self):
        super().__init__()
        self.code = 'e'

class CopperCard(TreasureCard):
    def __init__(self):
        super().__init__(1)

class SilverCard(TreasureCard):
    def __init__(self):
        super().__init__(2)

class GoldCard(TreasureCard):
    def __init__(self):
        super().__init__(3)

class PlatinumCard(TreasureCard):
    def __init__(self):
        super().__init__(5)

deck = [
        EstateCard(),
        EstateCard(),
        EstateCard(),
        EstateCard(),
        EstateCard(),
        CopperCard(),
        SilverCard(),
        GoldCard(),
        GoldCard(),
        GoldCard(),
        MilitiaCard(),
        PlatinumCard(),
]

hand_combos = list(combinations(deck, 5))

# keys are hashes of possibilities
poss_data = {}

# if poss data hash exists, then just increment count

def hand_is_deck_relevant(hand):
    for card in hand:
        if card.consider_deck == True:
            return True
    return False

def hand_is_discard_relevant(hand):
    for card in hand:
        if card.consider_discard == True:
            return True
    return False

def generate_poss_key(hand, deck, discard, deck_irrelevant, discard_irrelevant):
    key = ""

    # deck
    if deck_irrelevant:
        key += "X"
    else:
        key += ".".join(list(map(lambda x: x.code, deck)))

    # hand
    hand_codes = list(map(lambda x: x.code, hand))
    hand_codes.sort()
    key += "|" + ".".join(hand_codes) + "|"

    # discard
    if discard_irrelevant:
        key += "X"
    else:
        discard_codes = list(map(lambda x: x.code, discard))
        discard_codes.sort()
        key += ".".join(discard_codes)
    return key
    

def update_poss_data(play_data, poss_data, count=1):
    for play in play_data:
        if play['poss_key'] not in poss_data:
            poss_data[play['poss_key']] = {
                'c':0,
                'base_c':0,
                'm':play['m'],
            }
        poss_data[play['poss_key']]['base_c'] += count
        poss_data[play['poss_key']]['c'] = poss_data[play['poss_key']]['base_c']


def simulate_hand(hand, deck, discard, poss_key):
    data = {
        'm':0,
        'total_c':0,
        'num_treasure':0,
        'num_victory':0,
        'num_a_ter':0,
        'num_a_cont':0,
        'play_treasure':0,
        'play_a_ter':0,
        'play_a_cont':0,
        'poss_key':poss_key,
        'attacks':0,
    }

    for card in hand:
        if card.is_treasure:
            data['num_treasure'] += 1
            data['play_treasure'] += 1

        if card.is_victory:
            data['num_victory'] += 1

        if isinstance(card.value, int):
            data['m'] += card.value

        data['total_c'] += 1

    # TODO recursively call simulate_hand for branches/choices

    return [data]

for hand in hand_combos:
    consider_deck = hand_is_deck_relevant(hand)
    consider_discard = hand_is_discard_relevant(hand)

    # Get remaining deck minus cards in hand
    remain = list(filter(lambda x: x not in hand, deck))

    # Check ignore deck+discard cache
    if not consider_deck and not consider_discard:
        poss_key = generate_poss_key(hand, None, None, True, True)

        if poss_key in poss_data:
            poss_data[poss_key]['c'] += poss_data[poss_key]['base_c']
            continue
        
        poss_key = generate_poss_key(hand, None, None, not consider_deck, not consider_discard)
        play_data = simulate_hand(hand, None, None, poss_key)

        poss_count = 0
        for i in range(len(remain) + 1):
            poss_count += ncr(len(remain), i) * npr(len(remain)-i, len(remain)-i)

        update_poss_data(play_data, poss_data, poss_count)
        continue


    # Check ignore discard cache
    if consider_deck and not consider_discard:
        continue

    # Use deck+discard
    for i in range(len(remain) + 1):
        # Different combinations of x cards in discard
        discard_combos = list(combinations(remain, i))

        for discard in discard_combos:
            draw_remain_permutations = list(permutations(list(filter(lambda x: x not in discard, remain))))

            for draw_remain in draw_remain_permutations:

                poss_key = generate_poss_key(hand, draw_remain, discard, not consider_deck, not consider_discard)
                play_data = simulate_hand(hand, draw_remain, discard, poss_key)
                
                update_poss_data(play_data, poss_data)


def analyze_poss_data(poss_data):
    results = {
            'num_poss': 0,
            'money_min': 999999,
            'money_max': 0,
            'money_avg': 0,
    }

    money_total = 0
    for k,v in poss_data.items():
        results['num_poss'] += v['c']

        money_total = money_total + (v['m'] * v['c'])

        if v['m'] > results['money_max']:
            results['money_max'] = v['m']

        if v['m'] < results['money_min']:
            results['money_min'] = v['m']

    results['money_avg'] = money_total / results['num_poss']
    return results

print("RESULTS:")
print("--------------------")
#print(len(poss_data.keys()))
print(poss_data.keys())
#print(poss_data)
print(deck)
print(analyze_poss_data(poss_data))

















