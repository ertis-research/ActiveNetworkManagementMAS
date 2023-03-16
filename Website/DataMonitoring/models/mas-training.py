import base64

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import reverb

import tensorflow as tf
from pytz import timezone

from tf_agents.agents.dqn import dqn_agent
from tf_agents.drivers import py_driver, dynamic_step_driver
from tf_agents.environments import suite_gym
from tf_agents.environments import tf_py_environment
from tf_agents.environments import tf_environment
from tf_agents.environments import utils
from tf_agents.agents.dqn.dqn_agent import DqnAgent, DdqnAgent
from datetime import datetime
from tf_agents.environments import py_environment
from tf_agents.networks.q_network import QNetwork
from tf_agents.networks import q_network
from tf_agents.eval import metric_utils
from tf_agents.metrics import tf_metrics
from tf_agents.networks import sequential
from tf_agents.policies import policy_saver
from tf_agents.policies import py_tf_eager_policy
from tf_agents.policies import random_tf_policy
from tf_agents.replay_buffers import reverb_replay_buffer, tf_uniform_replay_buffer
from tf_agents.replay_buffers import reverb_utils
from tf_agents.trajectories import trajectory
from tf_agents.trajectories import time_step as ts
from tf_agents.environments import wrappers

from tf_agents.specs import tensor_spec
from tf_agents.utils import common

from tf_agents.specs import array_spec

from tf_agents.utils import common
from pickle import load
from datetime import datetime, timedelta
from pymongo import MongoClient
import time
import pandas as pd
import json
import os


num_iterations = int(os.environ.get("ITER"))
soc = float(os.environ.get("SOC"))
scenario_type = float(os.environ.get("TYPE"))
temp_dir = os.environ.get("NAME")
flexibility = float(os.environ.get("FLEX"))
pred = os.environ.get("PRED")
host = os.environ.get("HOST")
user = os.environ.get("USER")
passw =os.environ.get("PASSW")

gpus = tf.config.experimental.list_physical_devices('GPU')

for gpu in gpus:
    tf.config.experimental.set_memory_growth(gpu, True)

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


client = MongoClient(host=host, username=user, password=passw, connectTimeoutMS=2500)

class AmpereStorageBattery():
    def __init__(self, capacity = None, soc = None):
        """
            Initilization method
            : param
                capacity - Capacity of the Storage Battery
        """
        self.capacity = capacity if capacity else 120.0
        self.state = soc
        self.soc = self.capacity * self.state if self.state else self.capacity * 0.5 
        self.consumption = 0
        
    def charge20(self):
        """
            Simulation of 20Kwh charge (20kwh = 5kw per 15 minutes)
            : return consumption
        """

        self.consumption = self.soc -  min(self.capacity, self.soc + 5)  
        self.soc -=  self.consumption
        return self.consumption
    
    def charge40(self):
        """
            Simulation of 40Kwh charge (40kwh = 10kw per 15 minutes)
            : return consumption
        """
        
        self.consumption = self.soc -  min(self.capacity, self.soc + 10)    
        self.soc -=  self.consumption
        return self.consumption
    
    def charge60(self):
        """
            Simulation of 60Kwh charge (60kwh = 15kw per 15 minutes)
            
        """
        
        self.consumption = self.soc - min(self.capacity, self.soc + 15) 
        self.soc -=  self.consumption
        return self.consumption
    
    def discharge20(self):
        """
            Simulation of 20Kwh discharge (20kwh = 5kw per 15 minutes)
        """
        self.consumption = min(5, self.soc - 5)
        self.soc -= abs(self.consumption)
        return -abs(self.consumption)
    
    def discharge40(self):
        """
            Simulation of 40Kwh discharge (40kwh = 10kw per 15 minutes)
            
        """
        self.consumption = min(10, self.soc - 10)
        self.soc -= self.consumption
        return self.consumption
        
    
    def discharge60(self):
        """
            Simulation of 60Kwh discharge (60kwh = 15kw per 15 minutes)
            : return consumption
        """
        self.consumption = min(15, self.soc - 15)
        self.soc -= self.consumption
        return self.consumption
    
    def stop(self):
        """
            Stop processing
        """
        self.consumption = 0
        
    def render(self, mode="human"):
        """
            Print the ev charging station status
        """
        
        print ("Ampere SB -> Capacity: {}, State of Charge: {}, Consumption: {}".format(self.capacity, self.soc, self.consumption))
    
    def reset(self):
        self.soc = self.capacity * self.state if self.state else self.capacity * 0.5 
        self.consumption = 0



class ChargingStation():
    def __init__(self, power = 30.0):
        """
            Initilization method
            : param
                power - Power of the Charge Station
        """
        self.s1 = 0 # 0 - Available, 1 - Busy, 2 - Charging, 3 - Discharging
        self.s2 = 0 # 0 - Available, 1 - Busy, 2 - Charging, 3 - Discharging
        self.power = power # Default 30 Kw
        
    def carArrival(self, station):
        """
            Simulation of the arrival of a car at a charging station
            : param
                station - Station where the car is plugged 
        """
        if station == 1 and self.s1 == 0:
            self.s1 = 1
        elif station == 2 and self.s2 == 0:
            self.s2 = 1
        else:
            print("Station is busy")

    def carDeparture(self, station):
        """
            Simulation of the departure of a car at a charging station
            : param
                station - Station where the car is plugged 
        """
        if station == 1 and self.s1 != 0:
            self.s1 = 0
        elif station == 2 and self.s2 != 0:
            self.s2 = 0
        else:
            print("Station was Available yet")
            
    def charge(self, station):
        """
            The car starts charging from the station
            : param
                station - Station where the car is charging 
        """
        if station == 1 and self.s1 != 0:
            self.s1 = 2
        elif station == 2 and self.s2 != 0:
            self.s2 = 2
        return self.consumption()
            
    def discharge(self, station):
        """
            The car starts discharging from the station
            : param
                station - Station where the car is discharging 
        """
        if station == 1 and self.s1 != 0:
            self.s1 = 3
        elif station == 2 and self.s2 != 0:
            self.s2 = 3
        return self.consumption()
    
    def consumption(self):
        """
            Calculates the consumption of the charging station based on its occupancy and condition.
            : param
                station - Station where the car is charging 
            : return the consumption of the charging station
        """
        if self.s1 == 2 and self.s2 < 3:
            return -self.power
        elif self.s2 == 2 and self.s1 < 3:
            return -self.power
        if self.s1 == 3 and self.s2 == 3:
            return self.power
        if self.s1 == 3 and self.s2 != 2 or self.s1 != 2 and self.s2 == 3:
            return self.power
        else: 
            return 0.0
        
    def stop(self):
        """
            Stop charging.
        """
        
        self.s1 = 1
        self.s2 = 1
        
        
    def render(self, mode ="human"):
        """
            Print the ev charging station status
        """
        print ("EV Station -> Station 1: {}, Station 2 {}, Consumption: {}".format(self.s1, self.s2, self.consumption()))
    
    def reset(self):
        self.s1 = 0 
        self.s2 = 0 

class Airconditioning():
    def __init__(self):
        self.state = 0
        
    def turnOff(self):
        self.state = 0
        return self.consumption()
         
    def smallChange(self):
        self.state = 1
        return self.consumption()
    
    def bigChange(self):
        self.state = 2
        return self.consumption()
        
    def render(self, mode="human"):
        print("Air conditioning -> State {}, Consumption {}".format(self.state, self.consumption()))
    
    def consumption(self):
        if self.state == 0:
            return -20.0
        else:
            # Base consumption + consumption added per grade
            # 1,13 - It is the coefficient of passage from frigories to watts.
            return -round(20.0 + self.state*15.0, 2)# Divided by 4, since it is a quarter-hourly time slot


class RealScenario(py_environment.PyEnvironment):
    
    def __init__(self, objective_curve, capacity = None, soc = None, flexibility = 15.0):
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=50, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(2,), dtype=np.int32, minimum=0, name='observation')
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility 
        self.flexibility = flexibility        
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        self.sb = AmpereStorageBattery()
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
    
    def get_cumulative_consumption(self):
        return self.cumulative_consumption

    def get_consumption(self):
        return self.consumption

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec
    def _current_time_step(self):
        """Returns the current `TimeStep`."""
        return self._current_time_step()

    def _reset(self):
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        #Storage battery
        self.sb = AmpereStorageBattery()
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        return ts.restart(np.array([self.objective_curve[self._state],self.sb.soc], dtype=np.int32))

    def _step(self, action):
        self.ac.turnOff()
        self.cs.stop()
        self.sb.stop()
        if self._episode_ended:
            self._reset()
         # Do nothing.
        if action == 0:

            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #EV Charge
        elif action == 3:
            c = self.cs.charge(1) + self.ac.turnOff()
        #EV Discharge
        elif action == 4:
            c = self.cs.discharge(1) + self.ac.turnOff()
        #SB Charge20
        elif action == 5:
            c = self.sb.charge20() + self.ac.turnOff()
        #SB Charge40
        elif action == 6:
            c = self.sb.charge40() + self.ac.turnOff()
        #SB Charge60
        elif action == 7:
            c = self.sb.charge60() + self.ac.turnOff()
        #SB Discharge20
        elif action == 8:
            c = self.sb.discharge20() + self.ac.turnOff()
        #SB Discharge40
        elif action == 9:
            c = self.sb.discharge40() + self.ac.turnOff()
        #SB Discharge60
        elif action == 10:
            c = self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature and EV Charge
        elif action == 11:
            c = self.ac.smallChange() + self.cs.charge(1)
        #Small Change Temperature and EV Discharge
        elif action == 12:
            c = self.ac.smallChange() + self.cs.discharge(1)
        #Small Change Temperature and SB Charge20
        elif action == 13:
            c = self.ac.smallChange() + self.sb.charge20()
        #Small Change Temperature and SB Charge40
        elif action == 14:
            c = self.ac.smallChange() + self.sb.charge40()
        #Small Change Temperature and SB Charge20
        elif action == 15:
            c = self.ac.smallChange() + self.sb.charge60()
        #Small Change Temperature and SB Discharge20
        elif action == 16:
            c = self.ac.smallChange() + self.sb.discharge20()
        #Small Change Temperature and SB Discharge40
        elif action == 17:
            c = self.ac.smallChange() + self.sb.discharge40()
        #Small Change Temperature and SB Discharge60
        elif action == 18:
            c = self.ac.smallChange() + self.sb.discharge60()
        #Big Change Temperature and EV Charge
        elif action == 19:
            c = self.ac.bigChange() + self.cs.charge(1)
        #Big Change Temperature and EV Discharge
        elif action == 20:
            c = self.ac.bigChange() + self.cs.discharge(1)
        #Big Change Temperature and SB Charge20
        elif action == 21:
            c = self.ac.bigChange() + self.sb.charge20()
        #Big Change Temperature and SB Charge40
        elif action == 22:
            c = self.ac.bigChange() + self.sb.charge40()
        #Big Change Temperature and SB Charge60
        elif action == 23:
            c = self.ac.bigChange() + self.sb.charge60()
        #Big Change Temperature and SB Discharge20
        elif action == 24:
            c = self.ac.bigChange() + self.sb.discharge20()
        #Big Change Temperature and SB Discharge40
        elif action == 25:
            c = self.ac.bigChange() + self.sb.discharge40()
        #Big Change Temperature and SB Discharge60
        elif action == 26:
            c = self.ac.bigChange() + self.sb.discharge60()
        #EV Charge and SB Charge20
        elif action == 27:
            c = self.cs.charge(1) + self.sb.charge20() + self.ac.turnOff()
        #EV Charge and SB Charge40
        elif action == 28:
            c = self.cs.charge(1) + self.sb.charge40() + self.ac.turnOff()
        #EV Charge and SB Charge60
        elif action == 29:
            c = self.cs.charge(1) + self.sb.charge60() + self.ac.turnOff()
        #EV Charge and SB Discharge20
        elif action == 30:
            c = self.cs.charge(1) + self.sb.discharge20() + self.ac.turnOff()
        #EV Charge and SB Discharge40
        elif action == 31:
            c = self.cs.charge(1) + self.sb.discharge40() + self.ac.turnOff()
        #EV Charge and SB Discharge60
        elif action == 32:
            c = self.cs.charge(1) + self.sb.discharge60() + self.ac.turnOff()
        #EV Discharge and SB Charge20
        elif action == 33:
            c = self.cs.discharge(1) + self.sb.charge20() + self.ac.turnOff()
        #EV Discharge and SB Charge40
        elif action == 34:
            c = self.cs.discharge(1) + self.sb.charge40() + self.ac.turnOff()
        #EV Discharge and SB Charge60
        elif action == 35:
            c = self.cs.discharge(1) + self.sb.charge60() + self.ac.turnOff()
        #EV Discharge and SB Discharge20
        elif action == 36:
            c = self.cs.discharge(1) + self.sb.discharge20() + self.ac.turnOff()
        #EV Discharge and SB Discharge40
        elif action == 37:
            c = self.cs.discharge(1) + self.sb.discharge40() + self.ac.turnOff()
        #EV Discharge and SB Discharge60
        elif action == 38:
            c = self.cs.discharge(1) + self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature, EV Charge and SB Charge20
        elif action == 39:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge20()
        #Small Change Temperature, EV Charge and SB Charge40
        elif action == 40:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge40()
        #Small Change Temperature, EV Charge and SB Charge60
        elif action == 41:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge60()
        #Small Change Temperature, EV Charge and SB Discharge20
        elif action == 42:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge20()
        #Small Change Temperature, EV Charge and SB Discharge40
        elif action == 43:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge40()
        #Small Change Temperature, EV Charge and SB Discharge60
        elif action == 44:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge60()
        #Big Change Temperature, EV Charge and SB Charge20
        elif action == 45:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge20()
        #Big Change Temperature, EV Charge and SB Charge40
        elif action == 46:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge40()
        #Big Change Temperature, EV Charge and SB Charge60
        elif action == 47:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge60()
        #Big Change Temperature, EV Charge and SB Discharge20
        elif action == 48:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge20()
        #Big Change Temperature, EV Charge and SB Discharge40
        elif action == 49:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge40()
        #Big Change Temperature, EV Charge and SB Discharge60
        elif action == 50:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge60()
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
            

        if abs(val) > self.objective_curve[self._state] * (self.flexibility)/100 or self._state == len(self.objective_curve)-1 :
            self._episode_ended = True 
            reward = 5*len(self.objective_curve) if self._state == len(self.objective_curve)-1 else -35*(len(self.objective_curve)-self._state + 1)
            return ts.termination(np.array([self.objective_curve[self._state], self.sb.soc], dtype=np.int32), reward+self.cumulative_consumption+ 35 * (self._state + 1))
        else:
            reward = self.cumulative_consumption + 10 * (self._state + 1)

        self._state += 1
        return ts.transition(np.array([self.objective_curve[self._state], self.sb.soc], dtype=np.int32), reward=reward)
    
    
    def render(self, mode = 'human'):
        print("\n")
        #print("Current_step {}, Objective curve {},  real consumption {}, ended: {}".format(self._state, self.objective_curve[self._state], self.consumption, self._episode_ended))
        self.sb.render()
        self.ac.render()
        self.cs.render()


class Scenario1(py_environment.PyEnvironment):
    
    def __init__(self, objective_curve, flexibility = 15.0):
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=8, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(1,), dtype=np.int32, minimum=0, name='observation')
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility 
        self.flexibility = flexibility        
        #Air conditioning of the room
        self.ac = Airconditioning()
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
    
    def get_cumulative_consumption(self):
        return self.cumulative_consumption

    def get_consumption(self):
        return self.consumption

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec
    def _current_time_step(self):
        """Returns the current `TimeStep`."""
        return self._current_time_step()

    def _reset(self):
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        return ts.restart(np.array([self.objective_curve[self._state]], dtype=np.int32))

    def _step(self, action):
        self.ac.turnOff()
        self.cs.stop()
        if self._episode_ended:
            self._reset()
         # Do nothing.
        if action == 0:

            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #EV Charge
        elif action == 3:
            c = self.cs.charge(1) + self.ac.turnOff()
        #EV Discharge
        elif action == 4:
            c = self.cs.discharge(1) + self.ac.turnOff()
        #Small Change Temperature and EV Charge
        elif action == 5:
            c = self.ac.smallChange() + self.cs.charge(1)
        #Small Change Temperature and EV Discharge
        elif action == 6:
            c = self.ac.smallChange() + self.cs.discharge(1)
        #Big Change Temperature and EV Charge
        elif action == 7:
            c = self.ac.bigChange() + self.cs.charge(1)
        #Big Change Temperature and EV Discharge
        elif action == 8:
            c = self.ac.bigChange() + self.cs.discharge(1)
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
            

        if abs(val) > self.objective_curve[self._state] * (self.flexibility)/100 or self._state == len(self.objective_curve)-1 :
            self._episode_ended = True 
            reward = 5*len(self.objective_curve) if self._state == len(self.objective_curve)-1 else -35*(len(self.objective_curve)-self._state + 1)
            return ts.termination(np.array([self.objective_curve[self._state]], dtype=np.int32), reward+self.cumulative_consumption+ 35 * (self._state + 1))
        else:
            reward = self.cumulative_consumption + 10 * (self._state + 1)

        self._state += 1
        return ts.transition(np.array([self.objective_curve[self._state]], dtype=np.int32), reward=reward)
    
    
    def render(self, mode = 'human'):
        print("\n")
        #print("Current_step {}, Objective curve {},  real consumption {}, ended: {}".format(self._state, self.objective_curve[self._state], self.consumption, self._episode_ended))
        self.ac.render()
        self.cs.render()



class Scenario2(py_environment.PyEnvironment):
    
    def __init__(self, objective_curve, capacity = None, soc = None, flexibility = 15.0):
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=20, name='action')
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(2,), dtype=np.int32, minimum=0, name='observation')
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility 
        self.flexibility = flexibility        
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        self.sb = AmpereStorageBattery()
        self.consumption = 0
        self.cumulative_consumption = 0
    
    def get_cumulative_consumption(self):
        return self.cumulative_consumption

    def get_consumption(self):
        return self.consumption

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec
    def _current_time_step(self):
        """Returns the current `TimeStep`."""
        return self._current_time_step()

    def _reset(self):
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        #Storage battery
        self.sb = AmpereStorageBattery()
        self.consumption = 0
        self.cumulative_consumption = 0
        return ts.restart(np.array([self.objective_curve[self._state],self.sb.soc], dtype=np.int32))

    def _step(self, action):
        self.ac.turnOff()
        self.sb.stop()
        if self._episode_ended:
            self._reset()
         # Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #SB Charge20
        elif action == 3:
            c = self.sb.charge20() + self.ac.turnOff()
        #SB Charge40
        elif action == 4:
            c = self.sb.charge40() + self.ac.turnOff()
        #SB Charge60
        elif action == 5:
            c = self.sb.charge60() + self.ac.turnOff()
        #SB Discharge20
        elif action == 6:
            c = self.sb.discharge20() + self.ac.turnOff()
        #SB Discharge40
        elif action == 7:
            c = self.sb.discharge40() + self.ac.turnOff()
        #SB Discharge60
        elif action == 8:
            c = self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature and SB Charge20
        elif action == 9:
            c = self.ac.smallChange() + self.sb.charge20()
        #Small Change Temperature and SB Charge40
        elif action == 10:
            c = self.ac.smallChange() + self.sb.charge40()
        #Small Change Temperature and SB Charge20
        elif action == 11:
            c = self.ac.smallChange() + self.sb.charge60()
        #Small Change Temperature and SB Discharge20
        elif action == 12:
            c = self.ac.smallChange() + self.sb.discharge20()
        #Small Change Temperature and SB Discharge40
        elif action == 13:
            c = self.ac.smallChange() + self.sb.discharge40()
        #Small Change Temperature and SB Discharge60
        elif action == 14:
            c = self.ac.smallChange() + self.sb.discharge60()
        #Big Change Temperature and SB Charge20
        elif action == 15:
            c = self.ac.bigChange() + self.sb.charge20()
        #Big Change Temperature and SB Charge40
        elif action == 16:
            c = self.ac.bigChange() + self.sb.charge40()
        #Big Change Temperature and SB Charge60
        elif action == 17:
            c = self.ac.bigChange() + self.sb.charge60()
        #Big Change Temperature and SB Discharge20
        elif action == 18:
            c = self.ac.bigChange() + self.sb.discharge20()
        #Big Change Temperature and SB Discharge40
        elif action == 19:
            c = self.ac.bigChange() + self.sb.discharge40()
        #Big Change Temperature and SB Discharge60
        elif action == 20:
            c = self.ac.bigChange() + self.sb.discharge60()
            
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
            

        if abs(val) > self.objective_curve[self._state] * (self.flexibility)/100 or self._state == len(self.objective_curve)-1 :
            self._episode_ended = True 
            reward = 5*len(self.objective_curve) if self._state == len(self.objective_curve)-1 else -35*(len(self.objective_curve)-self._state + 1)
            return ts.termination(np.array([self.objective_curve[self._state], self.sb.soc], dtype=np.int32), reward+self.cumulative_consumption+ 35 * (self._state + 1))
        else:
            reward = self.cumulative_consumption + 10 * (self._state + 1)

        self._state += 1
        return ts.transition(np.array([self.objective_curve[self._state], self.sb.soc], dtype=np.int32), reward=reward)
    
    
    def render(self, mode = 'human'):
        print("\n")
        #print("Current_step {}, Objective curve {},  real consumption {}, ended: {}".format(self._state, self.objective_curve[self._state], self.consumption, self._episode_ended))
        self.sb.render()
        self.ac.render()


def compute_avg_return(environment, policy, num_episodes=10):
    
    total_return = 0.0
    for _ in range(num_episodes):

        time_step = environment.reset()
        episode_return = 0.0

        while not time_step.is_last():
            action_step = policy.action(time_step)
            time_step = environment.step(action_step.action)
            episode_return += time_step.reward
            total_return += episode_return

    avg_return = total_return / num_episodes
    return avg_return.numpy()[0]

initial_collect_steps = 10000000  # @param
collect_steps_per_iteration = 1  # @param
replay_buffer_capacity = 100 # @param
pred = json.loads(pred)
print("PRED: ", pred, type(pred))
fc_layer_params = (256,)

batch_size = 1024  # @param
learning_rate = 1e-2  # @param
log_interval = 1000  # @param

num_eval_episodes = 100 # @param
eval_interval = 100  # @param
if scenario_type == 0:
    env = RealScenario(pred, flexibility)
    train_py_env = wrappers.TimeLimit(RealScenario(pred, flexibility), duration=1000)
    eval_py_env = wrappers.TimeLimit(RealScenario(pred, flexibility), duration=1000)
    train_env = tf_py_environment.TFPyEnvironment(train_py_env)
    eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)
elif scenario_type == 1:
    env = Scenario1(pred, flexibility)
    train_py_env = wrappers.TimeLimit(Scenario1(pred, flexibility), duration=1000)
    eval_py_env = wrappers.TimeLimit(Scenario1(pred, flexibility), duration=1000)
    train_env = tf_py_environment.TFPyEnvironment(train_py_env)
    eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)
elif scenario_type == 2:
    env = Scenario2(pred, flexibility)
    train_py_env = wrappers.TimeLimit(Scenario2(pred, flexibility), duration=1000)
    eval_py_env = wrappers.TimeLimit(Scenario2(pred, flexibility), duration=1000)
    train_env = tf_py_environment.TFPyEnvironment(train_py_env)
    eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)



q_net = q_network.QNetwork(
train_env.observation_spec(),
train_env.action_spec(),
fc_layer_params=fc_layer_params)

optimizer = tf.compat.v1.train.AdamOptimizer(learning_rate=learning_rate)
global_step = tf.compat.v1.train.get_or_create_global_step()
train_step_counter = tf.compat.v2.Variable(0)

tf_agent = DqnAgent(
        train_env.time_step_spec(),
        train_env.action_spec(),
        q_network=q_net,
        optimizer=optimizer,
        td_errors_loss_fn = common.element_wise_squared_loss,
        train_step_counter=train_step_counter)



tf_agent.initialize()
eval_policy = tf_agent.policy
collect_policy = tf_agent.collect_policy

replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
        data_spec=tf_agent.collect_data_spec,
        batch_size=train_env.batch_size,
        max_length=replay_buffer_capacity)

replay_observer = [replay_buffer.add_batch]

train_metrics = [
            tf_metrics.EnvironmentSteps(),
            tf_metrics.AverageReturnMetric(),

]
dataset = replay_buffer.as_dataset(
        num_parallel_calls=3,
        sample_batch_size=batch_size, single_deterministic_pass=False,
num_steps=2).prefetch(3)
driver = dynamic_step_driver.DynamicStepDriver(
            train_env,
            collect_policy,
            observers=replay_observer + train_metrics,
    num_steps=1)


tf_policy_saver = policy_saver.PolicySaver(tf_agent.policy)

print(compute_avg_return(eval_env, tf_agent.policy, num_eval_episodes))



tf_agent.train = common.function(tf_agent.train)
tf_agent.train_step_counter.assign(0)

final_time_step, policy_state = driver.run()
iterator = iter(dataset)
for i in range(1000):
    final_time_step, _ = driver.run(final_time_step, policy_state)

for i in range(num_iterations):
    final_time_step, _ = driver.run(final_time_step, policy_state)
    #for _ in range(1):
    #    collect_step(train_env, tf_agent.collect_policy)

    experience, _ = next(iterator)
    train_loss = tf_agent.train(experience=experience)
    step = tf_agent.train_step_counter.numpy()
    if step % eval_interval == 0:
        avg_return = compute_avg_return(eval_env, tf_agent.policy, num_eval_episodes)
        print("STEP: {} AVG: {}".format(step, avg_return))

data = {"model_name" : temp_dir, "scenario_type" : scenario_type, "flexibility": flexibility, "state_of_charge" : soc, "steps" : num_iterations, "results" : float(avg_return) }
db = client.Ebalance
col = db["models"]
col.insert_one(data)

tf_policy_saver.save(temp_dir)
