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
        self.n_questions_per_skill_level = get_n_questions_per_skill_level()
        self.n_questions_all = sum(self.n_questions_per_skill_level.values())
        self.game_names = get_game_names()
        self.questions_per_module_per_skill_level = get_questions_per_module_per_skill_level()
        self.max_level = max([level for level in self.questions_per_module_per_skill_level])
        self.minigame_to_modules_mapping = get_minigame_to_modules_mapping()
        self.module_to_skill_mapping = get_module_to_skill_mapping()
        self.modules_to_minigames_mapping = get_modules_to_minigames_mapping()
        self.minigames_to_skill_mapping = get_minigame_to_skill_mapping()
        self.n_questions_per_minigame = get_number_of_questions_per_minigame()

        self.success_probs = None # gets overwritten by env 
        self.session_state = 0. #prob that next game is last of the day (needed for returning features)

        # dictionary that will store all the information regarding the quetions 
        self.questions =  {}
        
       
        # groups of questions are described by tuples (q,d), in which q describes the qr-level and d the remaining delay period in days
       
            # in the small MDP, 3 is the maximal QR-level 
        self.priorities = [0, 1, 2, 3, 4] 

        self.state_order = self.priorities

            
         
           

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
                    
                    question_states.append(qr)
                question_states_dict = {}
                for qs in question_states:
                    if qs == 0:
                        question_states_dict[qs] = self.questions[level][module]["count_all"]
                    else:
                        question_states_dict[qs] = 0

                self.questions[level][module]["current_state"] = question_states_dict

       # print(self.questions)
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
        priorities = self.priorities
        
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

    def update_qr_levels(self, question_pool):
        """Updates QR-levels and delay periods after a minigame has been "played" according to the rules in https://docs.google.com/document/d/1-I8qUK0nRGH57wtrOrldmhP2RoDW5JFkHzu6woH9w1I/edit
            Paramter question_pool (dictionary): Pool of questions selected by self.select_questions(), with the answer added in by env.step()
            Returns nothing, but updates self.questions
            Only the questions contained in question_pool will be updated"""
        
         
        # Questions presented for the first time are a special case: They automatically advance to QR level 1 and can then further advance to two if answered correctly 
        if 0 in question_pool["results"]:
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][0] -= sum(question_pool["results"][0].values())
                self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][1] += sum(question_pool["results"][0].values())
                
                del question_pool["results"][0]
        

        
        
        for result in question_pool["results"]:
            # completed questions do not change their QR value regardless of the answer 
            if result == self.questions[question_pool["skill_level"]][question_pool["module"]]["max_qr_level"]:
                # If the delay period has expired, it is reset to the maximal delay 
                continue 
            
           

                # correctly answered questions rise (but not beyond the max qr level), delay is set according to new level
            self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][result] -= question_pool["results"][result]["correct"]
            new_qr = min(result + 1, self.questions[question_pool["skill_level"]][question_pool["module"]]["max_qr_level"] )
            self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][new_qr] += question_pool["results"][result]["correct"]

                # incorrectly answered questions fall (but not below 1), , delay is set according to new level
            self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][result] -=  question_pool["results"][result]["incorrect"]
            new_qr = max(result - 1, 1 )
            self.questions[question_pool["skill_level"]][question_pool["module"]]["current_state"][new_qr] += question_pool["results"][result]["incorrect"]
        
        # check no questions have been lost or added 
        for level in range(len(self.questions_per_module_per_skill_level)):  
            
            for module in self.minigame_to_modules_mapping:
                
                assert self.questions[level][module]["count_all"] == sum(self.questions[level][module]["current_state"].values())
    
        

   
    
    
    def calculate_current_skill_levels(self):
        """Calculates and  the skill level for each skill, according to the rule that a skill level is considered completed if 80% of the associated questions have reached their highest QR-level
        Return as dictionary with skill names as keys and skill levels as values"""

        current_skill_levels ={"baseline": 0, "medium similarity": 0, "similarity": 0}
        level_found = {"baseline": False, "medium similarity": False, "similarity": False}
        
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
                            
                            if s== self.questions[level][module]["max_qr_level"]:
                                
                                completed_questions += self.questions[level][module]["current_state"][s]
                                
                # If 80% of the relevant are completed, the skill level is considered to be completed as well
                if completed_questions >= n_relevant_questions * 0.8:
                    current_skill_levels[skill] = level + 1

                # Otherwise, the skill level is not completed and the last skill level is the one the learner is at at the moment 
                else:
                    level_found[skill] = True
        return current_skill_levels

    #def calculate_current_progress(self):
    #    """Calculates and Returns the progress (skill level + (sum of qr levels of relevant questions)/(sum of maximal qr level of relevant questions)) """
    #    current_progress = {"baseline": 0, "medium similarity": 0, "similarity": 0}
    #    current_skill_levels = self.calculate_current_skill_levels()

    #    for skill in current_skill_levels:
    #        skill_level = current_skill_levels[skill]
    #        if skill_level > self.max_level:
    #            skill_level = self.max_level
    #        goal_sum = 0
    #        progress_sum = 0
    #        for module in self.minigame_to_modules_mapping:
    #            if skill in self.questions[skill_level][module]["associated_skills"]:
    #                goal_sum += self.get_max_qr(skill_level) * self.questions[skill_level][module]["count_all"]
    #                for state in self.questions[skill_level][module]["current_state"]:
    #                    progress_sum += state* self.questions[skill_level][module]["current_state"][state]
    #                    
            
    #        current_progress[skill] = skill_level + progress_sum / goal_sum

    #    return current_progress

    def calculate_current_progress(self, current_goal):
        """Calculates and Returns the progress (skill level + (sum of qr levels of relevant questions)/(sum of maximal qr level of relevant questions)) """
        current_progress = {"baseline": 0, "medium similarity": 0, "similarity": 0}
        #current_skill_levels = self.calculate_current_skill_levels()
        skill_level = int(current_goal[0] - 1)
        if skill_level > self.max_level:
                skill_level = self.max_level
        for skill in current_progress:
            #skill_level = current_skill_levels[skill]
            
            goal_sum = 0
            progress_sum = 0
            for module in self.minigame_to_modules_mapping:
                if skill in self.questions[skill_level][module]["associated_skills"]:
                    goal_sum += self.get_max_qr(skill_level) * self.questions[skill_level][module]["count_all"]
                    for state in self.questions[skill_level][module]["current_state"]:
                        progress_sum += state* self.questions[skill_level][module]["current_state"][state]
                        
           
            current_progress[skill] = skill_level + progress_sum / goal_sum

        return current_progress

    def calculate_current_progress2(self, current_goal):
        """Calculates and Returns the progress (skill level + (sum of qr levels of relevant questions)/(sum of maximal qr level of relevant questions)) """
        current_progress = {"baseline": 0, "medium similarity": 0, "similarity": 0}
        current_skill_levels = self.calculate_current_skill_levels()
        skill_level = int(current_goal[0] - 1)
        if skill_level > self.max_level:
                skill_level = self.max_level
        for skill in current_progress:
            #skill_level = current_skill_levels[skill]
            
            goal_sum = 0
            progress_sum = 0
            for module in self.minigame_to_modules_mapping:
                if skill in self.questions[skill_level][module]["associated_skills"]:
                    goal_sum += self.get_max_qr(skill_level) * self.questions[skill_level][module]["count_all"]
                    for state in self.questions[skill_level][module]["current_state"]:
                        progress_sum += state* self.questions[skill_level][module]["current_state"][state]
                        
           
            current_progress[skill] = skill_level + progress_sum / goal_sum
            if current_skill_levels[skill] == current_goal[0]:
                current_progress[skill] += 1

        return current_progress    


    def get_max_qr(self, level):
        # Questions of level 0 and 1 have a maximal QR-Level of 3, all other Questions 5
        return 4 


    def get_state(self):
        """Returns the state of the Question Recycler in the format needed for the MDP"""


        state = []
        for level in  range(len(self.n_questions_per_skill_level)):
            
            for module in self.minigame_to_modules_mapping:
                # the state order is used to guarantee consistency 
                for group in self.state_order:
                    state.append(self.questions[level][module]["current_state"][group])
        
        return tuple(state)
 
    
    def set_state(self, state):
        """Set the State of the Question Recycler according to the input state given in MDP format"""
        self.check()
        i = 0
        for level in  range(len(self.n_questions_per_skill_level)):
            for module in self.minigame_to_modules_mapping:
                for group in self.state_order:
                    
                    self.questions[level][module]["current_state"][group] = state[i]
                    
                    i = i+1
        self.check()

    

        


        



            

