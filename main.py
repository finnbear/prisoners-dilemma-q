import random

episode_length = 12

Q = {}

gamma = 0.25

epsilon_counter = 1

def get_epsilon():
	return 1 / float(epsilon_counter)

def update_epsilon():
	global epsilon_counter

	epsilon_counter += 0.0005

def pick_action(state):
	if str(state) not in Q:
		Q[str(state)] = [0, 0]

	if Q[str(state)][0] == Q[str(state)][1] or random.random() < get_epsilon():
		return random.randint(0, 1)
	else:
		if Q[str(state)][0] > Q[str(state)][1]:
			return 0
		else:
			return 1

def read_action(state):
	action = -1

	print("State: " + str(state) + " (" + str(len(state)) + "/" + str(episode_length) + ")")

	while (action != 0 and action != 1):
		try:
			action = int(raw_input("Choose Cooperate/Defect (0/1): "))
		except ValueError:
			print("Please input a number.")
	
	return action

def reward_action(state, action, reward):
	Q[str(state)][action] += reward

# Training mode
while epsilon_counter < 5:
	state1 = [] # State visible to player 1
	state2 = [] # State visible to player 2

	for i in range(episode_length):
		action = None

		action1 = pick_action(state1) # Select action for player 1
		action2 = pick_action(state2) # Select action for player 2

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

		reward_action(state1[:i], action1, reward1) # Assign reward to action of player 1
		reward_action(state2[:i], action2, reward2) # Assign reward to action of player 2

	# Assign reward for winning player
	if total_reward1 > total_reward2:
		reward_chunk = int(total_reward1 / episode_length * gamma)

		for i in range(episode_length):
			action1 = state2[i]

			reward_action(state1[:i], action1, reward_chunk)
	elif total_reward2 > total_reward1:
		reward_chunk = int(total_reward2 / episode_length * gamma)

		for i in range(episode_length):
			action2 = state1[i]

			reward_action(state2[:i], action2, reward_chunk)

	cooperation_metric = 0
	cooperation_max_value = 0
	cooperation_max_state = "[]"

	for key, value in Q.iteritems():
		if value[0] > value[1]:
			cooperation_metric += 1

			if value[0] - value[1] > cooperation_max_value:
				cooperation_max_value = value[0] - value[1]
				cooperation_max_state = key

	print("Cooperation occurs in " + str("%.3f" % (float(cooperation_metric) / len(Q) * 100)) + "% of " + str(len(Q)) + " states, highest in " + str(cooperation_max_state) + ", scoring " + str(total_reward1) + " with epsilon " + str("%.5f" % get_epsilon()))

	update_epsilon()

# Testing mode
while epsilon_counter < 10:
	state1 = [] # State visible to player 1
	state2 = [] # State visible to player 2

	for i in range(episode_length):
		action = None

		action1 = read_action(state1) # Allow player 1 to pick action
		action2 = pick_action(state2) # Select action for player 2

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

	# Print the winning player and score
	print("Score: " + str(total_reward1) + " to " + str(total_reward2))
	if total_reward1 > total_reward2:
		print("You win!")
	elif total_reward2 > total_reward1:
		print("You lose!")
	else:
		print("Tie!")