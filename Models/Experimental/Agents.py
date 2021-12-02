#from functools import partialmethod
import numpy as np
#import gym 
from collections import defaultdict
import itertools
import copy
import random 
import pickle
import random 
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

class RandomAgent():
    """agent for randomly selecting actions"""
    
    def __init__(self,env):
	    self.action_space = env.action_space
	
    def choose_action(self,observation):
        return self.action_space.sample()

class MyopicAgent():
    def __init__(self,env, apply_pseudo_rewards = False, value_function = None , mode = None, apply_approx_pseudo_rewards = False, w = None ):
        """Myopic Agent that performs a one step look ahead to greedely choose actions
            Parameters: apply_pseudo_rewards (boolean): Integrate pseudo reward sderived from a state-value function (pass value function if set to true)
                        value_function (dict): Dictionary with a value for each possible state (only available for small MDP)
                        mode (str): determines rounding / scaling mode for approximate pseudo rewards
                        apply_approx_pseudo_rewards (boolean): Whether to apply approximate Q(s,a) value sobtained from feature weights (pass w if set to true)
                        w (list): feature weights """

        self.action_space = env.action_space
        self.env = env
        self.apply_pseudo_rewards = apply_pseudo_rewards
        self.mode = mode
        if self.apply_pseudo_rewards:
            self.value_function = value_function
            if mode == "scaled":
                values = self.value_function.values()
                min_ = min(values)
                max_ = max(values)

                value_function = {key: ((v - min_ ) / (max_ - min_) )  for (key, v) in self.value_function.items() }
                self.value_function = value_function

        self.pseudos = []
        self.apply_approx_pseudo_rewards = apply_approx_pseudo_rewards
        self.weights = w

    def choose_action(self,observation):
        action = self.one_step_look_ahead(observation)

        return action

    def one_step_look_ahead(self,state):
        state = self.env.question_recycler.get_state()
        possible_rewards = np.zeros(self.action_space.n)
        for action in range(self.action_space.n):
            print("Action: ", action)
            # reset question recycler to the state we are looking ahead from 
            self.env.question_recycler.set_state(state)

            # select questions 
            selected_questions = self.env.question_recycler.select_questions(self.env.task_names[action])
            

            prob_right = self.env.success_probabilities[self.env.task_names[action]]
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
            
            probs = []
            rewards = []


            if self.apply_approx_pseudo_rewards:
                # get feature representaion of current state
                approx_q = np.array(self.env.question_recycler.get_state_features(action, self.env.skills_goal, include_session_state = False))
                # insert 1 for multiplication with intercept
                approx_q = np.insert(approx_q,0,1)
                # get dot product of feature vector and weight vector 
                approx_q = np.dot(approx_q, self.weights)
                
                self.pseudos.append((self.env.task_names[action]  , approx_q))
    
                

            for answer in answers:
                
                
                temp_selected_questions = copy.deepcopy(selected_questions)
                
                # get probabilty of answer pattern 
                prob_next_state = get_prob_next_state(answer, prob_right)
                
                for a,q in zip(answer,q_counter):
                    temp_selected_questions["results"][q]["correct"] = a[0]
                    temp_selected_questions["results"][q]["incorrect"] =  a[1] 
                    
                probs.append(prob_next_state)
                
                self.env.question_recycler.update_qr_levels(temp_selected_questions)
                
                next_state = self.env.question_recycler.get_state()
                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
       
                # check if treshold is passed by comparing all current skill levels with the goal skill levels 
                goal_reached = (next_skill_state >= self.env.skills_goal).all()
           
                # assign rewards 
                if goal_reached: 
                     # reaching the goal yields a positive reward, to which the negative reward of the action cost is added 
                    reward = self.env.reward_goal + self.env.get_action_cost(action)
                    
                else: 
                    reward = self.env.get_action_cost(action)
            
                if self.apply_pseudo_rewards:

                    n = self.value_function[next_state]
                    s = self.value_function[state]
                    

                    if self.mode == "round":
                        n = int(n)
                        s = int(s)
                        p = (n - s)
                    elif self.mode == "rounded_positive":
                        n = max(0, int(n))
                        s = max(0, int(s))
                        p = (n - s)
                    elif self.mode == "scaled":
                        n = n * 1000
                        s = s * 1000
                        p = int(max(0, (n-s)) / 40)
                    
                    
                    elif self.mode == "rounded_positive":
                        p = max(0, (n-s))
                        

                    else: 
                        p = (n - s)
                        #print("Vs")
                        #print("Vn", n)
                        #print("Vs", s)
                        #print("BP", p)
                        #print("r", reward)
                        #print(action, " ", p)
                    
                    self.pseudos.append(p)
                    rewards.append(reward + p)

                # for pseudo reward based on apprx Q(s,a), the pseudo reward is the same for all answer pattern for the same action 
                elif self.apply_approx_pseudo_rewards:
                        rewards.append(approx_q)
                        self.pseudos.append(approx_q)
                    
                else:
                    rewards.append(reward)

                self.env.question_recycler.set_state(state)
                     
            #print(rewards)
            #print(probs)
            #print(sum([r * p for r, p in zip(rewards, probs)]))
            #print("P", sum(probs))
            
            possible_rewards[action] = sum([r * p for r, p in zip(rewards, probs)])
        # choose action with highest expected reward 
        #print("B: ", possible_rewards[0],"MS: ",possible_rewards[1], "S: ", possible_rewards[2])
        return np.argmax(possible_rewards)


class ApproxQ_sa_Agent():
    """Myopic agent greedily choosing the action with the highest approximated Q(s,a) value"""
    def __init__(self,env, weights, use_intercept = False):
        self.env = env
        self.weights = weights
        self.pseudos = {game:[] for game in self.env.task_names}
        self.use_intercept = use_intercept

    def choose_action(self,observation):
        q = np.zeros(self.env.n_tasks)
        for action in range(self.env.n_tasks):
            # get feature representaion of current state
            approx_q = np.array(self.env.question_recycler.get_state_features(action, self.env.skills_goal, include_session_state = False))
            #print(self.env.task_names[action], ": " , approx_q)
            # insert 1 for multiplication with intercept
            if self.use_intercept:
                approx_q = np.insert(approx_q,0,1)
            # get dot product of feature vector and weight vector 
            approx_q = np.dot(approx_q, self.weights)
            #print(approx_q)
            q[action] = approx_q
            self.pseudos[self.env.task_names[action]].append(approx_q)
        
        return np.argmax(q)




class MyopicApproxAgent_Goal():
    """Agent that chooses action based on the potential for progress made in the next state"""
    def __init__(self,env, consider_reward = False, return_points = False):
        self.action_space = env.action_space
        self.env = env
        # whether to purely consider progress or also factor in action cost 
        self.consider_reward = consider_reward
        self.return_points = return_points
    def choose_action(self,observation):
        action = self.one_step_look_ahead(observation)

        return action

    def one_step_look_ahead(self,state):
        
        state = self.env.question_recycler.get_state()
        possible_rewards = np.zeros(self.action_space.n)
        current_progress = self.env.question_recycler.calculate_current_progress(self.env.skills_goal)
        #print("Old ",current_progress)
        #print(current_progress)
        
        for action in range(self.action_space.n):
            #print(action)
            # reset question recycler to the state we are looking ahead from 
            self.env.question_recycler.set_state(state)

            # select questions 

            selected_questions = self.env.question_recycler.select_questions(self.env.task_names[action])
            #print(selected_questions["questions"])

            prob_right = self.env.success_probabilities[self.env.task_names[action]]
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
            #print(answers)
            
            
            probs = []
            rewards = []
            action_progress_potential = []
            for answer in answers:
                
                
                temp_selected_questions = copy.deepcopy(selected_questions)
                #print("ans", answer)
                # get probabilty of answer pattern 
                prob_next_state = get_prob_next_state(answer, prob_right)         
                #print("p", prob_next_state)
                for a,q in zip(answer,q_counter):
                    temp_selected_questions["results"][q]["correct"] = a[0]
                    temp_selected_questions["results"][q]["incorrect"] =  a[1] 
                    
                probs.append(prob_next_state)
               
                self.env.question_recycler.update_qr_levels(temp_selected_questions)
                 
              
            
                new_progress = self.env.question_recycler.calculate_current_progress(self.env.skills_goal)
               # print(new_progress)
                action_progress_potential.append(sum(new_progress.values()))

                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                goal_reached = (next_skill_state >= self.env.skills_goal).all()
           
                #mean_task_cost = self.env.task_cost_distributions[action].mean()[0]/100000 * -1
                #mean_task_cost = mean_task_cost / sum(selected_questions["questions"].values())
                # assign rewards 
                if goal_reached: 
               
                    
                    rewards.append(self.env.reward_goal -1)# + max(0,(sum(new_progress.values()) - sum(current_progress.values()))))
                    
                else:
                    rewards.append(-1) #max(0,(sum(new_progress.values()) - sum(current_progress.values()))))
                    

                self.env.question_recycler.set_state(state)
                     
                
            #print("M", max(action_progress_potential))
            #print("D",(max(action_progress_potential) - sum(current_progress.values())))
            #print("R", rewards)
            #print("P", probs)
            #print("P", sum(probs))
            assert abs(sum(probs)-1) < 0.00001
            #print("R", sum([r * p for r, p in zip(rewards, probs)]))
            #print("Ds",((max(action_progress_potential)) - sum(current_progress.values()))*100 )

            possible_rewards[action] = sum([r * p for r, p in zip(rewards, probs)]) + ((max(action_progress_potential)) - sum(current_progress.values()))*100
            #print(possible_rewards)
        if self.return_points: 
            return possible_rewards

        return int(np.argmax(possible_rewards))


class ValueIterAgent():
    """Agent to perform Value Iteration on the reduced MDP"""

    def __init__(self,env, states, var_delay = False):
        # states are precomputed by StateSpaceDefiner 
        
        #Convergence Treshhold 
        self.delta = 0.0000001
        
        self.num_actions=env.action_space.n
        self.env = env
        self.num_states= len(states)

        # Dictionaries for storing the values and the policy 
        self.policy = {}
        for state in states:
            self.policy[state] = 0
        
        self.values = {}
        for state in states:
            self.values[state] = 0.0
        
        # Discount Factor
        self.gamma = 0.9
        self.var_delay = var_delay
    
    def value_iteration(self):
        """Changes self.values by performing value iteration until the update becomes smaller than self.delta"""
        # counter for numbers of iterations needed 
        e = 0
        
        
        # Initialize a dictionary to store the newly computed state values before transferring them to self.states, to compute the magnitude of the update   
        V_new = defaultdict(float)
        
        # initialize max_diff to a value greater than delta
        max_diff = self.delta + 0.00002

        # When the updates are smaller than the threshhold, the value iteration is considered to have converged  
        while max_diff > self.delta:

            # start fresh reference to compare updates against
            max_diff = 0

            # Print the current iteration 
            #print(e)
            e += 1
            #if e == 2:
            #    break
            
            # Iterate over all states 
            for state in self.values:
                #print("new state")
                # Set the Question Recycler to the State 
                self.env.question_recycler.set_state(state)
                                
                # Calculate the Skill levels from the state 
                skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
            
                
                # Any state that has already surpassed the highest goal values has a utility of 0 because no future rewards can be obtained 
                if skill_state == tuple(self.env.question_recycler.max_level + 1  for x in range(self.env.n_skills)):
            
                    self.values[state] = 0 
                    continue
                #else:
                    #print("hello")

                # adapt the next intermediate goal according to state 
                if (skill_state >= np.array([1.,1.,1.])).all() :
                    
                    next_goal = np.array([2.,2.,2.]) 
                else:
                    next_goal = np.array([1.,1.,1.]) 

                    
                # list for storing the rewards for all possible next states 
                next_states_rewards = []
                
                # Iterate over all possible actions
                for action in range(self.num_actions):
                    # reset question recycler 
                    self.env.question_recycler.set_state(state)
                    # get the questions for this action in this state 
                    selected_questions = self.env.question_recycler.select_questions(self.env.task_names[action])
                    # get the probability of getting a question right for the action 
                    prob_right = self.env.success_probabilities[self.env.task_names[action]]

                    # dictionary for storing all possible outcomes
                    poss = {}
                    # list for ordered access 
                    q_counter = []
                    for q in selected_questions["questions"]:
                        poss[q] = list(get_tuples(2,selected_questions["questions"][q]))
                        q_counter.append(q)
                    
                    # Get all combinations of outcomes 
                    lst = list(poss.values())
                    if len(lst) > 1:
                        answers = list(itertools.product(*lst))
                        
                    else:
                        answers = [((x),) for x in lst[0]]

                    
                    # list for storing the probabilities for reaching each possible next state and the reward obtained by reaching that next state 
                    probs = []
                    rewards = []
                    
                    # Iterate over all possible outcomes 
                    for answer in answers:
                        
                        #print("here")
                            
                            # Get a detached copy because selected_questions should not change for the following iterations
                        temp_selected_questions = copy.deepcopy(selected_questions)
                    
                            
                            # put in the answer 
                        for a,q in zip(answer,q_counter):
                            temp_selected_questions["results"][q]["correct"] = a[0]
                            temp_selected_questions["results"][q]["incorrect"] =  a[1] 
                    
                            
                            # Update Question Recycler based on anwser 
                        self.env.question_recycler.update_qr_levels(temp_selected_questions)
                        if not self.var_delay:
                            #self.env.question_recycler.update_delays_for_new_session(1)
                            #print("also here")
                            
                            # get probabilty of the answer pattern by answer 
                            prob_next_state = get_prob_next_state(answer, prob_right)  
                            #print("P", prob_next_state)       
                            probs.append(prob_next_state)
                            # get the next state 
                            next_state = self.env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
                            if next_state in self.values:
                                self.env.question_recycler.set_state(next_state)
                                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                            # check whether the current goal is reached and get the appropiate reward
                                if (next_skill_state >= next_goal).all():
                                    reward = self.env.reward_goal -1
                                else: 
                                    reward =  -1 

                                rewards.append(reward + self.gamma * self.values[next_state])

                            #print("R",reward)
                            if next_state not in self.values:
                                assert False
                            # Reset state for next iteration 
                            self.env.question_recycler.set_state(state)

                        
                    
                    
                    #print(probs)
                    #print(rewards)
                    # get the expected value for the next state 
                    nv = [p * r for p,r in zip(probs, rewards)]
                    #print(nv)
                    # Collect values for determining the maximizimal future reward expectation 
                    next_states_rewards.append(sum(nv)) 
                    #print(next_states_rewards)
                    
                # The maximal possible value reachable trough any action become the new state value 
                if len(next_states_rewards) < 1:

                    V_new[state] = 0
                else:
                    #print("hello2")
                    #print(max(next_states_rewards))
                    V_new[state] = max(next_states_rewards)


                # The magnitude of the update is calculated in order to estimate convergence
                # The comparison with max_diff ensures that the largest update in the iteration gets compared to delta              
                max_diff = max(max_diff, abs((self.values[state]- V_new[state])))
                
                # Update the value function 
                self.values[state] = V_new[state]

            
	            
        return self.values, e
  

    def extract_policy(self):
        """Based on the values stored in self.values, changes self.policy to reflect the optimal policy"""

        # Iterate over all states 
        for state in self.policy:
            # Reset the Question Recycler
            self.env.question_recycler.set_state(state)

            # Array for storing a value for each action 
            q_sa = np.zeros(self.num_actions)

            # calculate the skill state form the current state 
            skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())

            # terminal state don't need a policy 
            if skill_state == tuple(self.env.question_recycler.max_level + 1 for x in range(self.env.n_skills)):
            #if (skill_state >= np.array([1.,1.,1.,1.,1.,1.])).all():
                #self.policy[state] = 0 
                continue
            
            # Adapt goal 
            #if (skill_state >= np.array([1.,1.,1.])).all() :
                    
            #    next_goal = np.array([2.,2.,2.]) 
            #else:
            next_goal = np.array([1.,1.,1.])
            
            # Iterate over all possible actions  
            for action in range(self.num_actions):
                # reset the Question Recycler 
                self.env.question_recycler.set_state(state)
                # Get Questions for action 
                selected_questions = self.env.question_recycler.select_questions(self.env.task_names[action])
                prob_right = self.env.success_probabilities[self.env.task_names[action]]
                
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
                    self.env.question_recycler.update_qr_levels(temp_selected_questions)
                    
                            # get the next state 
                    next_state = self.env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
                    assert next_state in self.values

                    self.env.question_recycler.set_state(next_state)
                    next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                            # check whether the current goal is reached and get the appropiate reward
                    if (next_skill_state >= next_goal).all():
                        reward = self.env.reward_goal  -1
                    else: 
                        reward =  -1 
                           
                    rewards.append(reward + self.gamma * self.values[next_state])
                    
                             
                            # Reset state for next iteration 
                    self.env.question_recycler.set_state(state)

                    
                  
                # calculate expected values
                #print("ACTION: ", action)
                #print(rewards)
                #print(probs)
                
                nv = [p * r for p,r in zip(probs, rewards)]
         
                q_sa[action] = sum(nv)
                #print(q_sa)
            
            # Determine optimal action and add it to the policy   
            self.policy[state] = np.argmax(q_sa)   
            #print(self.policy[state])
            
        return self.policy

    def choose_action(self,observation):
        """Given a state, returns the action according to the agents' policy"""
        print(self.policy[observation])
        return self.policy[observation]

class HandCraftedAgent():
    """Agent choosing actions according to simple handcrafted policy"""
    def __init__(self,env):
        self.action_space = env.action_space
      
        self.env = env

    

    def choose_action(self,observation):
        if isinstance(observation, tuple):
            self.env.question_recycler.set_state(observation)

        # order skills by development
        skills = dict(sorted(self.env.question_recycler.calculate_current_skill_levels().items(), key=lambda item: item[1]))
        
        # Start with least developed skill 
        for skill in skills:
            # for each game..
            for game in self.env.question_recycler.minigames_to_skill_mapping:
               
                # ..check if it trains the skill currently considered 
                if self.env.question_recycler.minigames_to_skill_mapping[game][skill]:
                    
                    # check if it will present any question ready to increase their qr_level 
                    contains_first_prio_questions = False
                    selected_questions = self.env.question_recycler.select_questions(game)
                    
                    for prio in self.env.question_recycler.priorities:
                        if prio in selected_questions["questions"] and  prio in self.env.question_recycler.priorities[:self.env.question_recycler.get_max_qr(selected_questions["skill_level"])] and selected_questions["skill_level"] == skills[skill]:
                            contains_first_prio_questions = True
                    
                    # Choose the first game presentig questions which are ready to increase their qr-level 
                    if contains_first_prio_questions:
                        return self.env.task_names.index(game)

        # if this point is reached, no game can present questions ready to increase their qr-level 
        for skill in skills:

            for game in self.env.question_recycler.minigames_to_skill_mapping:

                if skill in self.env.question_recycler.minigames_to_skill_mapping[game]:
                    # Choose the first game that trains least developed skill 
                    return self.env.task_names.index(game)



class InGameRewardMaximizingAgent():
    def __init__(self, env):
        self.action_space = env.action_space
      
        self.env = env
        
    def choose_action(self, observation):

        return np.argmax(self.env.success_probabilities)

class DataFrequencyAgent():
    def __init__(self, env):
        self.action_space = env.action_space
      
        self.env = env
        if not env.reduced:
            self.frequencies = {"talk n' go":     0.023104,
                            "copy parrot" :      0.028399,
                            "factory card" :    0.029028,
                            "chat time" :       0.030621,
                            "eye spy"    :      0.031731,
                            "flying robot"   :  0.041691,
                            "judge me"       :  0.047949,
                            "brain battle"   : 0.054132,
                            "word snap"      :  0.059945,
                            "fix the mix"    : 0.066869,
                            "speak racer"    : 0.068794,
                            "tick talk"      :  0.076089,
                            "copy cat"       :  0.084234,
                            "robot factory"  :  0.088603,
                            "typing time"    :  0.126185,
                            "hello cafe"     :  0.142624}
        else:
        
            self.frequencies = {"speak racer": 0.232686286787727, "hello cafe": 0.48240450845335003, "copy cat": 0.284909204758923}

    def choose_action(self, observation):
        p = [s for s in self.frequencies.values()]

        action = np.random.choice(a = [x for x in self.frequencies], p = p)
        return self.env.task_names.index(action)
 

