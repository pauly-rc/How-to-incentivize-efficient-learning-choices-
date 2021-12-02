# How to incentivize efficient learning choices?
 
 This is the implementation of the MDP described in the thesis "How to incentivize efficient learning choices in digitallearning  environments? A reinforcement  learning  ap-proach applied to an educational game. 

## Experiments
The folder Experiments contains the implementation of the three described experiments, which is based on https://github.com/fredcallaway/psirokuturk. 


## Models 
The folder Models contains the implementation of both the Dawn of Civilisations and the Experimental MDPs.
The MDPs themselves are implemented in the files Environment.py, QR.py and QR_paramters.py, respectively. 
All the described simulated agents are implemented in Agents.py.
The executable files are the following, but beware that many of them were only excecuted on the MPI's cluster and might take up to 4 days to complete.
The optimal vallue function and the optimal policy are computed and saved by running computeValueFunction.py
The state space has to be calculated prior to that by running defineStateSpace.py
The results of the simulated agents are gathered by running evaluatePolicies.py


Especially in the Experimental model, the optimal brain points were computed and saved by running compute_brain_points.py
The value function needs to be already calculated for that.
The approximated brain points can be calculated and saved by running approximate_brain_points.py.
This depends on having calcuated the state space.

Both the resulting points files can be scaled to integers between 0 and 5 and brought to a smaller size (important for including them in the online experiment) by running scale_brainpoints.py

## Results
The folder Results contains the data from the simulated evaluation, the stimulus pretests and the main experiments and the jupyter notebooks used to derive the analyses and visualizations. 