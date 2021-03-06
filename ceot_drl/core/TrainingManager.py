""" 
    Training Manager. It takes an agent, environement and runs the scenario for a set of episodes.
"""


from MLS.ceot_drl.core.AbstractAgent import AbstractAgent
from MLS.ceot_drl.core.AbstractEnvironment import AbstractEnvironement

from collections import deque # to mantian the last k rewards

import matplotlib.pyplot as plt


class TrainingManager:
    def __init__(self,
                 num_episodes,
                 episode_length,
                 agent:AbstractAgent,
                 env:AbstractEnvironement,
                 average_reward_steps=5,
                 log_file='training_log.txt'):

        """TrainingManager initializer.

        Keyword arguments:
        num_episodes -- number of episodes
        episode_length -- length of an episode
        agent -- a RL agent, see AbstractAgent
        env  -- an environement object, see AbstractEnvironment 
        average_reward_steps -- number of last episodes where the average reward is calculated from
        device -- where will the neural networks be trained ("cpu", "gpu"). If multiple gpus exist the manager will choose the first avialable.
        """

        self.num_episodes = num_episodes
        self.episode_length = episode_length
        self.agent = agent
        self.env = env
        self.average_reward_steps = average_reward_steps
        self.log_file = log_file



    def run(self, verbose=False, plot=False, save_to_file=True, parallel=False):
        """ Run the RL scenario using the settings of the TrainingManager
        
        
        Keyword arguments:
        verbose -- if True, the manager will print the total reward for each epsiode and some other statics
        plot -- if True, the manager will plot online learning curve
        parallel -- if True the manager will parallel - NOT SUPPORTED YET.
        """
        
        # do some assertions first
        assert self.agent is not None, "Agent can not be None"
        assert self.env is not None, "Environment object can not be None"
        assert self.average_reward_steps > 1, "Reward must be averaged on more than 1 episode"
        
        # validate the agent is ready for training
        #assert self.agent.validate(), "Agent validation failed"

        # do the magic here, i.e., the main training loop
        last_rewards = deque(maxlen=self.average_reward_steps)
        all_rewards = []
        total_steps = 0
        with open(self.log_file,mode='w') as log:
            for i in range(self.num_episodes): 
                # 1 and 2- reset the environement and get initial state
                state = self.env.reset()
                # 3 get first action
                action = self.agent.get_policy_action(state)
                
                # 4 - iterate over the episode step unitl the agent moves to a terminal state or 
                # the episode ends 
                step = 1
                epsiode_done = False
                episode_reward = 0
                actions_list =[]
                while not epsiode_done and step < self.episode_length:
                    # record actions
                    actions_list.append(action)
                    # call step function in the environement
                    state_, reward, done, extra_signals = self.env.step(action)
                    episode_reward += reward
                    if done == 1:
                        epsiode_done = True

                    # Call learn function in the agent. To learn for the last experience
                    self.agent.learn(total_steps, step, state, state_, reward, action, done, extra_signals)
                    # next state-action pair
                    state = state_
                    action = self.agent.get_policy_action(state)
                    step += 1
                    total_steps += 1
                if verbose:
                    print('Episode:{}\treward:{}\tsteps:{}'.format(i, episode_reward, step))
                all_rewards.append(episode_reward)
                last_rewards.append(episode_reward)
                average_reward = sum(last_rewards)/self.average_reward_steps
                log.write(str(step)+ "\t" + str(episode_reward)+ "\t" + str(average_reward) + "\tActions list:" + str(actions_list) + "\n")
        
        # plot things
        plt.plot(all_rewards)
        #plt.plot(average_reward)
        plt.xlim((1, self.num_episodes))
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.show()