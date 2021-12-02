import pickle
from Environment import Environment 
from Agents import MyopicApproxAgent_Goal
import numpy as np 
import itertools
import copy
import json
import math 

def get_prob_next_state(answer, prob_right):
    """Returns the Probabilty of the answer given the probability of getting a question right"""
    # Each Question is consdiered an independent event, 
    prob_next_state = 1

    for a in answer:
        # therefore we multiply with prob_right for every correct Question in the Answer          
        for i in range(1, a[0]+1):
            prob_next_state =  prob_next_state * prob_right
       
        # And with (1 - prob_right) for every incorrect Question in the Answer
        for i in range(1, a[1]+1):
            prob_next_state =  prob_next_state * ( 1- prob_right)
      
        # Adjust for the number of disctinct answer patterns resulting in the same number of correct and incorrect questions (n! / (r!*(n-r)!))
        if a[0] != 0 and a[1] != 0:
            prob_next_state = prob_next_state *( math.factorial(a[0] + a[1]) / (math.factorial(a[0])*math.factorial(a[1])))
            
    return prob_next_state

def get_tuples(length, total):
    """Returns all tuples with n = length elements whose elements sum up to total"""
    if length == 1:
        yield (total,)
        return

    for i in range(total + 1):
        for t in get_tuples(length - 1, total - i):
            yield (i,) + t

with open("./optimal/value_function_wnP.p", "rb") as f:
    value_function, e = pickle.load(f)

approx_brain_points = {}


goal = np.array([1.,1.,1.])
f_goal = np.array([1.,1.,1.])

env = Environment(
                  skills_goal = goal,
                  final_goal= f_goal,
                  param_dict = None,
                  reduced = False)

approx_agent = MyopicApproxAgent_Goal(env = env, return_points=True)
choices = ["baseline", "medium similarity","similarity"]

for state in value_function:
    
    env.question_recycler.set_state(state)
    points = approx_agent.choose_action(state)
    approx_brain_points[str(state)] = {c:p for c,p in zip(choices, points)}

with open('approx_brain_points.json', 'w') as fp:
    json.dump(approx_brain_points , fp)