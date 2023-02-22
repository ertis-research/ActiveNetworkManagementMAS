import numpy as np
import random
import tensorflow as tf
import classes.UMADemo as demo
from classes.memory import Memory

# Aditional functions


def train(epsilon, MAX_STEPS, num_actions, policy_network, EPS_DECAY, EPS_MIN, env, memory, BATCH_SIZE, STEP_UPDATE_MODEL, target_network, K, scenario, type_s, model_type, gamma, loss_function, optimizer):
    step = 0
    while True:
        initial_state = np.array(env.reset())
        for i in range(1, MAX_STEPS):
            step+=1
            if step < 50000 or np.random.rand(1)[0] < epsilon:
                action = random.randint(0, num_actions-1)
            else:
                tf_tensor = tf.convert_to_tensor(initial_state)
                tf_tensor = tf.expand_dims(initial_state, 0)

                output = policy_network(tf_tensor, training=False)

                action = tf.argmax(output[0]).numpy()
            epsilon-=EPS_DECAY

            epsilon = max(epsilon, EPS_MIN)
            next_step, reward, done, _ = env.step(action)
            next_step = np.array(next_step)

            memory.save(initial_state, action, reward, next_step, float(done))
            initial_state = next_step

            if step % K == 0 and len(memory) >= BATCH_SIZE:
                optimize_model(memory, BATCH_SIZE, target_network, policy_network, gamma, loss_function, optimizer, num_actions)
            if step % STEP_UPDATE_MODEL == 0:
                target_network.set_weights(policy_network.get_weights())
                target_network.save("models/{}/{}/{}/targetNetwork_fineT.h5".format(scenario,type_s,model_type))
                policy_network.save("models/{}/{}/{}/policyNetwork_fineT.h5".format(scenario,type_s,model_type))
            if done: break


def define_env(scenario, type_s, model_type, curve_pred):
    policy_network = tf.keras.models.load_model("models/{}/{}/{}/policyNetwork.h5".format(scenario,type_s,model_type))
    target_network = tf.keras.models.load_model("models/{}/{}/{}/targetNetwork.h5".format(scenario,type_s,model_type))
    if scenario == "REAL":
        num_actions = 51
        action_values = ["Do nothing", "Small change temperature", "Big Change temperature", "EV Charge", "EV Discharge", "SB Charge20", "SB Charge40" ,"SB Charge60", "SB Discharge20" ,"SB Discharge40", "SB Discharge60", "Small Change Temperature and EV Charge", "Small Change Temperature and EV Discharge", "Small Change Temperature and SB Charge20", "Small Change Temperature and SB Charge40", "Small Change Temperature and SB Charge60", "Small Change Temperature and SB Discharge20", "Small Change Temperature and SB Discharge40", "Small Change Temperature and SB Discharge60", "Big Change Temperature and EV Charge", "Big Change Temperature and EV Discharge", "Big Change Temperature and SB Charge20", "Big Change Temperature and SB Charge40", "#Big Change Temperature and SB Charge60", "Big Change Temperature and SB Discharge20", "Big Change Temperature and SB Discharge40", "Big Change Temperature and SB Discharge60", "EV Charge and SB Charge20", "EV Charge and SB Charge40", "EV Charge and SB Charge60", "EV Charge and SB Discharge20", "EV Charge and SB Discharge40", "EV Charge and SB Discharge60", "EV Discharge and SB Charge20", "EV Discharge and SB Charge40", "EV Discharge and SB Charge60", "EV Discharge and SB Discharge20", "EV Discharge and SB Discharge40", "EV Discharge and SB Discharge60", "Small Change Temperature, EV Charge and SB Charge20", "Small Change Temperature, EV Charge and SB Charge40", "Small Change Temperature, EV Charge and SB Charge60", "EV Charge and SB Discharge20", "Small Change Temperature, EV Charge and SB Discharge40", "Small Change Temperature, EV Charge and SB Discharge60", "Big Change Temperature, EV Charge and SB Charge20", "Big Change Temperature, EV Charge and SB Charge40", "Big Change Temperature, EV Charge and SB Charge60", "Big Change Temperature, EV Charge and SB Discharge20", "Big Change Temperature, EV Charge and SB Discharge40",  "Big Change Temperature, EV Charge and SB Discharge60"]
        if type_s == "INC":
            env = demo.UMADemoINC(curve_pred[0][0:20])
        elif type_s == "DEC":
            env = demo.UMADemoDEC(curve_pred[0][0:20])
    elif scenario == "No_Car":
        num_actions = 21
        action_values = ["Do nothing.","Small change temperature","Big Change temperature", "SB Charge20", "SB Charge40", "SB Charge60", "SB Discharge20", "SB Discharge40", "SB Discharge60", "Small Change Temperature and SB Charge20", "Small Change Temperature and SB Charge40", "Small Change Temperature and SB Charge20" , "Small Change Temperature and SB Discharge20" , "Small Change Temperature and SB Discharge40", "Small Change Temperature and SB Discharge60", "Big Change Temperature and SB Charge20", "Big Change Temperature and SB Charge40", "Big Change Temperature and SB Charge60", "Big Change Temperature and SB Discharge20", "Big Change Temperature and SB Discharge40", "Big Change Temperature and SB Discharge60"]
        if type_s == "INC":
            env = demo.UMADemoINC_No_Car(curve_pred[0][0:20])
        elif type_s == "DEC":
            env = demo.UMADemoDEC_No_Car(curve_pred[0][0:20])
    elif scenario == "No_Bat":
        num_actions = 9
        action_values = ["Do nothing.", "Small change temperature", "Big Change temperature", "EV Charge", "EV Discharge", "Small Change Temperature and EV Charge", "Small Change Temperature and EV Discharge", "Big Change Temperature and EV Charge", "Big Change Temperature and EV Discharge"]
        if type_s == "INC":
            env = demo.UMADemoINC_No_Batteries(curve_pred[0][0:20])
        elif type_s == "DEC":
            env = demo.UMADemoDEC_No_Batteries(curve_pred[0][0:20])
    return env, action_values, policy_network, target_network, num_actions

def optimize_model(memory, BATCH_SIZE, target_network, policy_network, gamma, loss_function, optimizer, num_actions):
    states, actions, rewards, next_steps, dones = memory.sample(BATCH_SIZE)
    dones_tensor = tf.convert_to_tensor(dones)

    qpvalues = target_network.predict(next_steps, verbose=0)
    y_target = rewards + gamma*tf.reduce_max(qpvalues, axis=1)
    y_target = y_target * (1-dones_tensor) - dones_tensor
    
    mask = tf.one_hot(actions, num_actions)
    
    with tf.GradientTape() as cinta:
        Qvalues = policy_network(states)
        
        y_pred = tf.reduce_sum(tf.multiply(Qvalues, mask), axis = 1)
        loss = loss_function(y_target, y_pred)

    gradients = cinta.gradient(loss, policy_network.trainable_variables)
    optimizer.apply_gradients(zip(gradients, policy_network.trainable_variables))



