from random import sample
from Environment import Environment 
from Agents import *
import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys
import json
sys.setrecursionlimit(10000)

with open("value_function_wnPg1.p" ,"rb") as f:
    value_function , e = pickle.load(f)



#with open("./game_data_dists.p","rb") as f:
#    param_dict = pickle.load(f)
with open("optimal_brain_points_nVg1wfR.json", "r") as f:    
    optimal_brain_points = json.load(f)

scaled_points = {}
#print(min(d.values()  for d in optimal_brain_points.values())


print(len(optimal_brain_points))
b = 0
ms = 0
s = 0
o = 0
for key in optimal_brain_points:
    value = optimal_brain_points[key]
    if max(value, key=value.get) == "baseline":
        b += 1
    elif max(value, key=value.get) == "medium similarity":
        ms += 1
    elif max(value, key=value.get) == "similarity":
        s += 1
    else:
        o += 1 

print (b, ms, s, o)



learn_new = False

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




h = -10000
l = 100000
for state in optimal_brain_points:
    for key in env.task_names:
        if optimal_brain_points[state][key] > h:
            h = optimal_brain_points[state][key]
            h_state = state
        if optimal_brain_points[state][key] < l:
            l = optimal_brain_points[state][key] 
            l_state = state 

    #h.append( max(d[key]for d in optimal_brain_points.values()))
    #l.append( min(d[key]for d in optimal_brain_points.values()))
#h = max(h)
#l = min(l)
print(h_state)
print(h)
print(l_state)
print(l)
def scale(value):
    
    return ((value - l) / (h - l))*(5.98) -0.49
temp = []
print(scale(h))
print(scale(l))
for state in optimal_brain_points:
    scaled_points[state] = {}
    for key in env.task_names:
       
        temp.append(int(scale(optimal_brain_points[state][key])))
        scaled_points[state][key] = int(scale(optimal_brain_points[state][key]))
        
print(min(temp))
print(max(temp))
print(set(temp))

def compress_state(state):
    compressed_state = state.replace(",", "")
    compressed_state = compressed_state.replace(" ", "")
    compressed_state= compressed_state.replace("(", "")
    compressed_state = compressed_state.replace(")", "")
    return compressed_state




keymap = {'baseline':'a', 'medium similarity':'b', 'similarity':'c'}
reverse_keymap =  {'a':'baseline', 'b': 'medium similarity', 'c': 'similarity'}
keylist = [k for k in scaled_points.keys()]
for state in keylist:  
    scaled_points[state] = dict((keymap[key], value) for (key, value) in scaled_points[state].items())
    compressed_state = state.replace(",", "")
    compressed_state = compressed_state.replace(" ", "")
    compressed_state= compressed_state.replace("(", "")
    compressed_state = compressed_state.replace(")", "")
    #print(compressed_state)
    #print(state)
    scaled_points[compressed_state] = scaled_points.pop(state)

with open('optimal_brain_points_scaled_1101.json', 'w') as fp:
    json.dump(scaled_points , fp)

def compress_state(state):
    compressed_state = state.replace(",", "")
    compressed_state = compressed_state.replace(" ", "")
    compressed_state= compressed_state.replace("(", "")
    compressed_state = compressed_state.replace(")", "")
    return compressed_state


        
#learner = MyopicAgent(env, apply_pseudo_rewards = True, value_function = value_function)
#learner = HandCraftedAgent(env)
#learner = MyopicApproxAgent_Goal(env)
with open("statespace_20.p", "rb") as f:
    statespace = pickle.load(f)
with open ("policy_wnPg1_V2.p", "rb") as f:
    policy = pickle.load(f)
learner = ValueIterAgent(env, statespace)
learner.values = value_function
learner.policy = policy
#p = learner.extract_policy()

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
    #print(value_function[observation])
    action = learner.choose_action(observation)
    bp = scaled_points[compress_state( str(observation))]
    print(bp)
    op = optimal_brain_points[str(observation)]
    print(op)

    
    #print("Brain Points", bp)
    #ps = []
    #for key in bp:
    #    if bp[key] == max(bp.values()):
    #        ps.append(key)
    #b_action = max(bp, key=bp.get)
    #b_action = random.choice(ps)
    #b_action = reverse_keymap[b_action]
    print("chosen action 1: ", action)
    #print("chosen action 2: ", b_action)
    #print("chosen action: ", env.task_names[action])
    #print(b_action == env.task_names[action])
    #actions.append(b_action)
    # and observe the results 
    #observation, reward, done, info = env.step(action)  
    print("V", value_function[observation])
    observation, reward, done, info = env.step(action) 
    print("V", value_function[observation])
    #print(len(observation))
    #print(observation)
    #assert False
    
    r = r + reward
    print(reward)
    print(env.question_recycler.calculate_current_skill_levels() )
    print(f"Action: {action} \nReward: {reward} \nDone: {done}")
    
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
#bins = [x for x in range(-1, max(games_per_day)+1,1)]
#plt.hist(games_per_day, bins, density = True)
#print(env.question_recycler.questions)
#plt.show()
#print(set(learner.pseudos))
#print(reward/34)
#print(env.question_recycler.questions)
#x = [x for x in range(1000)]
#for y in x:
#    print(env.question_recycler.questions[y])
"""
fc_approx_brain_points = {}
for state in optimal_brain_points:
    fc_dict = {}
    points = list(optimal_brain_points[state].values())
    actions = list(optimal_brain_points[state].keys())

    fc = actions[points.index(max(points))]
    for action in optimal_brain_points[state]:
        if action == fc:
            fc_dict[action] = 1
        else:
            fc_dict[action] = 0
    cfc_dict = dict((keymap[key], value) for (key, value) in fc_dict.items())
    assert sum(list(cfc_dict.values())) == 1
    fc_approx_brain_points[compress_state(state)] = cfc_dict




    
with open('fc_approx_points_1101.json', 'w') as fp:
    json.dump(fc_approx_brain_points, fp)

"""
"""
fc_optimal_brain_points = {}
for state in policy:
    fc_dict = {}
    

    fc = env.task_names[ policy[state] ]
    #print(fc)
    for action in optimal_brain_points[str(state)]:
        if action == fc:
            fc_dict[action] = 1
        else:
            fc_dict[action] = 0
    #print(fc_dict)
    cfc_dict = dict((keymap[key], value) for (key, value) in fc_dict.items())
    #print(cfc_dict)
    assert sum(list(cfc_dict.values())) == 1
    fc_optimal_brain_points[compress_state(str(state))] = cfc_dict




    
with open('fc_optimal_points_1101.json', 'w') as fp:
    json.dump(fc_optimal_brain_points, fp)
    """