from Environment import Environment 
import pickle
import sys
import numpy as np
sys.setrecursionlimit(10000)

with open("./game_data_dists.p","rb") as f:
    param_dict = pickle.load(f)

env = Environment(
                  skills_goal = np.array([1.,1.,1.,1.,1.,1.]),  
                  param_dict = param_dict,
                  reduced = True)

# start the search 
env.find_next_states(env.initial_state, var_delay = False)

# save the states 
with open("./smallMDPStateSpace_3Modules_23Q_states0910.p","wb") as f:
    pickle.dump(env.states, f)

