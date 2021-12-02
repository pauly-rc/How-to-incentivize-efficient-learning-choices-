# Number Of Questions for each skill level and game taken from https://docs.google.com/spreadsheets/d/1OyLlZQk4_gHhSAdUbgK2runAI2rH7ofJ6ar8zMii7IQ/edit#gid=0
def get_game_names(reduced):
       """Returns list of mini-game names.
       Param: reduced (boolean): If true, returns list for small MDP """
       if reduced:
             # return ["speak racer", "copy cat", "hello cafe", "brain battle"]
              #return ["speak racer", "hello cafe"]
              return ["speak racer", "copy cat","hello cafe"]
       else:
              return ["fix the mix", "speak racer", "copy cat", "copy parrot", "typing time", "brain battle", "factory card", "robot factory", "word snap", "hello cafe", "flying robot", "chat time","tick talk", "eye spy", "judge me", "talk n' go"]
                   
def get_n_questions_per_skill_level(reduced):
       """Returns a dictionary containing the overall number of questions (across all skills) per level
       Param: reduced (boolean): If true, returns mapping for small MDP """
       if reduced:
              return    {"PreA.1":10,
                         "PreA.2":13,
                         }
       else:
              return {"PreA.1":64,
                     "PreA.2":80, 
                     "A1.1": 1188,
                     "A1.2": 864,
                     "A1.3": 651, 
                     "A2.1": 1463,
                     "A2.2": 994, 
                     "A2.3": 353,
                     "B1.1": 376,
                     "B1.2": 272,
                     "B1.3": 303, 
                     "B2.1": 347,
                     "B2.2": 261, 
                     "B2.3": 391,
                     "C1.1": 440,
                     "C1.2": 433
                     }



 
"""
def get_number_of_questions_per_minigame(reduced):
       Returns a dictionary containing a discrete probability distribution P(n_questions = x) for each minigame, describing how likely the game is to present x questions.
       The probabilites are caluclated from the QR-Data provided by Solve Education. 
       Param: reduced (boolean): If true, returns mapping for small MDP 
       if reduced:
              return {  'speak racer': [1., 0., 0., 0. , 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.],
                      'copy cat':   [0., 1., 0., 0., 0. , 0., 0., 0., 0., 0. , 0., 0., 0., 0., 0. , 0., 0., 0.], 
                     'hello cafe':  [1., 0., 0., 0., 0., 0., 0., 0. , 0., 0., 0., 0., 0., 0., 0., 0. , 0., 0.],
                     "brain battle": [0., 1., 0., 0., 0. , 0., 0., 0., 0., 0. , 0., 0., 0., 0., 0. , 0., 0., 0.]
                     }
       else:
              return {'fix the mix': [0.00564175, 0.00423131, 0.01057828, 0.01692525, 0.03526093, 0.87165021, 0.03949224, 0., 0.00423131, 0.,
                            0.0077574 , 0.00423131, 0.        , 0.        , 0.        ,0.        , 0.        , 0.        ],
                     'speak racer': [0.0096463 , 0.01286174, 0.0096463 , 0.00643087, 0.01607717, 0.92604502, 0.        , 0.        , 0.        , 0.        ,
                                   0.00482315, 0.01446945, 0.        , 0.        , 0.        , 0.        , 0.        , 0.        ],
                     'copy cat': [0.00428135, 0.00733945, 0.00183486, 0.        , 0.        ,
                            0.92110092, 0.01590214, 0.00611621, 0.00366972, 0.        ,
                            0.00672783, 0.03302752, 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'copy parrot': [0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.54545455, 0.        , 0.45454545, 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'typing time': [0.00111857, 0.        , 0.0033557 , 0.00223714, 0.        ,
                            0.93624161, 0.00391499, 0.        , 0.0033557 , 0.        ,
                            0.        , 0.03020134, 0.        , 0.        , 0.        ,
                            0.00894855, 0.        , 0.0106264 ],
                     'brain battle': [0.35272727, 0.45090909, 0.10909091, 0.01454545, 0.02545455,
                            0.02181818, 0.02545455, 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'factory card': [0.03043478, 0.04347826, 0.05217391, 0.03478261, 0.36956522,
                            0.44347826, 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.02608696, 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'robot factory': [3.40020401e-04, 6.80040802e-04, 0.00000000e+00, 0.00000000e+00,
                            0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                            0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
                            1.32607956e-02, 1.42808569e-01, 3.41720503e-01, 4.78748725e-01,
                            1.15606936e-02, 1.08806528e-02],
                     'word snap': [0.05080214, 0.20855615, 0.70320856, 0.02139037, 0.00802139,
                            0.        , 0.        , 0.        , 0.00802139, 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'hello cafe': [0.00124922, 0.00499688, 0.88632105, 0.00749532, 0.01873829,
                            0.01499063, 0.00437227, 0.        , 0.00749532, 0.01249219,
                            0.        , 0.00374766, 0.01623985, 0.        , 0.        ,
                            0.00999375, 0.        , 0.01186758],
                     'flying robot': [0.        , 0.0104712 , 0.        , 0.03141361, 0.85078534,
                            0.06282723, 0.01832461, 0.01308901, 0.        , 0.        ,
                            0.01308901, 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'chat time': [0.        , 0.        , 0.98148148, 0.        , 0.01851852,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'tick talk': [0.00313972, 0.        , 0.96075353, 0.01255887, 0.        ,
                            0.00941915, 0.        , 0.        , 0.00470958, 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.00941915],
                     'eye spy': [0.96296296, 0.        , 0.01234568, 0.        , 0.01234568,
                            0.        , 0.        , 0.01234568, 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     'judge me': [0.94214876, 0.02479339, 0.        , 0.        , 0.00826446,
                            0.        , 0.01652893, 0.00826446, 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ],
                     "talk n' go": [0.99019608, 0.00980392, 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        , 0.        , 0.        ,
                            0.        , 0.        , 0.        ]}

"""
def get_number_of_questions_per_minigame(reduced):
       if reduced:
              return {  'speak racer': 1,
                      'copy cat':   2,
                     'hello cafe':  1,
                     "brain battle": 2
                     }

       return {'fix the mix': 6,
                     'speak racer': 6,
                     'copy cat':6 ,
                     'copy parrot': 6,
                     'typing time': 6,
                     'brain battle': 2,
                     'factory card': 6,
                     'robot factory': 16,
                     'word snap':3 ,
                     'hello cafe':3 ,
                     'flying robot':5,
                     'chat time':3 ,
                     'tick talk': 3,
                     'eye spy': 1,
                     'judge me': 1,
                     "talk n' go": 1}

def get_minigame_to_skill_mapping(reduced):
       """Returns a nested dictionary. For each minigame, a dictionary containing the skill names as keys and boolean values as items, 
       describing whether the game trains the skill.  
       Param: reduced (boolean): If true, returns mapping for small MDP """
       if reduced:
              return { 
                     "speak racer": {"reading": False, "listening": False, "speaking": True, "vocabulary": True, "grammar": False,"writing": False},
                     "copy cat": {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "hello cafe": {"reading": True, "listening": True, "speaking": True, "vocabulary": False,"grammar": True,"writing": True},
                     #"brain battle": {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False}
                     }
       else:
              return {"fix the mix": {"reading": False, "listening": False, "speaking": False, "vocabulary": True, "grammar": False,"writing": True}, 
                     "speak racer": {"reading": False, "listening": False, "speaking": True, "vocabulary": True, "grammar": False,"writing": False},
                     "copy cat": {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "copy parrot" : {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "typing time" : {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "brain battle": {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False},
                     "factory card": {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "robot factory": {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "word snap": {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False },
                     "hello cafe": {"reading": True, "listening": True, "speaking": True, "vocabulary": False,"grammar": True,"writing": True},
                     "flying robot": {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
                     "chat time": {"reading": True, "listening": True, "speaking": True, "vocabulary": False,"grammar": True,"writing": True},
                     "tick talk": {"reading": True, "listening": True, "speaking": True, "vocabulary": False,"grammar": True,"writing": True},
                     "eye spy": {"reading": False , "listening": False, "speaking": True, "vocabulary": False,"grammar": False,"writing": False},
                     "judge me": {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False},
                     "talk n' go": {"reading": False, "listening": False, "speaking": True, "vocabulary": False,"grammar": False,"writing": False}
                     }


def get_questions_per_module_per_skill_level(reduced):
       """Returns a nested dictionary. For each level a dictionary containing the modules as keys and int values as items, 
       describing hoe many questions belong to that module at that level.  
       Param: reduced (boolean): If true, returns mapping for small MDP """
       if reduced:
              #return {0:{0: 0, 1: 2, 2: 6, 3: 0, 4:0, 5:2, 6: 0, 7: 0, 8: 0},
              #        1:{0: 0, 1: 6, 2: 5, 3: 1, 4:0, 5:1, 6: 0, 7: 0, 8: 0}
              #       }
              #return {0:{0: 0, 1: 2, 2: 5, 3: 0, 4:0, 5:1, 6: 0, 7: 0, 8: 0},
              #       1:{0: 0, 1: 5, 2: 4, 3: 0, 4:0, 5: 1, 6: 0, 7: 0, 8: 0}
              #       }
              return {0:{0: 0, 1: 2, 2: 6, 3: 0, 4:0, 5:2, 6: 0, 7: 0, 8: 0},
                     1:{0: 0, 1: 6, 2: 5, 3: 0, 4:0, 5: 2, 6: 0, 7: 0, 8: 0}
                     }
              #return {0:{0: 0, 1: 5, 2: 0, 3: 0, 4:0, 5:3, 6: 0, 7: 0, 8: 0},
              #       1:{0: 0, 1: 4, 2: 0, 3: 0, 4:0, 5: 6, 6: 0, 7: 0, 8: 0}
              #       }
       else:
              return {0:{0: 0, 1: 13, 2: 39, 3: 0, 4:0, 5: 12, 6: 0, 7: 0, 8: 0},
                     1:{0: 0, 1: 36, 2: 32, 3: 0, 4:0, 5: 12, 6: 0, 7: 0, 8: 0},
                     2:{0:0, 1:358, 2:137, 3:8, 4:75, 5:596, 6:8, 7:0, 8:6},
                     3:{0:0, 1:146, 2:124, 3:8, 4:50, 5:522, 6:8, 7:0, 8:6},
                     4:{0:0, 1:109, 2:75, 3:7, 4:50, 5:396, 6:8, 7:0, 8:6},
                     5:{0:35, 1:628, 2:246, 3:8, 4:52, 5:480, 6:8, 7:0, 8:6},
                     6:{0:28, 1:228, 2:64, 3:8, 4:52, 5:600, 6:8, 7:0, 8:6},
                     7:{0:21, 1:73, 2:32, 3:8, 4:25, 5:180, 6:8, 7:0, 8:6},
                     8:{0:16, 1:133, 2:48, 3:7, 4:44, 5:97, 6:8, 7:14, 8:9},
                     9:{0:16, 1:89, 2:36, 3:7, 4:44, 5:48, 6:8, 7:15, 8:9},
                     10:{0:17, 1:124, 2:56, 3:7, 4:44, 5:30, 6:8, 7:9, 8:8},
                     11:{0:36, 1:160, 2:48, 3:6, 4:51, 5:24, 6:0, 7:15, 8:7},
                     12:{0:40, 1:87, 2:32, 3:6, 4:51, 5:24, 6:0, 7:14, 8:7},
                     13:{0:40, 1:218, 2:32, 3:5, 4:34, 5:41, 6:0, 7:14, 8:7},
                     14:{0:18, 1:156, 2:80, 3:4, 4:48, 5:42, 6:0, 7:61, 8:31},
                     15:{0:18, 1:180, 2:81, 3:4, 4:16, 5:42, 6:0, 7:62, 8:30}
                     }

              

def get_minigame_to_modules_mapping():
       """Returns dictionary with module IDs as keys and lists of minigame names as values, 
       describing which minigames belong to which module.  
       """
       return {0: ["fix the mix"],
               1: ["speak racer"],
               2: ["copy cat", "copy parrot", "typing time", "factory card", "robot factory", "flying robot"],
               3: ["brain battle"],
               4: ["word snap"],
               5: ["hello cafe","chat time", "tick talk" ],
               6: ["eye spy"],
               7: ["judge me"],
               8: ["talk n' go"]
              }

def get_modules_to_minigames_mapping():
       """Returns dictionary withminiame names as keys and module ids as values, 
       describing to which module the minigame belongs.  
       """
       return {"fix the mix": 0,
               "speak racer": 1,
               "copy cat" : 2,
               "copy parrot" : 2,
               "typing time": 2, 
               "factory card" : 2, 
               "robot factory": 2, 
               "flying robot" : 2,
               "brain battle" : 3,
               "word snap" : 4,
               "hello cafe" : 5,
               "chat time" : 5, 
               "tick talk" :5,
               "eye spy" :6,
               "judge me" :7,
               "talk n' go" :8
              }

            
def get_module_to_skill_mapping():
       """Returns a nested dictionary. For each module, a dictionary containing the skill names as keys and boolean values as items, 
       describing whether the game trains the skill.  
       """
       return {0: {"reading": False, "listening": False, "speaking": False, "vocabulary": True, "grammar": False,"writing": True}, 
               1: {"reading": False, "listening": False, "speaking": True, "vocabulary": True, "grammar": False,"writing": False},
               2: {"reading": False, "listening": True, "speaking": False, "vocabulary": True,"grammar": False,"writing": False},
               3: {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False},
               4: {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False },
               5: {"reading": True, "listening": True, "speaking": True, "vocabulary": False,"grammar": True,"writing": True},
               6: {"reading": False , "listening": False, "speaking": True, "vocabulary": False,"grammar": False,"writing": False},
               7: {"reading": True, "listening": False, "speaking": False, "vocabulary": False,"grammar": True,"writing": False},
               8: {"reading": False, "listening": False, "speaking": True, "vocabulary": False,"grammar": False,"writing": False}
              }


