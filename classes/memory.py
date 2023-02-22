from collections import deque
import numpy as np
class Memory(object):
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def save(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        indices     = np.random.choice(len(self.memory), batch_size, replace=False)
        
        states      = []
        actions     = []
        next_states = []
        rewards     = []
        dones       = []


        for idx in indices: 
            states.append(self.memory[idx][0])
            actions.append(self.memory[idx][1])
            next_states.append(self.memory[idx][3])
            rewards.append(self.memory[idx][2])
            dones.append(self.memory[idx][4])
        
        return np.array(states), actions, rewards, np.array(next_states), dones

    def __len__(self):
        return len(self.memory)