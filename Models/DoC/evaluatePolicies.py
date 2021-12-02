from random import sample
from Environment import Environment 
from Agents import ValueIterAgent, RandomAgent, MyopicApproxAgent, HandCraftedAgent_V3, HandCraftedAgent_Exp, HandCraftedAgent, MyopicAgent, DataFrequencyAgent, InGameRewardMaximizingAgent, ApproxQ_sa_Agent
import numpy as np
import pickle





def policy_eval(agent, episodes, runs, param_dict, reduced = False):
    """Lets an agent interact with the MDP for a given number of episodes for a given number of runs and returns the collected rewards and achieved levels"""

    with open("result_files/value_function_3Modules_23Q_varNQ.p", "rb") as f:
        v = pickle.load(f)
    
    results = {}
    for run in range(runs):
        print(run)
        env = env = Environment(
                  skills_goal = np.array([1.,1.,1.,1.,1.,1.]), 
                  final_goal= np.array([3.,3.,3.,3.,3.,3.]),
                  param_dict = param_dict,
                  reduced = reduced)
        if agent == "Myopic":
            learner = MyopicAgent(env)
        elif agent == "Myopic_OptPseudoRewards":
            learner = MyopicAgent(env, apply_pseudo_rewards = True, value_function = v, mode = None)
        elif agent == "Myopic_OptPseudoRewards_Scaled":
            learner = MyopicAgent(env, apply_pseudo_rewards = True, value_function = v, mode = "scaled")
        elif agent == "MyopicApprox":
            learner = MyopicApproxAgent(env)
        elif agent == "MyopicApprox_wR":
            learner = MyopicApproxAgent(env, consider_reward = True)
        elif agent == "HandCrafted":
            learner = HandCraftedAgent(env)
        elif agent == "Random":
            learner = RandomAgent(env)
        elif agent == "DataFreq":
            learner = DataFrequencyAgent(env)
        elif agent == "InGameRewardMaxmizer":
            learner = InGameRewardMaximizingAgent(env)
        elif agent == "HandCrafted_Exp":
            learner = HandCraftedAgent_Exp(env)
        elif agent == "HandCrafted_V3":
            learner = HandCraftedAgent_V3(env)
        elif agent == "ApproxQ_sa_Agent":
            with open("weights_0730_A11_1f.p", "rb") as f:
                weights = pickle.load(f)
            learner = ApproxQ_sa_Agent(env, weights= weights)
        else:
            print("Define exsisting learner")
            assert False

        rewards = []
        levels = []
        observation = env.reset()
        level = 0
        for t in range(episodes):
            
            action = learner.choose_action(observation)
            observation, reward, done, info = env.step(action)

            # done is in reference to the current skill goal
            if done:
                level += 1
            rewards.append(reward)
            levels.append(level)

            # terminated is in reference to the highest possible skill goal 
            if info["terminated"]:
                for x in range(t, episodes):
                    levels.append(level)
                    rewards.append(sum(rewards))

                break

        
        
        results[run] = {"rewards": rewards, "levels": levels}

    return results 


    



        



# get from data 
with open("./game_data_dists.p","rb") as f:
    param_dict = pickle.load(f)

eval_results = {}
# agents / policies to evaulate 
agents = [ "HandCrafted", "ApproxQ_sa_Agent", "Random" ]
for agent in agents:
    print("Evaluating ", agent)
    eval_results[agent] = policy_eval(agent = agent, episodes = 2500, runs = 15, param_dict = param_dict, reduced= False)

    with open("./policy_eval_singlefeature_level.p", "wb") as f:
        pickle.dump(eval_results, f)
