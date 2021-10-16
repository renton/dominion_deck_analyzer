from itertools import combinations, permutations, combinations_with_replacement
import operator as op
from copy import deepcopy
from functools import reduce
from math import factorial

from cards import \
        EstateCard, \
        CopperCard, \
        SilverCard, \
        GoldCard, \
        MilitiaCard, \
        WorkshopCard, \
        FestivalCard

def npr(n, r):
    return int(factorial(n)/factorial(n-r))

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer // denom  # or / in Python 2

PROP_CODE_KEY = {
    'm' :   'money',
    'b' :   'buys',
    'a' :   'unused actions',
    'g4' :  'played an ACTION to gain a card of up to cost 4',


    '#_c':  'num cards in hand+play',
    '#_v':  'num VICTORY cards in hand+play',

    '#_t':  'num TREASURE cards in hand+play',
    'p_t':  'num TREASURE cards in play',

    '#_at': 'num TERMINAL ACTIONS in hand+play',           # num terminal actions in or added to hand
    'p_at': 'num TERMINAL ACTIONS in play',

    '#_ac': 'num CONT. ACTIONS in hand+play',
    'p_ac': 'num CONT. ACTIONS in play',

    '#_atk': 'num ATTACK ACTIONS cards in hand+play',
    'p_atk': 'num ATTACK ACTIONS cards in play',

    '#_w': 'num UNUSED ACTION cards',
}


deck = [
        MilitiaCard(),
        MilitiaCard(),
        FestivalCard(),
        FestivalCard(),
        FestivalCard(),
        WorkshopCard(),
        WorkshopCard(),
        EstateCard(),
        EstateCard(),
        CopperCard(),
        CopperCard(),
        CopperCard(),
        CopperCard(),
        SilverCard(),
        GoldCard(),
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
                'cnt':0,
                'base_cnt':0,
                '_':play['_'],
            }
        poss_data[play['poss_key']]['base_cnt'] += count
        poss_data[play['poss_key']]['cnt'] = poss_data[play['poss_key']]['base_cnt']


def simulate_hand(
        hand,
        deck,
        discard,
        poss_key,
        actions_left=1,
        buys_left=1,
        action_play=None,
        played_ids=None,
        data=None,

):
    if deck is None:
        deck = ()
    if discard is None:
        discard = ()

    results = []
    if played_ids is None:
        played_ids = set()

    if data is None:
        data = {
            'poss_key':poss_key,
            '_': {
                'm':0,              # money
                'b':0,              # buys left
                'a':0,              # actions left
                'g4':0,             # num gain card of up to cost 4

                '#_c':0,            # num total cards in or added to hand
                '#_v':0,            # num victory cards in or added to hand

                '#_t':0,            # num treasures in hand
                'p_t':0,            # num played treasures

                '#_at':0,           # num terminal actions in or added to hand
                'p_at':0,           # num terminal actions played

                '#_ac':0,           # num non-terminal actions in or added to hand
                'p_ac':0,           # num non-terminal actions played

                '#_atk':0,          # num attack actions in or added to hand
                'p_atk':0,          # num attack actions played

                '#_w':0,            # num wasted/unplayed actions cards in or added to hand
            },
        }
    else:
        data['poss_key'] = poss_key

    # play actions
    if action_play is not None:
        action_card_to_play = None
        for card in list(hand)+list(deck)+list(discard):
            if id(card) == action_play:
                action_card_to_play = card
                break
        if action_card_to_play is None:
            raise Exception("this should not happen A")

        if id(action_card_to_play) in played_ids:
            raise Exception("this should not happen B")

        # PLAY IT!
        actions_left -= 1
        actions_left += action_card_to_play.add_actions
        buys_left += action_card_to_play.add_buys
        data['_']['m'] += action_card_to_play.add_money

        if action_card_to_play.is_terminal:
            data['_']['p_at'] += 1
        else:
            data['_']['p_ac'] += 1

        if card.is_attack:
            data['_']['p_atk'] += 1

        if card.is_gain4:
            data['_']['g4'] += 1

        played_ids.add(id(action_card_to_play))


    # action branching recursive decisions
    for card in hand:
        if card.is_action:
            if id(card) not in played_ids:
                if actions_left > 0:
                    results += simulate_hand(
                        hand,
                        deck,
                        discard,
                        poss_key + ">" + card.code,
                        actions_left,
                        buys_left,
                        id(card),
                        deepcopy(played_ids),
                        deepcopy(data)
                    )
                else:
                    # TODO fix Wasted actions... not easy to tell what is in your hand at this point (wont work with draws)
                    # TODO fix for draws
                    data['_']['#_w'] += 1

    # TODO draws will need to deepcopy hand list without changing the poss_key

    # counts
    for card in hand:
        if card.is_treasure:
            data['_']['#_t'] += 1

        if card.is_victory:
            data['_']['#_v'] += 1

        if card.is_action:
            if card.is_terminal:
                data['_']['#_at'] += 1
            else:
                data['_']['#_ac'] += 1

            if card.is_attack:
                data['_']['#_atk'] += 1

        data['_']['#_c'] += 1

    # play treasures
    for card in hand:
        if card.is_treasure:
            data['_']['p_t'] += 1

        if isinstance(card.value, int):
            data['_']['m'] += card.value




    data['_']['b'] = buys_left
    data['_']['a'] = actions_left
    results += [data]
    return results

for hand in hand_combos:
    consider_deck = hand_is_deck_relevant(hand)
    consider_discard = hand_is_discard_relevant(hand)

    # Get remaining deck minus cards in hand
    remain = list(filter(lambda x: x not in hand, deck))

    # Check ignore deck+discard cache
    if not consider_deck and not consider_discard:
        poss_key = generate_poss_key(hand, None, None, True, True)

        if poss_key in poss_data:
            poss_data[poss_key]['cnt'] += poss_data[poss_key]['base_cnt']
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
    agg_results = {
            'num_poss': 0,
            'props' : {}
    }

    money_total = 0
    totals = {}

    for poss_key,poss_results in poss_data.items():
        agg_results['num_poss'] += poss_results['cnt']

        for prop_key,v in poss_results['_'].items():
            if prop_key not in agg_results['props']:
                agg_results['props'][prop_key] = {
                        'min' : 9999,
                        'max' : 0,
                        'avg' : 0,
                        'std' : 0,
                        'dist': {},
                }

            if prop_key not in totals:
                totals[prop_key] = 0
            totals[prop_key] += (v * poss_results['cnt'])

            if v > agg_results['props'][prop_key]['max']:
                agg_results['props'][prop_key]['max'] = v

            if v < agg_results['props'][prop_key]['min']:
                agg_results['props'][prop_key]['min'] = v

            #TODO std

            if v not in agg_results['props'][prop_key]['dist']:
                agg_results['props'][prop_key]['dist'][v] = 0
            agg_results['props'][prop_key]['dist'][v] += poss_results['cnt']


    for prop_key,total_v in totals.items():
        agg_results['props'][prop_key]['avg'] = total_v / agg_results['num_poss']


    return agg_results

def print_agg_result(agg_result):
    print("RESULTS:")
    print("==============================")
    print("num_poss: ", results['num_poss'])
    for k,v in results['props'].items():
        print('-------------------------------------------------')
        print(PROP_CODE_KEY[k], "\n")
        for k2,v2 in v.items():
            if k2 == 'dist':
                for k3,v3 in v2.items():
                    print("\t\t", k3, " : ", "(" + str(round((v3/results['num_poss']) * 100, 3)) + " %)", "\t", v3)
            else:
                print("\t", k2, " : ", v2)

#print(len(poss_data.keys()))

for k,v in poss_data.items():
    print('------')
    print(k)
    print(v)
#print(poss_data)
print(deck)
results = analyze_poss_data(poss_data)


print_agg_result(results)




















