from classes.utils import *

# GPU settings
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

#Constant vars

K = 4
EPS_DECAY = 0.0000009
EPS_MIN = 0.1
BATCH_SIZE = 32
MAX_STEPS = 10000
STEP_UPDATE_MODEL = 5000

scenario = "No_Car" # REAL, No_Bat, No_Car
type_s = "INC" # INC, DEC
model_type = "Dense" # Network (Dense)
curve_pred = [[35.0, 42.5, 47.5,  38.5, 33.0, 41.0, 46.0, 37.0]]
optimizer = tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)
loss_function = tf.keras.losses.Huber()
seed = 42
gamma = 0.99
epsilon = 1
memory = Memory(10000) # Memory size

env, _, policy_network, target_network, num_actions = define_env(scenario, type_s, model_type, curve_pred) 

train(epsilon, MAX_STEPS, num_actions, policy_network, EPS_DECAY, EPS_MIN, env, memory, BATCH_SIZE, STEP_UPDATE_MODEL, target_network, K, scenario, type_s, model_type, gamma, loss_function, optimizer)   