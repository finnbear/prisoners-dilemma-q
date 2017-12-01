# Script section
import sys
import random
from time import time
from matplotlib import pyplot as plt

# Configuration section
population_size = 15  # How many AIs in the population
mentor_instances = 2  # How many instances of each defined strategy there are
episode_length = 100  # How many turns to play
dve = 0.5  # During vs. ending reward
training_time = 4  # How long to train in seconds per agent

# Prisoner's dilemma rewards [Player 1 reward, Player 2 reward]
reward_matrix = [[[2, 2],  # Both players cooperate
                  [0, 3],  # Player 1 cooperates, player 2 defects
                  [3, 0],  # Player 1 defects, player 2 cooperates
                  [1, 1]]]  # Both players defect


# Human agents pick which action to perform
class AgentHuman:
    @staticmethod
    def pick_action(state):
        action_p = -1

        # Print the given state
        print("State: " + str(state) + " (" + str(len(state)) + "/" + str(episode_length) + ")")

        # Repeat until valid input provided
        while action_p not in [0, 1]:
            try:
                # Parse human's chosen action
                action_p = int(input("Choose Cooperate/Defect (0/1): "))
            except ValueError:
                # Prompt human for valid input
                print("Please input a number.")

        return action_p

    def reward_action(self, state, action_p, reward):
        pass


# Q agents learn the best action to perform for every state encountered
class AgentQ:
    def __init__(self, memory):
        self.wins = 0  # Number of times agent has won an episode
        self.losses = 0  # Number of times agent has lost an episode
        self.Q = {}  # Stores the quality of each action in relation to each state
        self.memory = memory  # The number of previous states the agent can factor into its decision
        self.epsilon_counter = 1  # Inversely related to learning rate

    def get_q(self, state):
        quality1 = self.Q[str(state[-self.memory:])][0]
        quality2 = self.Q[str(state[-self.memory:])][1]

        return quality1, quality2

    def set_q(self, state, quality1, quality2):
        self.Q[str(state[-self.memory:])][0] = quality1
        self.Q[str(state[-self.memory:])][1] = quality2

    def normalize_q(self, state):
        quality1, quality2 = self.get_q(state)

        normalization = min(quality1, quality2)

        self.set_q(state, (quality1 - normalization) * 0.95, (quality2 - normalization) * 0.95)

    def max_q(self, state):
        quality1, quality2 = self.get_q(state)

        if quality1 == quality2 or random.random() < (1 / self.epsilon_counter):
            return random.randint(0, 1)
        elif quality1 > quality2:
            return 0
        else:
            return 1

    def pick_action(self, state):
        # Decrease learning rate
        self.epsilon_counter += 0.5

        # If the given state was never previously encountered
        if str(state[-self.memory:]) not in self.Q:
            # Initialize it with zeros
            self.Q[str(state[-self.memory:])] = [0, 0]

        return self.max_q(state)

    def reward_action(self, state, action_r, reward):
        # Increase the quality of the given action at the given state
        self.Q[str(state[-self.memory:])][action_r] += reward

        # Normalize the Q matrix
        self.normalize_q(state)

    def mark_victory(self):
        self.wins += 1

    def mark_defeat(self):
        self.losses += 1

    def analyse(self):
        # What percentage of games resulted in victory/defeat
        percent_won_q = 0
        if self.wins > 0:
            percent_won_q = float(self.wins) / (self.wins + self.losses)
        '''
        percent_lost_q = 0
        if self.losses > 0:
            percent_lost_q = float(self.losses) / (self.wins + self.losses)
        '''
        # How many states will result in cooperation/defection
        times_cooperated = 0
        times_defected = 0

        for state in self.Q:
            action_s = self.max_q(eval(state))

            if action_s == 0:
                times_cooperated += 1
            else:
                times_defected += 1

        # What percentage of states will result in cooperation/defection
        percent_cooperated = 0
        if times_cooperated > 0:
            percent_cooperated = float(times_cooperated) / len(self.Q)
        '''
        percent_defected = 0
        if times_defected > 0:
            percent_defected = float(times_defected) / len(self.Q)
        '''
        # Return most relevant analysis
        return self.wins, percent_won_q, percent_cooperated

    def reset_analysis(self):
        self.wins = 0
        self.losses = 0


# Defined agents know which action to perform
class AgentDefined:
    def __init__(self, strategy):
        self.wins = 0  # Number of times agent has won an episode
        self.losses = 0  # Number of times agent has lost an episode
        self.strategy = strategy

    def pick_action(self, state):
        if self.strategy == 0:  # Tit for tat
            if len(state) == 0:  # On the first tern
                return 0  # Cooperate
            else:  # Otherwise
                return state[-1]  # Pick the last action of the opponent
        elif self.strategy == 1:  # Holds a grudge
            if 1 in state:  # If the enemy has ever defected
                return 1  # Defect
            else:  # Otherwise
                return 0  # Cooperate

    def reward_action(self, state, action_r, reward):
        pass  # Since these agents are defined, no learning occurs

    def mark_victory(self):
        self.wins += 1

    def mark_defeat(self):
        self.losses += 1

    def analyse(self):
        # What percentage of games resulted in victory/defeat
        percent_won = 0
        if self.wins > 0:
            percent_won = float(self.wins) / (self.wins + self.losses)
        '''
        percent_lost = 0
        if self.losses > 0:
            percent_lost = float(self.losses) / (self.wins + self.losses)
        '''
        # Return most relevant analysis
        return self.wins, percent_won


# Stores all AIs
population = []

# Stores record of analysis of all AIs
population_analysis = []

# Stores all instances of defined strategies
mentors = []

# TODO: Mentor analysis

# Create a random AI with a random amount of memory
for i in range(population_size):
    population.append(AgentQ(random.randint(2, 5)))

# Create instances of defined strategies
for i in range(2):  # Number of defined strategies
    for j in range(mentor_instances):
        mentors.append(AgentDefined(i))

# Training time initialization
start_time = time()
remaining_time = training_time * population_size
last_remaining_time = int(remaining_time)

# Training mode with AIs
while remaining_time > 0:
    # Calculate remaining training time
    remaining_time = start_time + training_time * population_size - time()

    # Things to be done every second
    if 0 < remaining_time < last_remaining_time:
        # Alert user to remaining time
        sys.stdout.write('\r')
        sys.stdout.flush()
        sys.stdout.write("Training time remaining: %.1f " % remaining_time)
        sys.stdout.flush()
        last_remaining_time = int(remaining_time * 2) / float(2)

        # Analyse population
        if time() > start_time + 0.5:
            time_step = []
            for agent in population:
                time_step.append(agent.analyse())
                agent.reset_analysis()
            population_analysis.append(time_step)

            # TODO: Analyse mentors

    state1 = []  # State visible to player 1 (actions of player 2)
    state2 = []  # State visible to player 2 (actions of player 1)

    # Pick a random member of the population to serve as player 1
    player1 = random.choice(population)

    # Pick a random member of the population or a defined strategy to serve as player 2
    player2 = random.choice(population + mentors)

    for i in range(episode_length):
        action = None

        action1 = player1.pick_action(state1)  # Select action for player 1
        action2 = player2.pick_action(state2)  # Select action for player 2

        state1.append(action2)  # Log action of player 2 for player 1
        state2.append(action1)  # Log action of player 1 for player 2

    # Stores the total reward over all games in an episode
    total_reward1 = 0
    total_reward2 = 0

    for i in range(episode_length):
        action1 = state2[i]
        action2 = state1[i]

        reward1 = 0  # Total reward due to the actions of player 1 in the entire episode
        reward2 = 0  # Total reward due to the actions of player 2 in the entire episode

        # Calculate rewards for each player
        if action1 == 0 and action2 == 0:  # Both players cooperate
            reward1 = reward_matrix[0][0][0]
            reward2 = reward_matrix[0][0][1]
        elif action1 == 0 and action2 == 1:  # Only player 2 defects
            reward1 = reward_matrix[0][1][0]
            reward2 = reward_matrix[0][1][1]
        elif action1 == 1 and action2 == 0:  # Only player 1 defects
            reward1 = reward_matrix[0][2][0]
            reward2 = reward_matrix[0][2][1]
        elif action1 == 1 and action2 == 1:  # Both players defect
            reward1 = reward_matrix[0][3][0]
            reward2 = reward_matrix[0][3][1]

        total_reward1 += reward1
        total_reward2 += reward2

        player1.reward_action(state1[:i], action1, reward1 * dve)  # Assign reward to action of player 1
        player2.reward_action(state2[:i], action2, reward2 * dve)  # Assign reward to action of player 2

    # Assign reward for winning player
    if total_reward1 > total_reward2:
        reward_chunk = total_reward1 / episode_length * (1 - dve)

        for i in range(episode_length):
            action1 = state2[i]

            player1.reward_action(state1[:i], action1, reward_chunk)

            player1.mark_victory()
            player2.mark_defeat()
    elif total_reward2 > total_reward1:
        reward_chunk = total_reward2 / episode_length * (1 - dve)

        for i in range(episode_length):
            action2 = state1[i]

            player2.reward_action(state2[:i], action2, reward_chunk)

            player1.mark_victory()
            player2.mark_defeat()

# Start new line
print("")

# Plot analysis of AIs
victories_percent_stack_x = []
victories_percent_stack_y = []
victories_percent_stack_colors = []

for i in range(len(population_analysis[-1])):
    victories_percent_stack_y.append([])

    wins, percent_to_win, percent_to_cooperate = population_analysis[-1][i]
    victories_percent_stack_colors.append(str(percent_to_cooperate))

i = 0
for time_step in population_analysis:
    victories_percent_stack_x.append(i + 1)

    total_wins = 0

    for agent_analysis in time_step:
        wins, percent_to_win, percent_to_cooperate = agent_analysis

        total_wins += percent_to_win

    j = 0
    for agent_analysis in time_step:
        wins, percent_to_win, percent_to_cooperate = agent_analysis

        victories_percent = 0
        if wins > 0:
            victories_percent = float(percent_to_win) / total_wins

        victories_percent_stack_y[j].append(victories_percent)

        j += 1

    i += 1

fig = plt.figure()

ax1 = fig.add_subplot(121)

ax1.stackplot(victories_percent_stack_x, victories_percent_stack_y, colors=victories_percent_stack_colors)

ax2 = fig.add_subplot(122)

for i in range(len(victories_percent_stack_y)):
    ax2.plot(victories_percent_stack_x, victories_percent_stack_y[i], c=victories_percent_stack_colors[i], linewidth=1,
             alpha=0.95)

plt.show()

# Testing mode
wins_p1 = 0
wins_p2 = 0
while (wins_p1 and wins_p2) <= 100:
    state1 = []  # State visible to player 1 (actions of player 2)
    state2 = []  # State visible to player 2 (actions of player 1)

    # Use a human to serve as player 1
    player1 = AgentDefined(1)

    # Use a random AI to serve as player 2
    player2 = random.choice(population)

    for i in range(episode_length):
        # #####actions = None

        action1 = player1.pick_action(state1)  # Allow player 1 to pick action
        action2 = player2.pick_action(state2)  # Select action for player 2

        state1.append(action2)  # Log action of player 2 for player 1
        state2.append(action1)  # Log action of player 1 for player 2

    total_reward1 = 0
    total_reward2 = 0

    for i in range(episode_length):
        action1 = state2[i]
        action2 = state1[i]

        reward1 = 0  # Total reward due to the actions of player 1 in the entire episode
        reward2 = 0  # Total reward due to the actions of player 2 in the entire episode

        # Calculate rewards for each player
        if action1 == 0 and action2 == 0:  # Both players cooperate
            reward1 = reward_matrix[0][0][0]
            reward2 = reward_matrix[0][0][1]
        elif action1 == 0 and action2 == 1:  # Only player 2 defects
            reward1 = reward_matrix[0][1][0]
            reward2 = reward_matrix[0][1][1]
        elif action1 == 1 and action2 == 0:  # Only player 1 defects
            reward1 = reward_matrix[0][2][0]
            reward2 = reward_matrix[0][2][1]
        elif action1 == 1 and action2 == 1:  # Both players defect
            reward1 = reward_matrix[0][3][0]
            reward2 = reward_matrix[0][3][1]

        total_reward1 += reward1
        total_reward2 += reward2

    # Print the winning player and score
    print("Score: " + str(total_reward1) + " to " + str(total_reward2))
    if total_reward1 > total_reward2:
        print("Player 1 wins!")
        wins_p1 += 1
    elif total_reward2 > total_reward1:
        print("Player 2 loses!")
        wins_p2 += 1
    else:
        print("Tie!")
        wins_p1 += 0.5
        wins_p2 += 0.5
print("P1: {0}, P2: {1}".format(str(wins_p1), str(wins_p2)))
