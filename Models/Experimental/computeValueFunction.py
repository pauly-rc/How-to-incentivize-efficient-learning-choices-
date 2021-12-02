from random import sample
from Environment import Environment 
from Agents import *
import numpy as np
import pickle


# first goal 
goal = np.array([1.,1.,1.,1.,1.,1.]) 



n_level_advances = 0 
advanced_at = []
games_per_day = []

# Initialise instance of the environment with the toy example values 
env = Environment(
                  skills_goal = goal,
                  final_goal= goal,
                  param_dict = None,

with open("state_space.p", "rb") as f:
    states = pickle.load(f)





learner = ValueIterAgent(env, states, var_delay = True)


print("Beginn Value Iteration")
v, e = learner.value_iteration()
with open("./value_function.p", "wb") as f:
    pickle.dump(v, f)

print("extract policy")
p = learner.extract_policy()
with open("./policy.p", "wb") as f:
    pickle.dump(p, f)



