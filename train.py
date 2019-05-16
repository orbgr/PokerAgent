import random
import numpy as np
import pickle
from tqdm import tqdm
import time

from utils import dealCards as DealCards
from utils import simulateHand as SimulateHand
from utils import init_cardsMap as init_CardsMap



totalHands = 1326
actions = ["f", "a"]
totalActions = len(actions)
money_value = [0,1,2,3]
totalMoneyValue = len(money_value)
cards_distance = [0,1,2,3,4,5,6,7,8,9,10,11,12]
totalCardsDist = len(cards_distance)

CardsMap = init_CardsMap()

Q_table = [[[[0 for k in range(totalActions)] for s in range(totalCardsDist)]for j in range(totalMoneyValue)] for i in range(totalHands)]
Q_table = np.float64(Q_table)

start_money = 10
money_agent = start_money
money_rand = start_money

penalty_sum = 0
agent_actions = [0,0]
random_actions = [0,0]

def train(numberTrain, learn, alpha=0.3, gamma=0.2):
    global money_agent
    global money_rand
    if not learn:
        return
    round = a_count =  m_count = 0
    for game_number in tqdm(range(1,numberTrain)):
        money_agent = start_money
        money_rand = start_money
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GAME NUMBER " + str(game_number) + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        while money_rand * money_agent != 0:
            # print("-I- Starting round: " + str(round))
            simulate_poker(round, game_number,numberTrain,alpha,gamma)
            round += 1
            # print("---- FINISH ---" )
        if (money_rand):
            # print("--------------SUMMARY: RANDOM PLAYER WINS WITH "+ str(money_rand) + " -------------------")
            m_count+=1
        else:
            # print("--------------SUMMARY: AGENT PLAYER WINS WITH " + str(money_agent) + " -------------------")
            a_count+=1

        # for i in tqdm(range(int(100 * (numberTrain - game_number) / numberTrain))):
        #     pass
        round = 0
   # print("AGENT WINS: " + str(a_count) + " RANDOM WINS: " + str(m_count) + " %:" + str(a_count/m_count))
    with open('q_table.data', 'wb') as filehandle:
         pickle.dump(Q_table, filehandle)
    print("----------------------------------------------Training finished.-----------------------------------------------------------------------------\n")
    print("Penalty Avg: " + str(penalty_sum/numberTrain))
    print("Random Actions: Fold: " + str(random_actions[0]) + " ALL-IN: " + str(random_actions[1])+ " Percentage Fold: " +  str(random_actions[0]/(random_actions[1]+random_actions[1])))
    print("Agent Actions: Fold: " + str(agent_actions[0]) + " ALL-IN: " + str(agent_actions[1])+ " Percentage Fold: " +  str(agent_actions[0]/(agent_actions[1]+agent_actions[1])))

def simulate_poker(round, game_number,numberTrain,alpha,gamma):
    global money_agent
    global money_rand
    global penalty_sum
    global agent_actions
    global random_actions
    penalty = 0

    hand_agent, hand_rand = DealCards()

    for num, Hand in CardsMap.items():
        if hand_agent == Hand:
            state = num
    dist = abs(hand_agent[0] - hand_agent[1])
    money_value = MoneyLevel(money_agent)
    is_bb = 1 if round % 2 else 0

    epsilon = game_number - numberTrain / numberTrain

    if random.uniform(0, 1) < epsilon:  # choose action
        action_agent = random.choice(actions)
    else:
        action_agent = chooseAction(money=money_agent,hand=hand_agent)

    action_rand = chooseAction(money=money_rand,hand=hand_rand)


    agent_actions[from_action_to_num(action_agent)] += 1
    random_actions[from_action_to_num(action_rand)] += 1

    # print("-I- Random Action: " + str(action_rand))
    pot = min(money_agent, money_rand)
    if is_bb:
        # print("-I- Agent is BB")
        round_money_rand, round_money_agent = SimulateHand(pot, hand_rand, action_rand, hand_agent, action_agent)
    else:
        # print("-I- Agent is SB")
        round_money_agent, round_money_rand = SimulateHand(pot, hand_agent, action_agent, hand_rand, action_rand)


    money_agent += round_money_agent
    money_rand += round_money_rand

    new_money_value = MoneyLevel(money_agent)

    # if money_value > new_money_value:
    #     penalty = int((money_value - new_money_value) / 2) * 5

    a = from_action_to_num(action_agent)

    # penalty_reward_agent = ExtraPenalties(reward_agent,action_agent,dist,is_bb,money_value,hand_agent[2])

    # penalty_sum += penalty_reward_agent
    # reward_agent += penalty

    if round_money_agent > 1:
        reward_agent = abs(new_money_value - money_value) * 5
    elif round_money_agent < -1:
        reward_agent = abs(new_money_value - money_value) * -5
    else:
        reward_agent = round_money_agent

    penalty_sum += reward_agent

    old_value = Q_table[state][money_value][dist][a]

    # next_max = np.argmax(Q_table[state][new_money_value][dist])
    next_max = NextState(state, action_agent, money_value, gamma, is_bb, dist, hand_agent, money_agent) + gamma * np.argmax(Q_table[state][new_money_value][dist])


    Q_table[state][money_value][dist][a] = (1 - alpha) * old_value + alpha * (reward_agent + gamma * next_max)



def chooseAction(money,hand):
    for num, Hand in CardsMap.items():
        if hand == Hand:
            state = num
    dist = abs(hand[0] - hand[1])
    money_value = MoneyLevel(money)

    return actions[np.argmax(Q_table[state][money_value][dist])]

def from_action_to_num(action):
    return 0 if action is "f" else 1

def MoneyLevel(agent_money):
    if agent_money <= (start_money * 2 / 4):
        money_value = 0
    elif agent_money <= (start_money * 4 / 4):
        money_value = 1
    elif agent_money <= (start_money * 6 / 4):
        money_value = 2
    else:
        money_value = 3
    return money_value

def NextState(state,action,money_value,gamma,is_bb,dist,hand_agent,money):
    if money <= 0 or money > 20:
        return 0

    round_money,action_rand = simulate(hand_agent,action,is_bb)

    new_money = money + round_money
    new_money_value = MoneyLevel(new_money)

    if round_money > 1:
        new_reward = abs(new_money_value - money_value) * 5
    elif round_money < -1:
        new_reward = abs(new_money_value - money_value) * -5
    else:
        new_reward = round_money

    next_max = np.argmax(Q_table[state][new_money_value][dist])

    return new_reward + gamma * next_max + NextState(state, action, new_money_value, gamma ** 2, not is_bb, dist, hand_agent, new_money)

def simulate(hand_agent,action_agent,is_bb):
    none, hand_rand = DealCards()
    action_rand = random.choice(actions)
    pot = min(money_agent, money_rand)
    if is_bb:
        # print("-I- Agent is SB")
        reward_rand, reward_agent = SimulateHand(pot, hand_rand, action_rand, hand_agent, action_agent)

    else:
        # print("-I- Agent is BB")
        reward_agent, reward_rand = SimulateHand(pot, hand_agent, action_agent, hand_rand, action_rand)
    return reward_agent,action_rand

# def ExtraPenalties(reward_agent,action,distance,is_bb,money_level,is_fit_cards):
#     # higher the rank, need to do all-in.
#
#     position_rank = is_a_not_rank(is_fit_cards) + moneyRank(money_level) + distanceRank(distance) + is_a_not_rank(is_bb)
#     if action == "f":
#         penalty = -position_rank
#     else:
#         penalty = position_rank
#
#     return reward_agent + penalty
#
#
#
# def distanceRank(distance):
#     if distance < 3:
#         distance_rank = abs((distance - 4) / 2)
#     if distance > 10:
#         distance_rank = (distance - 9) / 0.5
#     else:
#         distance_rank = -1.2
#     return distance_rank
#
# def moneyRank(money_level):
#     rank = [1.2,0.5,0,5,-1.2]
#     return rank[money_level]
#
# def is_a_not_rank(is_a):
#     return 1 if not is_a else -1
#

#
