import random
from time import time

population_size = 20
mentors_size = 5
episode_length = 10 # How many turns to play
dve = 0.1 # During vs. ending reward
training_time = 6 # How long to train per agent

# Human agents pick which action to perform
class Agent_Human:
	def pick_action(self, state):
		action = -1

		print("State: " + str(state) + " (" + str(len(state)) + "/" + str(episode_length) + ")")

		while (action != 0 and action != 1):
			try:
				action = int(raw_input("Choose Cooperate/Defect (0/1): "))
			except ValueError:
				print("Please input a number.")
		
		return action
	def reward_action(self, state, action, reward):
		pass

# Q agents learn the best action to perform for every state encountered
class Agent_Q:
	def __init__(self, memory):
		self.Q = {} # Stores the quality of each action in relation to each state
		self.memory = memory
		self.epsilon_counter = 1

	def pick_action(self, state):
		self.epsilon_counter += 0.25

		if str(state[-self.memory:]) not in self.Q:
			self.Q[str(state[-self.memory:])] = [0, 0]

		if self.Q[str(state[-self.memory:])][0] == self.Q[str(state[-self.memory:])][1] or random.random() < 1 / self.epsilon_counter:
			return random.randint(0, 1)
		else:
			if self.Q[str(state[-self.memory:])][0] > self.Q[str(state[-self.memory:])][1]:
				return 0
			else:
				return 1

	def reward_action(self, state, action, reward):
		self.Q[str(state[-self.memory:])][action] += reward

# Defined agents know which action to perform
class Agent_Defined:
	def __init__(self, strategy):
		self.strategy = strategy

	def pick_action(self, state):
		if (self.strategy == 0):
			if len(state) == 0:
				return 0
			else:
				return state[-1]
		elif (self.strategy == 1):
			if 1 in state:
				return 1
			else:
				return 0

	def reward_action(self, state, action, reward):
		pass

population = []
mentors = []

for i in range(population_size):
	population.append(Agent_Q(random.randint(2, 5)))

for i in range(mentors_size):
	mentors.append(Agent_Defined(random.randint(0, 1)))

# Training mode
start_time = time()
remaining_time = training_time * population_size
last_remaining_time = int(remaining_time)

while remaining_time > 0:
	remaining_time = start_time + training_time * population_size - time()

	if 0 < remaining_time < last_remaining_time:
		print("Training time remaining: %.0f" % remaining_time)
		last_remaining_time = int(remaining_time)

	state1 = [] # State visible to player 1
	state2 = [] # State visible to player 2

	player1 = random.choice(population)
	player2 = random.choice(population + mentors)

	for i in range(episode_length):
		action = None

		action1 = player1.pick_action(state1) # Select action for player 1
		action2 = player2.pick_action(state2) # Select action for player 2

		state1.append(action2) # Log action of player 2 for player 1
		state2.append(action1) # Log action of player 1 for player 2

	total_reward1 = 0
	total_reward2 = 0

	for i in range(episode_length):
		action1 = state2[i]
		action2 = state1[i]

		reward1 = 0 # Total reward due to the actions of player 1 in the entire episode
		reward2 = 0 # Total reward due to the actions of player 2 in the entire episode

		# Calculate rewards for each player
		if action1 == 0 and action2 == 0: # Both players cooperate
			reward1 = 1
			reward2 = 1
		elif action1 == 0 and action2 == 1: # Only player 2 defects
			reward1 = 0
			reward2 = 5
		elif action1 == 1 and action2 == 1: # Both players defect
			reward1 = 3
			reward2 = 3
		elif action1 == 1 and action2 == 0: # Only player 1 defects
			reward1 = 5
			reward2 = 0

		total_reward1 += reward1
		total_reward2 += reward2

		player1.reward_action(state1[:i], action1, reward1 * dve) # Assign reward to action of player 1
		player2.reward_action(state2[:i], action2, reward2 * dve) # Assign reward to action of player 2

	# Assign reward for winning player
	if total_reward1 > total_reward2:
		reward_chunk = total_reward1 / episode_length * (1 - dve)

		for i in range(episode_length):
			action1 = state2[i]

			player1.reward_action(state1[:i], action1, reward_chunk)
	elif total_reward2 > total_reward1:
		reward_chunk = total_reward2 / episode_length * (1 - dve)

		for i in range(episode_length):
			action2 = state1[i]

			player2.reward_action(state2[:i], action2, reward_chunk)

# Testing mode
while True:
	state1 = [] # State visible to player 1
	state2 = [] # State visible to player 2

	player1 = Agent_Human()
	player2 = random.choice(population)

	for i in range(episode_length):
		action = None

		action1 = player1.pick_action(state1) # Allow player 1 to pick action
		action2 = player2.pick_action(state2) # Select action for player 2

		state1.append(action2) # Log action of player 2 for player 1
		state2.append(action1) # Log action of player 1 for player 2

	total_reward1 = 0
	total_reward2 = 0

	for i in range(episode_length):
		action1 = state2[i]
		action2 = state1[i]

		reward1 = 0 # Total reward due to the actions of player 1 in the entire episode
		reward2 = 0 # Total reward due to the actions of player 2 in the entire episode

		# Calculate rewards for each player
		if action1 == 0 and action2 == 0: # Both players cooperate
			reward1 = 2
			reward2 = 2
		elif action1 == 0 and action2 == 1: # Only player 2 defects
			reward1 = 0
			reward2 = 4
		elif action1 == 1 and action2 == 1: # Both players defect
			reward1 = 1
			reward2 = 1
		elif action1 == 1 and action2 == 0: # Only player 1 defects
			reward1 = 4
			reward2 = 0

		total_reward1 += reward1
		total_reward2 += reward2

	# Print the winning player and score
	print("Score: " + str(total_reward1) + " to " + str(total_reward2))
	if total_reward1 > total_reward2:
		print("You win!")
	elif total_reward2 > total_reward1:
		print("You lose!")
	else:
		print("Tie!")