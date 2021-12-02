import pickle
from Environment import Environment 
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
      
        # Adjust for the number of disctinct answer patterns resulting in the same number of correct and incorrect questions 
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

with open("./value_function.p", "rb") as f:
    value_function, e = pickle.load(f)

optimal_brain_points = {}


goal = np.array([1.,1.,1.])
f_goal = np.array([1.,1.,1.])

env = Environment(
                  skills_goal = goal,
                  final_goal= f_goal,
                  param_dict = None,
                  reduced = False)


for state in value_function:
    
    # Reset the Question Recycler
    env.question_recycler.set_state(state)

    # dict for storing brainpoints for each action 
    brain_points_state = {}

    # calculate the skill state form the current state 
    skill_state = tuple(env.question_recycler.calculate_current_skill_levels().values())

            # terminal state don't need a policy 
    if skill_state == tuple(env.question_recycler.max_level + 1 for x in range(env.n_skills)):
        continue
            
           
    next_goal = np.array([1.,1.,1.])
            
    # Iterate over all possible actions  
    for action in range(env.n_tasks):
                # reset the Question Recycler 
        env.question_recycler.set_state(state)
                # Get Questions for action 
        selected_questions = env.question_recycler.select_questions(env.task_names[action])
        prob_right = env.success_probabilities[env.task_names[action]]
                
                # get all possible outcomes 
        poss = {}
        q_counter = []
        for q in selected_questions["questions"]:
            poss[q] = list(get_tuples(2,selected_questions["questions"][q]))
            q_counter.append(q)
        lst = list(poss.values())
        if len(lst) > 1:
            answers = list(itertools.product(*lst))
        else:
            answers = [((x),) for x in lst[0]]

        # for storing probabilites of reaching a next state and corresponding rewards
        probs = []
        potentials = []
        rewards = []
        # Iterate over possible outcomes (= possible next states)
        for answer in answers:
                        
                   
            temp_selected_questions = copy.deepcopy(selected_questions)
                                            # get probabilty of answer pattern 
            prob_next_state = get_prob_next_state(answer, prob_right)      
            probs.append(prob_next_state)   
                    
            for a,q in zip(answer,q_counter):
                temp_selected_questions["results"][q]["correct"] = a[0]
                temp_selected_questions["results"][q]["incorrect"] =  a[1]

                        
                        
                        # Update Question Recycler
            env.question_recycler.update_qr_levels(temp_selected_questions)
            
                            # get the next state 
            next_state = env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
            assert next_state in value_function 

            potentials.append(value_function[next_state])

            env.question_recycler.set_state(next_state)
            next_skill_state = tuple(env.question_recycler.calculate_current_skill_levels().values())
            # check whether the current goal is reached and get the appropiate reward
            if (next_skill_state >= next_goal).all():
                reward = env.reward_goal  -1
            else: 
                reward =  -1 
                           
            rewards.append(reward)
                    
                             
            # Reset state for next iteration 
            env.question_recycler.set_state(state)

        expected_v_next = sum([p * r for p,r in zip(probs, potentials)])
        delta_v = expected_v_next - value_function[state]
        brain_points_state[env.task_names[action]] = delta_v + sum([p * r for p,r in zip(probs, rewards)]) 

    optimal_brain_points[str(state)] = brain_points_state   

                 
with open('optimal_brain_points.json', 'w') as fp:
    json.dump(optimal_brain_points , fp)