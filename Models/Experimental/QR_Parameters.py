# Number Of Questions for each skill level and game taken from https://docs.google.com/spreadsheets/d/1OyLlZQk4_gHhSAdUbgK2runAI2rH7ofJ6ar8zMii7IQ/edit#gid=0
def get_game_names():
       """Returns list of mini-game names.
       Param: reduced (boolean): If true, returns list for small MDP """
       return ["baseline", "medium similarity","similarity"]
    
                   
def get_n_questions_per_skill_level():
       """Returns a dictionary containing the overall number of questions (across all skills) per level
       Param: reduced (boolean): If true, returns mapping for small MDP """
       
       return    {"PreA.1":20,
                  #"PreA.2":12
              }
     



 

def get_number_of_questions_per_minigame():
       """Returns a dictionary containing a discrete probability distribution P(n_questions = x) for each minigame, describing how likely the game is to present x questions.
       The probabilites are caluclated from the QR-Data provided by Solve Education. 
       Param: reduced (boolean): If true, returns mapping for small MDP """
       return {  'baseline': [0., 0., 0., 1. , 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                      'medium similarity':   [0., 0., 0., 1., 0. , 0., 0., 0., 0., 0. , 0., 0., 0., 0., 0. , 0., 0., 0.], 
                     'similarity':  [0., 0., 0., 1., 0., 0., 0., 0. , 0., 0., 0., 0., 0., 0., 0., 0. , 0., 0.],
                     
                     }
       

def get_minigame_to_skill_mapping():
       """Returns a nested dictionary. For each minigame, a dictionary containing the skill names as keys and boolean values as items, 
       describing whether the game trains the skill.  
       Param: reduced (boolean): If true, returns mapping for small MDP """
       return { 
                     "baseline": {"baseline": True, "medium similarity": False, "similarity": False},
                     "medium similarity": {"baseline": False, "medium similarity": True, "similarity": False},
                     "similarity": {"baseline": False, "medium similarity": False, "similarity": True},
               
                     }
   


def get_questions_per_module_per_skill_level():
       """Returns a nested dictionary. For each level a dictionary containing the modules as keys and int values as items, 
       describing hoe many questions belong to that module at that level.  
       Param: reduced (boolean): If true, returns mapping for small MDP """
       return {0:{0: 4, 1: 8, 2: 8},
              # 1:{0: 4, 1: 4, 2: 4}
       
                    
                     }

              

def get_minigame_to_modules_mapping():
       """Returns dictionary with module IDs as keys and lists of minigame names as values, 
       describing which minigames belong to which module.  
       """
       return {0: ["baseline"],
               1: ["medium similarity"],
               2: ["similarity"]
               
              }

def get_modules_to_minigames_mapping():
       """Returns dictionary withminiame names as keys and module ids as values, 
       describing to which module the minigame belongs.  
       """
       return {"baseline": 0,
               "medium similarity": 1,
               "similarity" : 2,
              }

            
def get_module_to_skill_mapping():
       """Returns a nested dictionary. For each module, a dictionary containing the skill names as keys and boolean values as items, 
       describing whether the game trains the skill.  
       """
       return { 
                     0: {"baseline": True, "medium similarity": False, "similarity": False},
                     1: {"baseline": False, "medium similarity": True, "similarity": False},
                     2: {"baseline": False, "medium similarity": False, "similarity": True},
               
                     }


