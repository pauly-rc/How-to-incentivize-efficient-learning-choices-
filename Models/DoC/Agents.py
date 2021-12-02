from functools import partialmethod
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
                
                self.env.question_recycler.update_qr_levels_and_delays(temp_selected_questions)
                if self.env.reduced:
                    self.env.question_recycler.update_delays_for_new_session(1)
                next_state = self.env.question_recycler.get_state()
                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
       
                # check if treshold is passed by comparing all current skill levels with the goal skill levels 
                goal_reached = (next_skill_state >= self.env.skills_goal).all()
           
                # assign rewards 
                if goal_reached: 
                     # reaching the goal yields a positive reward, to which the negative reward of the action cost is added 
                    reward = self.env.reward_goal + self.env.task_cost_distributions[action].mean() /100 * -1
                    
                else: 
                    reward = self.env.task_cost_distributions[action].mean() /100 * -1 
            
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
                        print("Vn", n)
                        print("Vs", s)
                        print("BP", p)
                        print("r", reward)
                    
                    self.pseudos.append(p)
                    rewards.append(reward[0] + p)

                # for pseudo reward based on apprx Q(s,a), the pseudo reward is the same for all answer pattern for the same action 
                elif self.apply_approx_pseudo_rewards:
                        rewards.append(approx_q)
                        self.pseudos.append(approx_q)
                    
                else:
                    rewards.append(reward[0])

                self.env.question_recycler.set_state(state)
            print(rewards)
            print(probs)
            print(sum([r * p for r, p in zip(rewards, probs)]))
            print("P", sum(probs))         
           
            possible_rewards[action] = sum([r * p for r, p in zip(rewards, probs)])
        # choose action with highest expected reward 
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
    def __init__(self,env, return_points = False, scale_points = False):
        self.action_space = env.action_space
        self.env = env
        self.return_points = return_points
        self.scale_points = scale_points

        self.costs= {'fix the mix': -0.0865305999159651, 'speak racer': -0.04428165712199728, 'copy cat': -0.0937489324511539, 'copy parrot': -0.057754794997735455, 'typing time': -0.09352242768311225, 'brain battle': -0.09671575614760604, 'factory card': -0.09451654839343666, 'robot factory': -0.10978686324874502, 'word snap': -0.08698597156512367, 'hello cafe': -0.06531010959984816, 'flying robot': -0.05448183785330356, 'chat time': -0.10557980979658181, 'tick talk': -0.10115137717088073, 'eye spy': -0.05303190157055769, 'judge me': -0.04062066583200944, "talk n' go": -0.04487510619650611}

    def choose_action(self,observation):
        action = self.one_step_look_ahead(observation)

        return action

    def one_step_look_ahead(self,state):
        
        state = self.env.question_recycler.get_state()
        possible_rewards = np.zeros(self.action_space.n)
        current_progress = self.env.question_recycler.calculate_current_progress(self.env.skills_goal)
        #print(current_progress)
        for action in range(self.action_space.n):
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
                
                # get probabilty of answer pattern 
                prob_next_state = get_prob_next_state(answer, prob_right)         
                
                for a,q in zip(answer,q_counter):
                    temp_selected_questions["results"][q]["correct"] = a[0]
                    temp_selected_questions["results"][q]["incorrect"] =  a[1] 
                    
                probs.append(prob_next_state)
               
                self.env.question_recycler.update_qr_levels_and_delays(temp_selected_questions)
                 
              
            
                new_progress = self.env.question_recycler.calculate_current_progress(self.env.skills_goal)
                action_progress_potential.append(sum(new_progress.values()))
                if self.env.reduced:
                    self.env.question_recycler.update_delays_for_new_session(1)

                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                goal_reached = (next_skill_state >= self.env.skills_goal).all()
           
                mean_task_cost = self.costs[self.env.task_names[action]]#self.env.task_cost_distributions[action].mean()[0]/1000 * -1

                #mean_task_cost = mean_task_cost / sum(selected_questions["questions"].values())
                # assign rewards 
                if goal_reached: 
               
                    
                    rewards.append(25 +  mean_task_cost)#) + max(0,(sum(new_progress.values()) - sum(current_progress.values()))))
                    
                else:
                    rewards.append(mean_task_cost)# + max(0, (sum(new_progress.values()) - sum(current_progress.values()))))
                    

                self.env.question_recycler.set_state(state)
       
          
            possible_rewards[action] = sum([r * p for r, p in zip(rewards, probs)]) + (max(action_progress_potential) - sum(current_progress.values())) * 100
        if self.return_points: 
           
            points = {}
            if not self.scale_points:
                for i in range(len(possible_rewards)):
                    points[self.env.task_names[i]] = possible_rewards[i]
                return points
            else:
                for i in range(len(possible_rewards)):
                    points[self.env.task_names[i]] = self.scale(possible_rewards[i])
                return points

        if self.scale_points:
            # For testing rounded points
            print(possible_rewards)
            for i in range(len(possible_rewards)):
                possible_rewards[i] = self.scale(possible_rewards[i])
            print(possible_rewards)
            return int(np.argmax(possible_rewards))


        return int(np.argmax(possible_rewards))

    def scale(self, value):
        if value < 0:
            return 0 
        else:
            rounded_value = int(round(((value -  0.005619124822350843) / (61.85625851785114 -  0.005619124822350843))*4.98 + 0.51, 0))
            if rounded_value > 5:
                rounded_value = 5
        return rounded_value 



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
            print(e)
            e += 1
            
            # Iterate over all states 
            for state in self.values:
                
                # Set the Question Recycler to the State 
                self.env.question_recycler.set_state(state)
                                
                # Calculate the Skill levels from the state 
                skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
            
                
                # Any state that has already surpassed the highest goal values has a utility of 0 because no future rewards can be obtained 
                if skill_state == tuple(self.env.question_recycler.max_level + 1  for x in range(self.env.n_skills)):
            
                    self.values[state] = 0 
                    continue

                # adapt the next intermediate goal according to state 
                if (skill_state >= np.array([1.,1.,1.,1.,1.,1.])).all() :
                    
                    next_goal = np.array([2.,2.,2.,2.,2.,2.]) 
                else:
                    next_goal = np.array([1.,1.,1.,1.,1.,1.]) 

                    
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
                        
                        
                            
                            # Get a detached copy because selected_questions should not change for the following iterations
                        temp_selected_questions = copy.deepcopy(selected_questions)
                    
                            
                            # put in the answer 
                        for a,q in zip(answer,q_counter):
                            temp_selected_questions["results"][q]["correct"] = a[0]
                            temp_selected_questions["results"][q]["incorrect"] =  a[1] 
                    
                            
                            # Update Question Recycler based on anwser 
                        self.env.question_recycler.update_qr_levels_and_delays(temp_selected_questions)
                        if not self.var_delay:
                            self.env.question_recycler.update_delays_for_new_session(1)
                            
                            # get probabilty of the answer pattern by answer 
                            prob_next_state = get_prob_next_state(answer, prob_right)         
                            probs.append(prob_next_state)
                            # get the next state 
                            next_state = self.env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
                            if next_state in self.values:
                                self.env.question_recycler.set_state(next_state)
                                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                            # check whether the current goal is reached and get the appropiate reward
                                if (next_skill_state >= next_goal).all():
                                    reward = self.env.reward_goal + self.env.task_cost_distributions[action].mean() /100 * -1
                                else: 
                                    reward = self.env.task_cost_distributions[action].mean() /100 * -1 
                            
                                rewards.append(reward + self.gamma * self.values[next_state])
                            # Reset state for next iteration 
                            self.env.question_recycler.set_state(state)

                        else:
                            for delay in [0,1,2]:
                                self.env.question_recycler.update_delays_for_new_session(delay)
                                prob_next_state = get_prob_next_state(answer, prob_right)         
                                probs.append(prob_next_state / 3.)
                            # get the next state 
                                next_state = self.env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
                                if next_state in self.values:
                                    self.env.question_recycler.set_state(next_state)
                                    next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                            # check whether the current goal is reached and get the appropiate reward
                                    if (next_skill_state >= next_goal).all():
                                        reward = self.env.reward_goal + self.env.task_cost_distributions[action].mean() /100 * -1
                                    else: 
                                        reward = self.env.task_cost_distributions[action].mean() /100 * -1 
                            
                                    rewards.append(reward + self.gamma * self.values[next_state])
                            # Reset state for next iteration 
                                self.env.question_recycler.set_state(state)
                    
                    

                    # get the expected value for the next state 
                    nv = [p * r for p,r in zip(probs, rewards)]
                    # Collect values for determining the maximizimal future reward expectation 
                    next_states_rewards.append(sum(nv)) 
                    
                    
                # The maximal possible value reachable trough any action become the new state value 
                if len(next_states_rewards) < 1:
                    V_new[state] = 0
                else:
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
            if (skill_state >= np.array([1.,1.,1.,1.,1.,1.])).all() :
                    
                next_goal = np.array([2.,2.,2.,2.,2.,2.]) 
            else:
                next_goal = np.array([1.,1.,1.,1.,1.,1.])
            
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
                    
                    for a,q in zip(answer,q_counter):
                        temp_selected_questions["results"][q]["correct"] = a[0]
                        temp_selected_questions["results"][q]["incorrect"] =  a[1]

                        
                        
                        # Update Question Recycler
                    self.env.question_recycler.update_qr_levels_and_delays(temp_selected_questions)
                    if not self.var_delay:
                            self.env.question_recycler.update_delays_for_new_session(1)
                            
                            # get probabilty of the answer pattern by answer 
                            prob_next_state = get_prob_next_state(answer, prob_right)         
                            probs.append(prob_next_state)
                            # get the next state 
                            next_state = self.env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
                            if next_state in self.values:
                                self.env.question_recycler.set_state(next_state)
                                next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                            # check whether the current goal is reached and get the appropiate reward
                                if (next_skill_state >= next_goal).all():
                                    reward = self.env.reward_goal + self.env.task_cost_distributions[action].mean() /100 * -1
                                else: 
                                    reward = self.env.task_cost_distributions[action].mean() /100 * -1 
                            
                                rewards.append(reward + self.gamma * self.values[next_state])
                            # Reset state for next iteration 
                            self.env.question_recycler.set_state(state)

                    else:
                            for delay in [0,1,2]:
                                self.env.question_recycler.update_delays_for_new_session(delay)
                                prob_next_state = get_prob_next_state(answer, prob_right)         
                                probs.append(prob_next_state / 3.)
                            # get the next state 
                                next_state = self.env.question_recycler.get_state()
                            # check that the next state is permissable (= does not contain skills at levels higher than the maximal level) 
                                if next_state in self.values:
                                    self.env.question_recycler.set_state(next_state)
                                    next_skill_state = tuple(self.env.question_recycler.calculate_current_skill_levels().values())
                            # check whether the current goal is reached and get the appropiate reward
                                    if (next_skill_state >= next_goal).all():
                                        reward = self.env.reward_goal + self.env.task_cost_distributions[action].mean() /100 * -1
                                    else: 
                                        reward = self.env.task_cost_distributions[action].mean() /100 * -1 
                            
                                    rewards.append(reward + self.gamma * self.values[next_state])
                            # Reset state for next iteration 
                                self.env.question_recycler.set_state(state)
                  
                # calculate expected values
                nv = [p * r for p,r in zip(probs, rewards)]
                q_sa[action] = sum(nv)
            
            # Determine optimal action and add it to the policy   
            self.policy[state] = np.argmax(q_sa)   
            
        return self.policy

    def choose_action(self,observation):
        """Given a state, returns the action according to the agents' policy"""
        
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
                    
                    for prio in self.env.question_recycler.priorities[self.env.question_recycler.get_max_qr(selected_questions["skill_level"])]:
                        if prio in selected_questions["questions"] and  prio in self.env.question_recycler.priorities[self.env.question_recycler.get_max_qr(selected_questions["skill_level"])][:self.env.question_recycler.get_max_qr(selected_questions["skill_level"])] and selected_questions["skill_level"] == skills[skill]:
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
            #self.frequencies = {"brain battle"   : 0.15475812427225574,
            #"speak racer":  0.19667619350058219,
            #"hello cafe":  0.40774849158463006,
            #"copy cat" :  0.24081719064253201 }
            self.frequencies = {"speak racer": 0.232686286787727, "hello cafe": 0.48240450845335003, "copy cat": 0.284909204758923}

    def choose_action(self, observation):
        p = [s for s in self.frequencies.values()]
        #print(p)
        action = np.random.choice(a = [x for x in self.frequencies], p = p)
        return self.env.task_names.index(action)
        #

