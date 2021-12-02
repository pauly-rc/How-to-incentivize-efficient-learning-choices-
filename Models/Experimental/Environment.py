import itertools
import numpy as np
import gym
from gym import spaces 
from QR import QR 
import random
from scipy.stats import  lognorm
import copy


class Environment(gym.Env): 
    """MDP representaion of Dawn of Civilisations"""
    def __init__(self,  skills_goal, param_dict, reduced = False, final_goal = np.array([16.,16.,16.,16.,16.,16.]) ):
        """Parameters:
           skill_goal (np.array): The learning goal (the first goal to yield reward)
           param_dict  (dictionary): Dictionary containing parameters for task cost distributions, P(Success), Delay distribution, and Games per Session distribution 
           reduced (boolean):  If true, small MDP is used
           final_goal (np.array): Maximal learning goal, default is C1.2 (the whole game has been played through), can be set to lower levels
          """
        self.initial_goal = skills_goal
        self.skills_goal     = skills_goal
        self.final_goal      = final_goal

        self.reward_goal      = 2000
        
        self.reduced = reduced
        
        # Adapt default value for small MDP 
        self.final_goal =  np.array([1.,1.,1.])#,1.,1.,1.])
        
    
        # Get an instance of the QR-System 
        self.question_recycler = QR(reduced = reduced)
        
        self.task_names = self.question_recycler.game_names
        self.n_tasks = len(self.task_names)
        #print(self.n_tasks)
        self.n_skills = len(self.question_recycler.calculate_current_skill_levels())

        # summarized representation (skill levels)
        self.skills_initial  = tuple(self.question_recycler.calculate_current_skill_levels().values())

        
        #low = np.zeros(state_shape) - 10000
        #high = np.zeros(state_shape) + 10000
        

        self.action_space = spaces.Discrete(self.n_tasks)
        #self.observation_space = spaces.Box(low, high, dtype = np.int64)
        #print(self.observation_space)
        
        # state: number of questions in each (qr-level,delay) group per module and level  
        self.initial_state = self.question_recycler.get_state()
        self.state = self.initial_state

        # Create task cost distribution to smaple rewards from 
        self.task_cost_distributions = []
        for name in self.task_names:
            self.task_cost_distributions.append(1)
    

        # discretized probability distributions for games per day and delay between days 
        #self.delay_between_game_days = param_dict["Delays between Game Days"]["dist"]
        #self.games_per_day = param_dict["Games per Day"]
        #self.n_games_current_day = 1

        # Success probabilities calculated from data 
        self.success_probabilities = {
                                        "baseline": 0.582,
                                        "medium similarity": 0.524,
                                        "similarity": 0.465
        }
            
        self.question_recycler.success_probs = self.success_probabilities

        # States, for defining the state space (only feasible for reduced MDP)
        self.states = {self.initial_state : 0}
        
        
        

    
    def step(self, action):
        """Perfom one step of the MDP given the chosen action
        Parameter action (int): action id of the chosen action"""
        
        info = {}
        # get the questions for the chosen game
        selected_questions = self.question_recycler.select_questions(self.task_names[action])
        
        
        # determine answers by accessing P(success|game) and assigning correct and incorrect by sampling from that probability 
        prob_right = self.success_probabilities[self.task_names[action]]
        for q in selected_questions["questions"]:
            answ = np.random.choice(a = [True, False], p = [prob_right, 1 - prob_right], replace = True, size=selected_questions["questions"][q])
            selected_questions["results"][q]["correct"] = np.count_nonzero(answ)
            selected_questions["results"][q]["incorrect"] =  selected_questions["questions"][q] - np.count_nonzero(answ)

        
        print(selected_questions)
        # update QR Levels and delays based on  answers 
        self.question_recycler.update_qr_levels(selected_questions)
        
        # for the small MDP, delay = 1 after every game
        

        # get the next state 
        next_state = self.question_recycler.get_state()

        # calcluate the updated skill levels  for the next state
        next_skill_state = tuple(self.question_recycler.calculate_current_skill_levels().values())
       
        # check if treshold is passed by comparing all current skill levels with the goal skill levels 
        goal_reached = (next_skill_state >= self.skills_goal).all()
           
        # assign rewards 
        if goal_reached: 
            # reaching the goal yields a positive reward, to which the negative reward of the action cost is added 
            reward = self.reward_goal + self.get_action_cost(action)
            # and the episode is considered finished 
            done = True        
            # reset the skill set, all skill progress beyond the goal is carried over to the next epsiode 
            
            self.state = next_state
            self.skills_goal = self.skills_goal + (1.,1.,1.)#,1.,1.,1.)
        else:
            # if the goal is not reached, only the action cost is returned 
            reward = self.get_action_cost(action)
            # and the episode continues 
            done = False 
            self.state = next_state   
        
        # if the skills goal exceed the possible levels, the whole game has been played trough 
        if (self.skills_goal > tuple(self.final_goal)).all():    
            
            info["terminated"] = True
        else:
            info["terminated"]= False
         
        return self.state, reward, done, info  
        #return np.array(self.question_recycler.get_state_features(action=action, current_goal= self.skills_goal)) , reward, done, info  

    def get_action_cost(self, action):
        """Draws and returns a sample from the Action Cost Distribution for the action"""
        return -1


    def reset(self):
        """Reset the environment by setting the state to its initial values and resetting the Question Recycler"""
        self.question_recycler.set_state(self.initial_state)
        self.state = self.initial_state
        self.skills_goal = self.initial_goal
        #self.n_games_current_day = 1
        return self.state 

    
   
    def find_next_states(self, initial_state, var_delay = False):
        """Recursivly finds all possible future states starting from initial state and adds them to self.states
        Parameter: initial_state (tuple): state from which to find all possible future states
                    var_delay (boolean): If true, possible delays are 0, 1 and 2, otherwise only 1"""
        
        for action in range(self.n_tasks):
            # Find all possible next states that action can lead to 
            next_states = self.find_next_states_a(initial_state, action, var_delay=var_delay)

            for ns in next_states:
                # For every state that has not already been covered, add it to the state space and continue searach from there 
                if ns not in self.states:
                    self.states[ns] = 0
                    self.find_next_states(ns, var_delay = var_delay)
            
               
    
    def find_next_states_a(self, initial_state, action, var_delay = False):
        """Returns all possible next states if action is taken in the initial state"""

        # set the question recycler to the initial state
        self.question_recycler.set_state(initial_state)
        next_states = []
        selected_questions = self.question_recycler.select_questions(self.task_names[action])
        
        # get all possible Correct / Incorrect combinations
        def get_tuples(length, total):
            if length == 1:
                yield (total,)
                return

            for i in range(total + 1):
                for t in get_tuples(length - 1, total - i):
                    yield (i,) + t
            
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
       
        
        # Go trough all possible Correct / Incorrect combinations and get the resulting next state to append to the list 
        for answer in answers:
            # amke a deepcopy to be able to reuse selected_questions in the next iteration 
            temp_selected_questions = copy.deepcopy(selected_questions)

            for a,q in zip(answer,q_counter):
                temp_selected_questions["results"][q]["correct"] = a[0]
                temp_selected_questions["results"][q]["incorrect"] =  a[1] 
                
            self.question_recycler.update_qr_levels(temp_selected_questions)
            
            next_states.append(self.question_recycler.get_state())
            
            # reset the question recycler for the next iteration 
            self.question_recycler.set_state(initial_state)
        
        return next_states