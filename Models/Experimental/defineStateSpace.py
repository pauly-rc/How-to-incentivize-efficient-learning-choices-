from Environment import Environment 
import pickle
import sys
import numpy as np
sys.setrecursionlimit(50000)



env = Environment(
                  skills_goal = np.array([1.,1.,1.]),  
                  param_dict = None,
                  reduced = True)

# start the search 

env.find_next_states(env.initial_state, var_delay = False)

# save the states 
with open("./state_space.p","wb") as f:
    pickle.dump(env.states, f)


