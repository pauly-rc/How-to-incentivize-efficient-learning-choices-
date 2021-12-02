from random import sample
from Environment import Environment 
from Agents import *
import numpy as np
import pickle
import matplotlib.pyplot as plt
import sys
sys.setrecursionlimit(10000)

with open("./game_data_dists.p","rb") as f:
    param_dict = pickle.load(f)


learn_new = False

# first goal 
goal = np.array([1.,1.,1.,1.,1.,1.]) 
f_goal = np.array([4.,4.,4.,4.,4.,4.]) 


n_level_advances = 0 
advanced_at = []
games_per_day = []

# Initialise instance of the environment with the toy example values 
env = Environment(
                  skills_goal = goal,
                  final_goal= f_goal,
                  param_dict = param_dict,
                  reduced = False)
#print(env.initial_state)S
# Define Agent for learning 
#learner = MyopicApproxAgent(env)
#learner = HandCraftedAgent(env)
with open("state_space.p", "rb") as f:
    states = pickle.load(f)
print(len(states))
for state in states:
    print(state)
    break


#with open("weights_0729preA.p","rb") as f:
#    weights = pickle.load(f)


learner = ValueIterAgent(env, states, var_delay = False)
"""
if learn_new:

    print("Beginn Value Iteration")
    v, e = learner.value_iteration()
    with open("./value_function_2Modules_18Q.p", "wb") as f:
        pickle.dump(v, f)

    print("extract policy")
    p = learner.extract_policy()
    with open("./policy__2Modules_18Q.p", "wb") as f:
        pickle.dump(p, f)



else:
    

    learner.values = v 
 
    with open("./policy_3Modules_23Q_varNQ.p", "rb") as f:
        p = pickle.load(f)

    learner.policy = p 
"""
with open("./result_files/value_function.p", "rb") as f:
    v = pickle.load(f)
learner.values = v 
print("extract policy")
p = learner.extract_policy()
with open("./policy__2Modules_18Q.p", "wb") as f:
    pickle.dump(p, f)