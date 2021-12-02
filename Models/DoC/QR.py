import numpy as np 
from QR_Parameters import *
from Agents import get_prob_next_state, get_tuples
import random 
import copy

class QR():
    """
    The QR system as described by Solve Education
    """
    def __init__(self, reduced = False ):
       
        # reduced governs whether the full or the small MDP is used 
        # get all the hard-coded parameters from QR_Parameters.py
        self.n_questions_per_skill_level = get_n_questions_per_skill_level(reduced)
        self.n_questions_all = sum(self.n_questions_per_skill_level.values())
        self.game_names = get_game_names(reduced)
        self.questions_per_module_per_skill_level = get_questions_per_module_per_skill_level(reduced)
        self.max_level = max([level for level in self.questions_per_module_per_skill_level])
        self.minigame_to_modules_mapping = get_minigame_to_modules_mapping()
        self.module_to_skill_mapping = get_module_to_skill_mapping()
        self.modules_to_minigames_mapping = get_modules_to_minigames_mapping()
        self.minigames_to_skill_mapping = get_minigame_to_skill_mapping(reduced)
        self.n_questions_per_minigame = get_number_of_questions_per_minigame(reduced)

        self.success_probs = None # gets overwritten by env 
        self.session_state = 0. #prob that next game is last of the day (needed for returning features)

        # dictionary that will store all the information regarding the quetions 
        self.questions =  {}
        
       
        # groups of questions are described by tuples (q,d), in which q describes the qr-level and d the remaining delay period in days
        if reduced:
            # in the small MDP, 3 is the maximal QR-level 
            self.priorities = {3:   [(0,0), # Questions that the learners has not seen before a priority 1
                                (1,0), (2,0), #   Uncompleted questions with no remaining delay are priority 2, ordered by QR level 
                                (1,1), (2,1), (2,2), # Uncompleted Questions within their delay period are Priority 3, ordered by QR level and remaining delay 
                                (3,0)], # Completed questions can be summarized in one group regardless of their delay (reduced size of state space)
                               }

            self.state_order = {3:   [(0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0)]}  

            self.max_delays = [0,1,2,0]
        else:
            # in the large MDP, both 5 and 3 can be the maximal QR-level depending on the level  
            self.priorities = {5: [ 
                                (0,0), # Questions that the learners has not seen before a priority 1
                                (1,0), (2,0), (3,0), (4,0),  #  Uncompleted questions with no remaining delay are priority 2, ordered by QR level 
                                (1,1), (2,1), (3,1), (4,1),  (2,2), (3,2), (4,2), (3,3), (4,3),  (3,4), (4,4), (4,5),  (4,6),  (4,7),  (4,8), # Uncompleted Questions within their delay period are Priority 3, ordered by QR level and remaining delay 
                                (5,0), (5,1), (5,2), (5,3), (5,4),(5,5),(5,6),  (5,7),(5,8), (5,9), (5,10), (5,11),(5,12),(5,13),(5,14),(5,15),(5,16)], # Completed Questions are priority 4, ordetred by closeness to the end of their delay period 

                                # Same priorities for a maximal QR level of 3 
                           3:   [(0,0), 
                                (1,0), (2,0),
                                (1,1), (2,1), (2,2),
                                (3,0), (3,1), (3,2), (3,3), (3,4)],
                        }

            # fixed order for getting sorted values from dictionaries for getting and setting state  
            self.state_order = {5: [ 
                                (0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), (3,1), (3,2), (3,3), (3,4), (4,0), (4,1),(4,2), (4,3), (4,4),  (4,5), (4,6),  (4,7),  (4,8), 
                                (5,0), (5,1), (5,2), (5,3), (5,4),(5,5),(5,6),  (5,7),(5,8), (5,9), (5,10), (5,11),(5,12),(5,13),(5,14),(5,15),(5,16)], 

                           3:   [(0,0), (1,0), (1,1), (2,0), (2,1), (2,2), (3,0), (3,1), (3,2), (3,3), (3,4)]}    
            self.max_delays = [0,1,2,4,8,16] 

        # iterate over skill levels 0 - 15 [Pre A.1 - C1.2]
        for level in range(len(self.questions_per_module_per_skill_level)):  
            self.questions[level] = {}

            # iterate over the 9 distinct modules 
            for module in self.minigame_to_modules_mapping:
                
                
                self.questions[level][module] = {}
                
                # Pre A.1 and Pre A.2 questions have a maximal QR level of 3, all others 5
                self.questions[level][module]["max_qr_level"] = self.get_max_qr(level)
                # Include the overall number of question the module offers at the level
                self.questions[level][module]["count_all"] = self.questions_per_module_per_skill_level[level][module]
                # Store the games in which those questions can be presented
                self.questions[level][module]["games"] = self.minigame_to_modules_mapping[module]

                # Store the skills trained by the module 
                self.questions[level][module]["associated_skills"] = []
                for skill in self.module_to_skill_mapping[module]:
                    if self.module_to_skill_mapping[module][skill]:
                        self.questions[level][module]["associated_skills"].append(skill)
                
                # for each qr-level, delay combination, store the number of question being in that state [at the start all are at (0,0)]
                question_states = []
                for qr in range(self.questions[level][module]["max_qr_level"] +1):
                    
                    for delay in range(self.max_delays[qr]+1):
                        
                        question_states.append((qr, delay))
                question_states_dict = {}
                for qs in question_states:
                    if qs == (0,0):
                        question_states_dict[qs] = self.questions[level][module]["count_all"]
                    else:
                        question_states_dict[qs] = 0

                self.questions[level][module]["current_state"] = question_states_dict

                 
        # Check that the supossed number of questions have been allocated in the modules 
        sum_q = 0
        sum_a = 0
        sum_c = 0
        for level in range(len(self.questions_per_module_per_skill_level)):  
            #print(sum(self.questions_per_module_per_skill_level[level].values()))
            for module in self.minigame_to_modules_mapping:
                sum_c += self.questions[level][module]["count_all"]
                sum_q += sum(self.questions[level][module]["current_state"].values())
                sum_a += self.questions_per_module_per_skill_level[level][module]
        
        assert sum_q == self.n_questions_all == sum_a == sum_c
           
       
    
    def select_questions(self, minigame):
        """ Selects questions to be presented by a minigame according to the Rules specified in https://docs.google.com/document/d/1-I8qUK0nRGH57wtrOrldmhP2RoDW5JFkHzu6woH9w1I/edit
            Parameter minigame (int) describes for which mini game to select questions
            Returns a dictionary with information on the selected questiins"""


        # get the module the game belongs to 
        module = self.modules_to_minigames_mapping[minigame]
        self.check()

        # sample the number of questions presented by the game form the corresponding distribution
        n_question_dist = self.n_questions_per_minigame[minigame]
        n_questions = np.random.choice(a = [x for x in range(1,len(n_question_dist)+1)], p = n_question_dist, replace = True)
        
        
        
        # get the applicable skill level by determining the lowest skill level of those skills trained by the module 
        skill_level = self.get_relevant_skill_level(module)   

        
        # we cannot select more questions than provided by the module
        if self.questions[skill_level][module]["count_all"] < n_questions:
            n_questions = self.questions[skill_level][module]["count_all"]

        assert n_questions != 0
        
        # get priorities according to the maximal QR level 
        priorities = self.priorities[self.get_max_qr(skill_level)]
        
        # question pool to be returned to the environment 
        question_pool = {"module" : module, "skill_level": skill_level, "questions": {}, "results" : {}}
        

        n_selected = 0
        
        # go from highest priority to lowest
        for prio in priorities: 
            
            # the process stops once enough questions have been found 
            if n_selected >= n_questions:
                break

            # get the number of questions belonging to the current priority group 
            n = self.questions[skill_level][module]["current_state"][prio] 
            
            # select as many as possible and needed 
            n_selected += n
            if n_selected > n_questions:
                n = n - (n_selected - n_questions)
            
            # add the questions to the question pool 
            if n > 0:   
                question_pool["questions"][prio] = n
        
        
        
        # check the number of questions selected 
        assert sum(question_pool["questions"].values()) == n_questions

        # prepare the storage of results
        for key in question_pool["questions"]:
            question_pool["results"][key] = {}

        return question_pool

    def get_relevant_skill_level(self, module, get_list = False):
        """For the given module, returns the relevant skill level by determining the lowest skill level of those skills trained by the module and 
           checking for which level the module has questions
           Parameter module (int): module for which the skill level has to be determined 
           Paramater get_list (boolean) governs whether additionally a list of relevant skills and a list of relevant levels should be returned (needed for feature representation)"""
        # get a list of all skills trained by the module 
        relevant_skills = []
        for skill in self.module_to_skill_mapping[module]:
            if self.module_to_skill_mapping[module][skill]:
                relevant_skills.append(skill)
        
        # get the current skill level for each skill
        current_skill_levels = self.calculate_current_skill_levels()
        
        # get the levels of the skills in 
        relevant_levels = []
        for skill in relevant_skills:
            relevant_levels.append(current_skill_levels[skill])
        
        skill_level = min(relevant_levels)
        
        # make sure maximal level is not exceeded 
        if skill_level > self.max_level:
            skill_level = self.max_level
        
        # shift level if no questions are available 
         
        if self.questions[skill_level][module]["count_all"] == 0:
            original_skill_level = skill_level
            found = False
            # first search for questions at a higher skill level 
            while  skill_level <= self.max_level and self.questions[skill_level][module]["count_all"] == 0 :
                skill_level += 1 
                if skill_level > self.max_level:
                    break
                elif self.questions[skill_level][module]["count_all"] != 0:
                    found = True 
                    break

            
        
            # if none are found, go down from the original skill level 
            if not found:
                skill_level = original_skill_level
                while skill_level > 0 and self.questions[skill_level][module]["count_all"] == 0:
                    skill_level -= 1 
            
        
        if get_list:
            return relevant_skills, relevant_levels, skill_level

        return skill_level
        
    def check(self):
        """Checks whether the number of questions for each module is valid"""
        for level in range(len(self.questions_per_module_per_skill_level)):  
            
            for module in self.minigame_to_modules_mapping:
                
                if self.questions[level][module]["count_all"] != sum(self.questions[level][module]["current_state"].values()):
                    print(level)
                    print(module)
                    print(self.questions[level][module]["count_all"])
                    print(sum(self.questions[level][module]["current_state"].values()))
                assert self.questions[level][module]["count_all"] == sum(self.questions[level][module]["current_state"].values())

    def update_qr_levels_and_delays(self, question_pool):
        """Updates QR-levels and delay periods after a minigame has been "played" according to the rules in https://docs.google.com/document/d/1-I8qUK0nRGH57wtrOrldmhP2RoDW5JFkHzu6woH9w1I/edit
            Paramter question_pool (dictionary): Pool of questions selected by self.select_questions(), with the answer added in by env.step()
            Returns nothing, but updates self.questions
            Only the questions contained in question_pool will be updated"""
        
         
        # Questions presented for the first time are a special case: They automatically advance to QR level 1 and can then further advance to two if answered correctly 
        if (0,0) in question_pool["results"]:
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][(0,0)] -= sum(question_pool["results"][(0,0)].values())
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][(1,0)] += sum(question_pool["results"][(0,0)].values())
                if not (1,0) in question_pool["results"]:
                    question_pool["results"][(1,0)] = question_pool["results"][(0,0)]
                else:
                    question_pool["results"][(1,0)]["correct"] = question_pool["results"][(1,0)]["correct"] + question_pool["results"][(0,0)]["correct"]
                    question_pool["results"][(1,0)]["incorrect"] = question_pool["results"][(1,0)]["incorrect"] + question_pool["results"][(0,0)]["incorrect"]
                
                del question_pool["results"][(0,0)]
        

        
        
        for result in question_pool["results"]:
            # completed questions do not change their QR value regardless of the answer 
            if result[0] == self.questions[question_pool["skill_level"]][question_pool["module"]]["max_qr_level"]:
                # If the delay period has expired, it is reset to the maximal delay 
                if result[1] == 0:
                    self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][result] -=  sum(question_pool["results"][result].values())
                    self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][(result[0], self.max_delays[result[0]])] +=  sum(question_pool["results"][result].values())
                continue 
            
            # Questions are only affected if their delay period has expired
            if result[1] == 0:

                # correctly answered questions rise (but not beyond the max qr level), delay is set according to new level
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][result] -= question_pool["results"][result]["correct"]
                new_qr = min(result[0] + 1, self.questions[question_pool["skill_level"]][question_pool["module"]]["max_qr_level"] )
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][(new_qr, self.max_delays[new_qr])] += question_pool["results"][result]["correct"]

                # incorrectly answered questions fall (but not below 1), , delay is set according to new level
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][result] -=  question_pool["results"][result]["incorrect"]
                new_qr = max(result[0] - 1, 1 )
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][(new_qr, self.max_delays[new_qr])] += question_pool["results"][result]["incorrect"]
        
        # check no questions have been lost or added 
        for level in range(len(self.questions_per_module_per_skill_level)):  
            
            for module in self.minigame_to_modules_mapping:
                
                assert self.questions[level][module]["count_all"] == sum(self.questions[level][module]["current_state"].values())
    
        
    def update_delays_for_new_session(self, session_delay):
        """Reduced the remaining delay period of all questions by session_delay
            Parameter session_delay (int): Time passed between sessions in days
            Returns nothing, but updates self.questions"""
       
        # iterate over all questions
        for level in range(len(self.questions_per_module_per_skill_level)):  
            
            for module in self.minigame_to_modules_mapping:
                # dictionary for storing the new states to not overwrite information still needed for subsequent steps 
                new_states = {} 
                # iterate over (q,d) groups in questions 
                for state in self.questions[level][module]["current_state"]:
                    # the delay period can not fall below 0 
                    new_delay = max(state[1] - session_delay, 0)
                    # Add together questions whose delay i newly 0 with those which are already at 0 
                    if new_delay == 0 and state[1] != 0:
                        if (state[0], new_delay) not in new_states:
                            new_states[(state[0], new_delay)] = self.questions[level][module]["current_state"][state[0], new_delay]

                        new_states[(state[0], new_delay)] += self.questions[level][module]["current_state"][state] 
                    # Move all other question simply according to their new delay period 
                    else:
                        new_states[(state[0], new_delay)] = self.questions[level][module]["current_state"][state]
                
                # make sure all keys are included 
                for state in self.questions[level][module]["current_state"]:
                    # groups not included in new_states do not contain questions 
                    if state not in new_states:
                        new_states[state] = 0
                # All necessary new information has been gathered, so now the old states can be overwritten 
                self.questions[level][module]["current_state"] = copy.deepcopy(new_states)

    
   
    
    
    def calculate_current_skill_levels(self):
        """Calculates and  the skill level for each skill, according to the rule that a skill level is considered completed if 80% of the associated questions have reached their highest QR-level
        Return as dictionary with skill names as keys and skill levels as values"""

        current_skill_levels = {"reading":0, "listening":0, "speaking":0, "writing":0, "grammar":0, "vocabulary":0}
        level_found = {"reading":False, "listening":False, "speaking":False, "writing":False, "grammar":False, "vocabulary":False}
        
        for level in  range(len(self.n_questions_per_skill_level)):
            
            # stop the process once all levels have been determined (meaning for each skill aan uncompleted level was already found )
            if all(level_found.values()):
                break

            # Otherwise, go over the different skills
            for skill in current_skill_levels:
                if level_found[skill]:
                    continue

                # Collect all questions associated with that skill and skill level
                n_relevant_questions = 0
                completed_questions = 0
                    
                for module in self.minigame_to_modules_mapping:

                    if skill in self.questions[level][module]["associated_skills"]:

                      

                        n_relevant_questions += self.questions[level][module]["count_all"]
                        
                        for s in self.questions[level][module]["current_state"]:
                            
                            if s[0] == self.questions[level][module]["max_qr_level"]:
                                
                                completed_questions += self.questions[level][module]["current_state"][s]
                                
                # If 80% of the relevant are completed, the skill level is considered to be completed as well
                if completed_questions >= n_relevant_questions * 0.8:
                    current_skill_levels[skill] = level + 1

                # Otherwise, the skill level is not completed and the last skill level is the one the learner is at at the moment 
                else:
                    level_found[skill] = True
        return current_skill_levels

    #def calculate_current_progress(self):
     #   """Calculates and Returns the progress (skill level + (sum of qr levels of relevant questions)/(sum of maximal qr level of relevant questions)) """
     #   current_progress = {"reading":0, "listening":0, "speaking":0, "writing":0, "grammar":0, "vocabulary":0}
     #   current_skill_levels = self.calculate_current_skill_levels()

     #   for skill in current_skill_levels:
    #        skill_level = current_skill_levels[skill]
    #        if skill_level > self.max_level:
    #            skill_level = self.max_level
    #        goal_sum = 0
    #        progress_sum = 0
    #        for module in self.minigame_to_modules_mapping:
    #            if skill in self.questions[skill_level][module]["associated_skills"]:
    #                goal_sum += self.get_max_qr(skill_level) * self.questions[skill_level][module]["count_all"]
    #                for state in self.questions[skill_level][module]["current_state"]:
    #                    progress_sum += state[0] * self.questions[skill_level][module]["current_state"][state]
                        
            
    #        current_progress[skill] = skill_level + progress_sum / goal_sum

    #    return current_progress
    

    def calculate_current_progress(self, current_goal):
        """Calculates and Returns the progress (skill level + (sum of qr levels of relevant questions)/(sum of maximal qr level of relevant questions)) """
        current_progress = {"reading":0, "listening":0, "speaking":0, "writing":0, "grammar":0, "vocabulary":0}
        #current_skill_levels = self.calculate_current_skill_levels()
        skill_level = int(current_goal[0] - 1)
        if skill_level > self.max_level:
            skill_level = self.max_level
        for skill in current_progress:
            #skill_level = current_skill_levels[skill]
            #if skill_level > self.max_level:
            #    skill_level = self.max_level
            goal_sum = 0
            progress_sum = 0
            for module in self.minigame_to_modules_mapping:
                if skill in self.questions[skill_level][module]["associated_skills"]:
                    goal_sum += self.get_max_qr(skill_level) * self.questions[skill_level][module]["count_all"]
                    for state in self.questions[skill_level][module]["current_state"]:
                        progress_sum += state[0] * self.questions[skill_level][module]["current_state"][state]
                        
            
            current_progress[skill] = skill_level + progress_sum / goal_sum

        return current_progress

    def get_max_qr(self, level):
        # Questions of level 0 and 1 have a maximal QR-Level of 3, all other Questions 5
        if level <= 1:
            return 3
        else:
            return 5


    def get_state(self):
        """Returns the state of the Question Recycler in the format needed for the MDP"""


        state = []
        for level in  range(len(self.n_questions_per_skill_level)):
            
            for module in self.minigame_to_modules_mapping:
                # the state order is used to guarantee consistency 
                for group in self.state_order[self.get_max_qr(level)]:
                    state.append(self.questions[level][module]["current_state"][group])
        
        return tuple(state)
 
    
    def set_state(self, state):
        """Set the State of the Question Recycler according to the input state given in MDP format"""
        self.check()
        i = 0
        for level in  range(len(self.n_questions_per_skill_level)):
            for module in self.minigame_to_modules_mapping:
                for group in self.state_order[self.get_max_qr(level)]:
                    
                    self.questions[level][module]["current_state"][group] = state[i]
                    
                    i = i+1
        self.check()

    def get_state_features(self, action, current_goal, include_session_state = False, collect = False):
        """Returns a tuple of F(s,a)
            Parameter action (str, int or float): the action for which to calculate F(s,a)
            Parameter current_goal (np.array): Next learning goal to be reached
            Parameter include_session_state (boolean): Indicates whether to include F8(s,a) P(next game is last game) """
        
        if type(action) == int or type(action) == float or type(action) == np.int64:
            action = self.game_names[action]
            
        module = self.modules_to_minigames_mapping[action]
        current_skill_levels = self.calculate_current_skill_levels()
        relevant_skills, relevant_levels, skill_level = self.get_relevant_skill_level(module, get_list= True)
        goal_order = ["reading", "listening", "speaking", "writing", "grammar", "vocabulary"]



        # F1: Number of questions with expired delay available for a
        f1 = 0
        for q in self.questions[skill_level][module]["current_state"]:
            if q[1] == 0 and q[0] != self.get_max_qr(skill_level):
                f1 += self.questions[skill_level][module]["current_state"][q]

        # F2: 1 if f1 >= median number of questions presented by a, 0 otherwise
        if f1 >= self.n_questions_per_minigame[action]:
            f2 = 1
        else:
            f2 = 0

        # F3: 1 if any skill trained by a has not reached current learning goal, 0 otherwise
        f3 = 0
        for skill, level in zip(relevant_skills, relevant_levels):
            if level < current_goal[goal_order.index(skill)]:
                f3 = 1

        # F4: 1 if any skill trained by a is (one of the) least developed skills, 0 else
        f4 = 0
        least_developed = min(current_skill_levels.values())
        for skill in relevant_skills:
            if current_skill_levels[skill] == least_developed:
                f4 = 1
        
        # F5: Number of questions necessary to complete for skills trained by a to reach next skill level
        # F6: Number of completed questions for current skill level for skills trained by a
        # F7: Mean QR-level of questions for current skill level for skills trained by a 
        f5 = 0
        f6 = 0
        f7 = 0 
        for skill, level in zip(relevant_skills, relevant_levels):
            if level > self.max_level:
                continue
            for mod in self.questions[level]:
                if skill in self.questions[level][mod]["associated_skills"]:
                    f5 += self.questions[level][mod]["count_all"]
                    t_f7 = 0 
                    for q in self.questions[level][mod]["current_state"]:
                        if q[0] == self.get_max_qr(level):
                            f6 += self.questions[level][mod]["current_state"][q]
                        t_f7 += q[0] * self.questions[level][mod]["current_state"][q]
                    if self.questions[level][mod]["count_all"] != 0:
                        f7 += t_f7 / self.questions[level][mod]["count_all"]
                    
        f5 = f5 / len(relevant_skills)
        f6 = f6 / len(relevant_skills)
        f7 = f7 / len(relevant_skills)

        
        f8 = max(current_skill_levels.values()) - (sum(relevant_levels) / len(relevant_levels))
        
            
        f9 = self.questions[int(np.mean(current_goal) -1)][module]["count_all"]   

        f10 = self.questions[skill_level][module]["current_state"][(0,0)]
        f11 = self.questions[skill_level][module]["current_state"][(1,0)]
        f12 = self.questions[skill_level][module]["current_state"][(2,0)]
        f13 = self.questions[skill_level][module]["current_state"][(3,0)]
        if self.get_max_qr(skill_level) == 5:
            f14 = self.questions[skill_level][module]["current_state"][(4,0)]
            f15 = self.questions[skill_level][module]["current_state"][(5,0)]
        else:
            f14 = -1
            f15 = -1

        if collect:
            return tuple([f1,f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15])

        return tuple([f1,f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15,
                        f1*f9,f2*f9, f3*f9, f4*f9, f5*f9, f6*f9, f7*f9, f8*f9, f9*f9, f10*f9, f11*f9, f12*f9, f13*f9, f14*f9, f15*f9,
                        f1*f3,f2*f3, f3*f3, f4*f3, f5*f3, f6*f3, f7*f3, f8*f3, f9*f3, f10*f3, f11*f3, f12*f3, f13*f3, f14*f3, f15*f3])
                         
        #return tuple([f1,f2,f3,f1*f9,f11*f9,f12*f9,f13*f9,f14*f9, f15*f9, f9*f3,f10*f3,f11*f3,f12*f3,f13*f3,f14*f3,f15*f3] )
        
        
        #if include_session_state:
        #    return tuple([f1, f2, f3, f4, f5, f6, f7, self.session_state])
        #else:
        #    return tuple([f1, f2, f3, f4, f5, f6, f7])
    def get_state_features_fs(self, state, current_goal):

        features = []
        
        # current skill levels
        #print(self.calculate_current_skill_levels().values())
        skill_levels = [v for v in self.calculate_current_skill_levels().values()]
        features.append(skill_levels[0]) # f1
        features.append(skill_levels[1]) # f2
        features.append(skill_levels[2]) # f3
        features.append(skill_levels[3]) # f4
        features.append(skill_levels[4]) # f5
        features.append(skill_levels[5]) # f6

        # current progress 
        current_progress = [p for p in self.calculate_current_progress().values()]
        features.append(current_progress[0]) # f7
        features.append(current_progress[1]) # f8
        features.append(current_progress[2]) # f9
        features.append(current_progress[3]) # f10
        features.append(current_progress[4]) # f11
        features.append(current_progress[5]) # f12

        # Question availability 
        for module in self.module_to_skill_mapping: #f13 - f67
            relevant_skills, relevant_levels, skill_level = self.get_relevant_skill_level(module, get_list= True)
            
            # General 
            fg = self.questions[int(np.mean(current_goal) -1)][module]["count_all"] 
            features.append(fg)
            
            # Ready for review 
            if fg != 0:
                
                fq0 = self.questions[skill_level][module]["current_state"][(0,0)]
                fq1 = self.questions[skill_level][module]["current_state"][(1,0)]
                fq2 = self.questions[skill_level][module]["current_state"][(2,0)]
                fq3 = self.questions[skill_level][module]["current_state"][(3,0)]
                if self.get_max_qr(skill_level) == 5:
                    fq4 = self.questions[skill_level][module]["current_state"][(4,0)]
                else:
                    fq4 = -1

                features.extend([fq0, fq1,fq2,fq3,fq4])
            else:
                features.extend([0,0,0,0,0])


        

        
        return tuple(features)
    


    def update_session_state(self, p):
        """Sets self.session_state to p"""
        self.session_state = p 


    
    def safe_state_in_SE_format(self, return_state = False):
        import json
        reverse_mapping = {0:"1", 1:"2", 2:"4", 3:"7", 4:"10", 5:"11", 6:"12", 7:"13", 8:"14" }
        state = []
        for level in  range(len(self.n_questions_per_skill_level)):
            #print(level)
            for module in self.module_to_skill_mapping:
                #print("Level: ", level, "Module", module)
                #print(self.questions[level][module])
                if self.questions[level][module]["current_state"][(0,0)] != self.questions[level][module]["count_all"]:
                    #print("passed if")
                    for qs in self.questions[level][module]["current_state"]:
                        #print(qs)
                        if qs != (0,0) and self.questions[level][module]["current_state"][qs] != 0:
                            #print("passed second if")
                            entry = {}
                            entry["Module_ID"] = reverse_mapping[module]
                            entry["Difficulty_Level"] = str(level)
                            entry["Word_Level"] = str(qs[0])
                            entry["Remaining_Delay"] = str(qs[1])
                            entry["Number_of_Questions"] = str(self.questions[level][module]["current_state"][qs])
                            #print(entry)
                            state.append(copy.deepcopy(entry))

        if return_state:
            return state 
        with open("mystate1703.json", "w") as f:
            json.dump(state, f)



        


        



            

