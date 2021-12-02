from random import sample
from Environment import Environment 
from Agents import *
import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys
import json

# first goal 


goal = np.array([1.,1.,1.])
f_goal = np.array([1.,1.,1.])


n_level_advances = 0 
advanced_at = []
games_per_day = []

# Initialise instance of the environment with the toy example values 
env = Environment(
                  skills_goal = goal,
                  final_goal= f_goal,
                  param_dict = None,
                  reduced = False)
                  

with open("optimal_brain_points_v5.json", "r") as f:    
    optimal_brain_points = json.load(f)

h = -10000
l = 100000
for state in optimal_brain_points:
    for key in env.task_names:
        if optimal_brain_points[state][key] > h:
            h = optimal_brain_points[state][key]
        if optimal_brain_points[state][key] < l:
            l = optimal_brain_points[state][key] 


print("highest: ", h)
print("lowest: ", l)


def scale(value):
    
    return ((value - l) / (h - l))*(5.98) - 0.49



temp = []
print(scale(h))
print(scale(l))
for state in optimal_brain_points:
    for key in env.task_names:
       
        temp.append(int(round(scale(optimal_brain_points[state][key]))))
        optimal_brain_points[state][key] = int(round(scale(optimal_brain_points[state][key])))
        
print(min(temp))
print(max(temp))
print(set(temp))
with open('optimal_brain_points_scaled_5.json', 'w') as fp:
    json.dump(optimal_brain_points , fp)

sc = []
for state in optimal_brain_points:
    for key in env.task_names:
        sc.append(optimal_brain_points[state][key])

print(set(sc))















keymap = {'baseline':'a', 'medium similarity':'b', 'similarity':'c'}
reverse_keymap =  {'a':'baseline', 'b': 'medium similarity', 'c': 'similarity'}
keylist = [k for k in optimal_brain_points.keys()]
for state in keylist:  
    optimal_brain_points[state] = dict((keymap[key], value) for (key, value) in optimal_brain_points[state].items())
    compressed_state = state.replace(",", "")
    compressed_state = compressed_state.replace(" ", "")
    compressed_state= compressed_state.replace("(", "")
    compressed_state = compressed_state.replace(")", "")
    #print(compressed_state)
    #print(state)
    optimal_brain_points[compressed_state] = optimal_brain_points.pop(state)

def compress_state(state):
    compressed_state = state.replace(",", "")
    compressed_state = compressed_state.replace(" ", "")
    compressed_state= compressed_state.replace("(", "")
    compressed_state = compressed_state.replace(")", "")
    return compressed_state

with open("./optimal/value_function.p", "rb") as f:
        v,e = pickle.load(f)
learner = MyopicAgent(env, apply_pseudo_rewards = True, value_function = v)
#learner = HandCraftedAgent(env)
#learner = MyopicApproxAgent_Goal(env)
actions = []
print("Begin Learning")
observation = env.reset()
r = 0

# Observe the choices by the agent for a certain number of time steps 
for t in range(1, 150):
    print("######################### ACTION  " , t)
    #for action in env.task_names:
    #    print(action, ": ", env.question_recycler.get_state_features(action, env.skills_goal))
    # let agent chose action according to its policy
    action = learner.choose_action(observation)
    #action = learner.choose_action(observation)
    bp = optimal_brain_points[compress_state( str(observation))]
    print(bp)
    #for key, value in bp.items():
    #    bp[key]= round(value/15)
    #print(bp)
    #print("Brain Points", bp)
    ps = []
    for key in bp:
        if bp[key] == max(bp.values()):
            ps.append(key)
    #b_action = max(bp, key=bp.get)
    b_action = random.choice(ps)
    b_action = reverse_keymap[b_action]
    print("chosen action 1: ", action)
    print("chosen action 2: ", b_action)
    #print("chosen action: ", env.task_names[action])
    #print(b_action == env.task_names[action])
    actions.append(b_action)
    # and observe the results 
    #observation, reward, done, info = env.step(action)  
    observation, reward, done, info = env.step(env.task_names.index(b_action)) 
    #print(len(observation))
    #print(observation)
    #assert False
    
    r = r + reward
    print(reward)
    print(env.question_recycler.calculate_current_skill_levels() )
    print(f"Action: {b_action} \nReward: {reward} \nDone: {done}")
    
    if done:
        # document level advances 
        n_level_advances += 1
        advanced_at.append(t)
        
    if info["terminated"]:
        break

    if "games in day" in info:
        games_per_day.append(info["games in day"])
        
# print a summary 
print(f"Number of Level-ups: {n_level_advances}")
print(f"Level-ups took place in episodes: {advanced_at}")
for action in env.task_names:
    print(action, " : ", actions.count(action))