import random
import numpy as np
import pickle
import sys
import time
from tqdm import tqdm

from utils import dealCards as DealCards
from utils import init_cardsMap as init_CardsMap
from utils import simulateHand as SimulateHand
from utils import rank_hand as SimulateBluffTillEnd

CardsMap = init_CardsMap()
start_money = 10
money_agent = start_money
money_rand = start_money
actions = ["f","a"]
lie = 0
agent_actions = [0,0]
random_actions = [0,0]


def play(numberPlays,playing,file_out,stdout,mode):
        global money_agent
        global money_rand
        round = a_count = m_count = agent_round = total_round = 0
        if not playing:
            return

        if mode:
            sys.stdout = stdout

        with open('q_table.data', 'rb') as filehandle:
            q_table_from_train = pickle.load(filehandle)


        for game_number in tqdm(range(1, numberPlays)):
            money_agent = start_money
            money_rand = start_money
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GAME NUMBER " + str(game_number) + "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            while money_rand * money_agent != 0:
                if mode:
                    print("~~~~~~~~~~~~~~~ Starting round: " + str(round)+ "  ~~~~~~~~~~~~~~~")
                play_poker(round, game_number,q_table_from_train,mode)
                round += 1
            if (money_rand):
                if mode:
                    print("--------- U win ---------")
                m_count += 1
            else:
                if mode:
                    print("--------- AGENT win ---------")
                agent_round += round
                a_count += 1

            # for i in tqdm(range(int(100*(numberPlays-game_number)/numberPlays))):
            #     pass


            total_round += round
            round = 0
            #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  FINISH ROUND ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        if not mode:
            print("AGENT WINS: " + str(a_count) + " RANDOM WINS: " + str(m_count) + " %:" + str(a_count / (numberPlays-1)))
            print("Bluff %: " + str(lie/total_round))
            print("Average win rounds: " + str(agent_round/a_count))
            print("Random Actions: Fold: " + str(random_actions[0]) + " ALL-IN: " + str(random_actions[1]) + " Percentage Fold: " +  str(random_actions[0]/(random_actions[1]+random_actions[1])))
            print("Agent Actions: Fold: " + str(agent_actions[0]) + " ALL-IN: " + str(agent_actions[1])+ " Percentage Fold: " +  str(agent_actions[0]/(agent_actions[1]+ agent_actions[1])))

def play_poker(round, game_number,q_table_from_train,mode):
    global lie
    global money_agent
    global money_rand
    global agent_actions
    global random_actions

    hand_agent, hand_rand = DealCards()

    if mode:
        print("Your hand: " + str(hand_rand))

    for num, hand in CardsMap.items():
        if hand == hand_agent:
            state = num

    dist = abs(hand_agent[0] - hand_agent[1])
    is_bb = 0 if (round % 2 == 0) else 1
    money_value = MoneyLevel(money_agent)

    action_agent = actions[np.argmax(q_table_from_train[state][money_value][dist])]
    action_rand = random.choice(actions)
    if mode:
        if (round % 2 is 0):
            print("-G- U BB")
        else:
            print("-G- U SB")

    if mode:
        if not (action_agent is 0 and round % 2 is 1):
            action_rand = -1
            while action_rand not in['f','a']:
                print("-G- Choose Action: f for Fold || a for All-in? f|a")
                action_rand = input()
            # action_rand = from_action_to_num(action_rand)
        else:
            print("-I- Agent Folded!")

    agent_actions[from_action_to_num(action_agent)] += 1
    random_actions[from_action_to_num(action_rand)] += 1

    if mode:
        print("-I- Agent action is: " + action_agent)
        print("-I- Youre action is: " + action_rand)
        print("-I- Agent hand: " + str(hand_agent))

    # next_state, reward, done, info = env.step(action)   # env result on the action
    pot = min(money_agent, money_rand)
    if (round % 2 is 0):  # agent SB
        reward_agent, reward_rand = SimulateHand(pot, hand_agent, action_agent, hand_rand, action_rand)
    else:  # agent BB
        reward_rand, reward_agent = SimulateHand(pot, hand_rand, action_rand, hand_agent, action_agent)


    if (action_agent is "a" and is_bb == 0 and SimulateBluffTillEnd(hand_agent,hand_rand) and reward_agent > 0):   # bluff if agent: all-in & is_sb & rank less good & wins
        lie += 1

    money_agent += reward_agent
    money_rand += reward_rand
    if mode:
        print("-I- Agent now have: " + str(money_agent))
        print("-I- You now have: " + str(money_rand))



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