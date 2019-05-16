import random
import numpy as np

totalHands = 1326
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = ['c', 's', 'd', 'h']
totalRanks = len(ranks)
totalSuits = len(suits)
pfeqs = np.loadtxt("pf_eqs.dat")

def init_cardsMap():
    cardsMap = dict
    cardsMap = ToHandMap()
    return cardsMap

def dealCards():
    cardsMap = init_cardsMap()
    hand1 = cardsMap[random.randint(0, totalHands - 1)]
    hand2 = cardsMap[random.randint(0, totalHands - 1)]
    while hand1 == hand2:
        hand1 = cardsMap[random.randint(0, totalHands-1)]
        hand2 = cardsMap[random.randint(0, totalHands-1)]
    #print("hand1: "+ str(hand1) + "  .VS.  hands2: " + str(hand2))
    return hand1, hand2


def simulateHand(pot, SB_hand, SB_action, BB_hand, BB_action):
    cardsMap = init_cardsMap()
    for num, hand in cardsMap.items():
        if hand == SB_hand:
            state1 = num

    for num, hand in cardsMap.items():
        if hand == BB_hand:
            state2 = num

    if SB_action == "f":
        return (-0.5, 0.5)
    if  BB_action == "f":
        return (1, -1)


    # if (result == "sb"):
    #     return (pot, -pot)
    # if (result == "bb"):
    #     return (-pot, pot)
    # if (result == "draw"):
    #     return (0, 0)

    sbEquity = pfeqs[state1, state2]   #TODO: 5 cards, who win?
    #print("-D- SB is: " + str(SB_hand) + "BB is: " + str(BB_hand) + "resulting: " + str(sbEquity))


    if sbEquity is 0:
        return (0,0)
    elif np.random.normal(0.5,0.25) < sbEquity:
        return (pot, -pot)
    else:
        return (-pot, pot)


    # if sbEquity > 0.5:
    #     #print("SB WINS!!!!!!!!")
    #     return (pot, -pot)
    # if abs(sbEquity - 0.5) < 0.08 or sbEquity == 0:
    #     #print("FUCKING EVENNN!!!!!!!!")
    #     return (0,0)
    # #print("BB WINS!!!!!!!!")
    # return (-pot, pot)

def rank_hand(agent_hand, rand_hand):
    cardsMap = init_cardsMap()
    for num, hand in cardsMap.items():
        if hand == agent_hand:
            agent = num

    for num, hand in cardsMap.items():
        if hand == rand_hand:
            rand = num

    sbEquity = pfeqs[rand, agent]

    if np.random.normal(0.5,0.25) < sbEquity:
        return True
    else:
        return False

def ToHandMap():
    result = {}
    c = 0
    for r1 in range(2,totalRanks+2):
        for r2 in range(r1, totalRanks+2):
            for s1 in range(totalSuits):
                for s2 in range(totalSuits):
                    if r1 == r2 and s1 >= s2:
                        continue
                    # hand number c corresponds to holding
                    # ranks[r2], suits[s2], ranks[r1], suits[s1]
                    result[c] = [r2, r1, s1 == s2]
                    c += 1
    return result
