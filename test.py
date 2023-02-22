
from classes.utils import *

# GPU settings
gpus = tf.config.experimental.list_physical_devices('GPU')
for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

scenario = "No_Car" # REAL, No_Bat, No_Car
type_s = "INC" # INC, DEC
model_type = "Dense_2" # Network (Dense)
curve_pred = [[35.0, 42.5, 47.5,  38.5, 33.0, 41.0, 46.0, 37.0]]
optimizer = tf.keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)
loss_function = tf.keras.losses.Huber()
seed = 42
gamma = 0.99
epsilon = 1

env, action_values, policy_network, _ , num_actions = define_env(scenario, type_s, model_type, curve_pred) 
done = False
step = 0
env.reset()
state = np.array(env.reset())
while not done:
    state_tensor = tf.convert_to_tensor(state)
    state_tensor = tf.expand_dims(state_tensor, 0)
    action_probs = policy_network(state_tensor, training=False)
    action = tf.argmax(action_probs[0]).numpy()
    state, reward, done, info = env.step(action)
    print("STEP {}, ACTION {} {}, ACT_CONS {}, CONS {}".format(step,action,action_values[action],abs(env.get_action_cons()), env.get_cons()))
    step+=1
