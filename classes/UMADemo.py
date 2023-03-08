from classes.airConditioning import Airconditioning
from classes.storageBattery import StorageBattery
from classes.chargingStation import ChargingStation
import math
import gym

class UMADemoINC(gym.Env):
    """UMA DEMOSITE SCENARIO INCREMENTAL CONSUMPTION"""
    metadata = {'render.modes': ['human']}

    def __init__(self, objective_curve, capacity = 120.0, soc = 0.5):
        super(UMADemoINC, self).__init__()
        # Define action and observation space
        # They must be gym.gym.spaces objects
        # Example when using discrete actions:
        self.action_space = gym.spaces.Discrete(65)
        # Example for using image as input:
        self.obs_space = gym.spaces.Box(low=0, high=100, shape=(1,))
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility    
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        self.soc = soc
        self.sb = StorageBattery(soc=self.soc)
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        self.obs = math.ceil(self.objective_curve[self._state+1])
        
    def get_sb_soc(self):
        return self.sb.get_soc()
    
    def get_cons(self):
            return self.objective_curve[self._state-1]
        
    def get_action_cons(self):
        return self.consumption
        
    def step(self, action):
        # Execute one time step within the environment
        self.ac.turnOff()
        self.cs.stop()
        self.sb.stop()
        if self._episode_ended:
            self.reset()
        #Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #Huge Change temperature 
        elif action == 3:
            c = self.ac.hugeChange()
        #EV Charge
        elif action == 4:
            c = self.cs.charge(1) + self.ac.turnOff()
        #EV Discharge
        elif action == 5:
            c = self.cs.discharge(1) + self.ac.turnOff()
        #SB Charge20
        elif action == 6:
            c = self.sb.charge20() + self.ac.turnOff()
        #SB Charge40
        elif action == 7:
            c = self.sb.charge40() + self.ac.turnOff()
        #SB Charge60
        elif action == 8:
            c = self.sb.charge60() + self.ac.turnOff()
        #SB Discharge20
        elif action == 9:
            c = self.sb.discharge20() + self.ac.turnOff()
        #SB Discharge40
        elif action == 10:
            c = self.sb.discharge40() + self.ac.turnOff()
        #SB Discharge60
        elif action == 11:
            c = self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature and EV Charge
        elif action == 12:
            c = self.ac.smallChange() + self.cs.charge(1)
        #Small Change Temperature and EV Discharge
        elif action == 13:
            c = self.ac.smallChange() + self.cs.discharge(1)
        #Small Change Temperature and SB Charge20
        elif action == 14:
            c = self.ac.smallChange() + self.sb.charge20()
        #Small Change Temperature and SB Charge40
        elif action == 15:
            c = self.ac.smallChange() + self.sb.charge40()
        #Small Change Temperature and SB Charge20
        elif action == 16:
            c = self.ac.smallChange() + self.sb.charge60()
        #Small Change Temperature and SB Discharge20
        elif action == 17:
            c = self.ac.smallChange() + self.sb.discharge20()
        #Small Change Temperature and SB Discharge40
        elif action == 18:
            c = self.ac.smallChange() + self.sb.discharge40()
        #Small Change Temperature and SB Discharge60
        elif action == 19:
            c = self.ac.smallChange() + self.sb.discharge60()
        #Big Change Temperature and EV Charge
        elif action == 20:
            c = self.ac.bigChange() + self.cs.charge(1)
        #Big Change Temperature and EV Discharge
        elif action == 21:
            c = self.ac.bigChange() + self.cs.discharge(1)
        #Big Change Temperature and SB Charge20
        elif action == 22:
            c = self.ac.bigChange() + self.sb.charge20()
        #Big Change Temperature and SB Charge40
        elif action == 23:
            c = self.ac.bigChange() + self.sb.charge40()
        #Big Change Temperature and SB Charge60
        elif action == 24:
            c = self.ac.bigChange() + self.sb.charge60()
        #Big Change Temperature and SB Discharge20
        elif action == 25:
            c = self.ac.bigChange() + self.sb.discharge20()
        #Big Change Temperature and SB Discharge40
        elif action == 26:
            c = self.ac.bigChange() + self.sb.discharge40()
        #Big Change Temperature and SB Discharge60
        elif action == 27:
            c = self.ac.bigChange() + self.sb.discharge60()
        #Huge Change Temperature and EV Charge
        elif action == 28:
            c = self.ac.hugeChange() + self.cs.charge(1)
        #Huge Change Temperature and EV Discharge
        elif action == 29:
            c = self.ac.hugeChange() + self.cs.discharge(1)
        #Huge Change Temperature and SB Charge20
        elif action == 30:
            c = self.ac.hugeChange() + self.sb.charge20()
        #Huge Change Temperature and SB Charge40
        elif action == 31:
            c = self.ac.hugeChange() + self.sb.charge40()
        #Huge Change Temperature and SB Charge60
        elif action == 32:
            c = self.ac.hugeChange() + self.sb.charge60()
        #Huge Change Temperature and SB Discharge20
        elif action == 33:
            c = self.ac.hugeChange() + self.sb.discharge20()
        #Huge Change Temperature and SB Discharge40
        elif action == 34:
            c = self.ac.hugeChange() + self.sb.discharge40()
        #Huge Change Temperature and SB Discharge60
        elif action == 35:
            c = self.ac.hugeChange() + self.sb.discharge60()
        #EV Charge and SB Charge20
        elif action == 36:
            c = self.cs.charge(1) + self.sb.charge20() + self.ac.turnOff()
        #EV Charge and SB Charge40
        elif action == 37:
            c = self.cs.charge(1) + self.sb.charge40() + self.ac.turnOff()
        #EV Charge and SB Charge60
        elif action == 38:
            c = self.cs.charge(1) + self.sb.charge60() + self.ac.turnOff()
        #EV Charge and SB Discharge20
        elif action == 39:
            c = self.cs.charge(1) + self.sb.discharge20() + self.ac.turnOff()
        #EV Charge and SB Discharge40
        elif action == 40:
            c = self.cs.charge(1) + self.sb.discharge40() + self.ac.turnOff()
        #EV Charge and SB Discharge60
        elif action == 41:
            c = self.cs.charge(1) + self.sb.discharge60() + self.ac.turnOff()
        #EV Discharge and SB Charge20
        elif action == 42:
            c = self.cs.discharge(1) + self.sb.charge20() + self.ac.turnOff()
        #EV Discharge and SB Charge40
        elif action == 43:
            c = self.cs.discharge(1) + self.sb.charge40() + self.ac.turnOff()
        #EV Discharge and SB Charge60
        elif action == 44:
            c = self.cs.discharge(1) + self.sb.charge60() + self.ac.turnOff()
        #EV Discharge and SB Discharge20
        elif action == 45:
            c = self.cs.discharge(1) + self.sb.discharge20() + self.ac.turnOff()
        #EV Discharge and SB Discharge40
        elif action == 46:
            c = self.cs.discharge(1) + self.sb.discharge40() + self.ac.turnOff()
        #EV Discharge and SB Discharge60
        elif action == 47:
            c = self.cs.discharge(1) + self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature, EV Charge and SB Charge20
        elif action == 48:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge20()
        #Small Change Temperature, EV Charge and SB Charge40
        elif action == 49:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge40()
        #Small Change Temperature, EV Charge and SB Charge60
        elif action == 50:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge60()
        #Small Change Temperature, EV Charge and SB Discharge20
        elif action == 51:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge20()
        #Small Change Temperature, EV Charge and SB Discharge40
        elif action == 52:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge40()
        #Small Change Temperature, EV Charge and SB Discharge60
        elif action == 53:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge60()
        #Big Change Temperature, EV Charge and SB Charge20
        elif action == 54:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge20()
        #Big Change Temperature, EV Charge and SB Charge40
        elif action == 55:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge40()
        #Big Change Temperature, EV Charge and SB Charge60
        elif action == 56:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge60()
        #Big Change Temperature, EV Charge and SB Discharge20
        elif action == 57:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge20()
        #Big Change Temperature, EV Charge and SB Discharge40
        elif action == 58:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge40()
        #Big Change Temperature, EV Charge and SB Discharge60
        elif action == 59:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge60()
        #Huge Change Temperature, EV Charge and SB Charge20
        elif action == 60:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.charge20()
        #Huge Change Temperature, EV Charge and SB Charge40
        elif action == 61:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.charge40()
        #Huge Change Temperature, EV Charge and SB Charge60
        elif action == 62:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.charge60()
        #Huge Change Temperature, EV Charge and SB Discharge20
        elif action == 63:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.discharge20()
        #Huge Change Temperature, EV Charge and SB Discharge40
        elif action == 64:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.discharge40()
        #Huge Change Temperature, EV Charge and SB Discharge60
        elif action == 65:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.discharge60()

        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
        self._state += 1    
        if val>0 or self._state >= len(self.objective_curve)-1 :
            self._episode_ended = True 
            self.reward += 1 if self._state == len(self.objective_curve)-1 else -1
        else:
            if val == 0:
                self.reward += 1
            else:
                self.reward += 1/abs(val)
        
        return math.ceil(self.objective_curve[self._state]), self.reward, self._episode_ended, {}


    def reset(self):
        # Reset the state of the environment to an initial state
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        #Storage battery
        self.sb = StorageBattery(self.soc)
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        
        return math.ceil(self.objective_curve[self._state+1])
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.sb.render()
        self.ac.render()
        self.cs.render()



class UMADemoINC_No_Batteries(gym.Env):
    """UMA DEMOSITE SCENARIO INCREMENTAL CONSUMPTION"""
    metadata = {'render.modes': ['human']}

    def __init__(self, objective_curve):
        super(UMADemoINC_No_Batteries, self).__init__()
        # Define action and observation space
        # They must be gym.gym.spaces objects
        # Example when using discrete actions:
        self.action_space = gym.spaces.Discrete(11)
        # Example for using image as input:
        self.obs_space = gym.spaces.Box(low=0, high=100, shape=(1,))
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility    
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        self.obs = math.ceil(self.objective_curve[self._state+1])
    
    def get_cons(self):
            return self.objective_curve[self._state-1]
    def get_action_cons(self):
        return self.consumption
        
        
    def step(self, action):
        # Execute one time step within the environment
        self.ac.turnOff()
        self.cs.stop()
        if self._episode_ended:
            self.reset()
        #Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #Huge Change temperature 
        elif action == 3:
            c = self.ac.hugeChange()
        #EV Charge
        elif action == 4:
            c = self.cs.charge(1) + self.ac.turnOff()
        #EV Discharge
        elif action == 5:
            c = self.cs.discharge(1) + self.ac.turnOff()
        #Small Change Temperature and EV Charge
        elif action == 6:
            c = self.ac.smallChange() + self.cs.charge(1)
        #Small Change Temperature and EV Discharge
        elif action == 7:
            c = self.ac.smallChange() + self.cs.discharge(1)
        #Big Change Temperature and EV Charge
        elif action == 8:
            c = self.ac.bigChange() + self.cs.charge(1)
        #Big Change Temperature and EV Discharge
        elif action == 9:
            c = self.ac.bigChange() + self.cs.discharge(1)
        #Huge Change Temperature and EV Charge
        elif action == 10:
            c = self.ac.hugeChange() + self.cs.charge(1)
        #Huge Change Temperature and EV Discharge
        elif action == 11:
            c = self.ac.hugeChange() + self.cs.discharge(1)
            
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
        self._state += 1    
        if val>0 or self._state >= len(self.objective_curve)-1 :
            self._episode_ended = True 
            self.reward += 1 if self._state == len(self.objective_curve)-1 else -1
        else:
            if val == 0:
                self.reward += 1
            else:
                self.reward += 1/abs(val)
        
        return math.ceil(self.objective_curve[self._state]), self.reward, self._episode_ended, {}


    def reset(self):
        # Reset the state of the environment to an initial state
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        
        return math.ceil(self.objective_curve[self._state+1])
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.ac.render()
        self.cs.render()



class UMADemoINC_No_Car(gym.Env):
    """UMA DEMOSITE SCENARIO DECREMENTAL CONSUMPTION"""
    metadata = {'render.modes': ['human']}

    def __init__(self, objective_curve, capacity = 120.0, soc = 0.5):
        super(UMADemoINC_No_Car, self).__init__()
        # Define action and observation space
        # They must be gym.gym.spaces objects
        # Example when using discrete actions:
        self.action_space = gym.spaces.Discrete(27)
        # Example for using image as input:
        self.obs_space = gym.spaces.Box(low=0, high=100, shape=(1,))
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility    
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        self.soc = soc
        self.sb = StorageBattery(soc=soc)
        # EV Charging Station
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        self.obs = math.ceil(self.objective_curve[self._state+1])
        
    def get_sb_soc(self):
        return self.sb.get_soc()
    
    def get_cons(self):
            return self.objective_curve[self._state-1]

    def get_action_cons(self):
        return self.consumption
        
        
    def step(self, action):
        # Execute one time step within the environment
        self.ac.turnOff()
        self.sb.stop()
        if self._episode_ended:
            self.reset()
        #Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #Huge Change temperature 
        elif action == 3:
            c = self.ac.hugeChange()
        #SB Charge20
        elif action == 4:
            c = self.sb.charge20() + self.ac.turnOff()
        #SB Charge40
        elif action == 5:
            c = self.sb.charge40() + self.ac.turnOff()
        #SB Charge60
        elif action == 6:
            c = self.sb.charge60() + self.ac.turnOff()
        #SB Discharge20
        elif action == 7:
            c = self.sb.discharge20() + self.ac.turnOff()
        #SB Discharge40
        elif action == 8:
            c = self.sb.discharge40() + self.ac.turnOff()
        #SB Discharge60
        elif action == 9:
            c = self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature and SB Charge20
        elif action == 10:
            c = self.ac.smallChange() + self.sb.charge20()
        #Small Change Temperature and SB Charge40
        elif action == 11:
            c = self.ac.smallChange() + self.sb.charge40()
        #Small Change Temperature and SB Charge20
        elif action == 12:
            c = self.ac.smallChange() + self.sb.charge60()
        #Small Change Temperature and SB Discharge20
        elif action == 13:
            c = self.ac.smallChange() + self.sb.discharge20()
        #Small Change Temperature and SB Discharge40
        elif action == 14:
            c = self.ac.smallChange() + self.sb.discharge40()
        #Small Change Temperature and SB Discharge60
        elif action == 15:
            c = self.ac.smallChange() + self.sb.discharge60()
        #Big Change Temperature and SB Charge20
        elif action == 16:
            c = self.ac.bigChange() + self.sb.charge20()
        #Big Change Temperature and SB Charge40
        elif action == 17:
            c = self.ac.bigChange() + self.sb.charge40()
        #Big Change Temperature and SB Charge60
        elif action == 18:
            c = self.ac.bigChange() + self.sb.charge60()
        #Big Change Temperature and SB Discharge20
        elif action == 19:
            c = self.ac.bigChange() + self.sb.discharge20()
        #Big Change Temperature and SB Discharge40
        elif action == 20:
            c = self.ac.bigChange() + self.sb.discharge40()
        #Big Change Temperature and SB Discharge60
        elif action == 21:
            c = self.ac.bigChange() + self.sb.discharge60()
        #Huge Change Temperature and SB Charge20
        elif action == 22:
            c = self.ac.hugeChange() + self.sb.charge20()
        #Huge Change Temperature and SB Charge40
        elif action == 23:
            c = self.ac.hugeChange() + self.sb.charge40()
        #Huge Change Temperature and SB Charge60
        elif action == 24:
            c = self.ac.hugeChange() + self.sb.charge60()
        #Huge Change Temperature and SB Discharge20
        elif action == 25:
            c = self.ac.hugeChange() + self.sb.discharge20()
        #Huge Change Temperature and SB Discharge40
        elif action == 26:
            c = self.ac.hugeChange() + self.sb.discharge40()
        #Huge Change Temperature and SB Discharge60
        elif action == 27:
            c = self.ac.hugeChange() + self.sb.discharge60()
        
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
        self._state += 1    
                                            
        if val>0 or self._state >= len(self.objective_curve)-1 :
            self._episode_ended = True 
            self.reward += 1 if self._state == len(self.objective_curve)-1 else -1
        else:
            if val == 0:
                self.reward += 1
            else:
                self.reward += 1/abs(val)
        
        return math.ceil(self.objective_curve[self._state]), self.reward, self._episode_ended, {}


    def reset(self):
        # Reset the state of the environment to an initial state
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        #Storage battery
        self.sb = StorageBattery(soc=self.soc)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        
        return math.ceil(self.objective_curve[self._state+1])
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.sb.render()
        self.ac.render()

class UMADemoDEC(gym.Env):
    """UMA DEMOSITE SCENARIO DECREMENTAL CONSUMPTION"""
    metadata = {'render.modes': ['human']}

    def __init__(self, objective_curve, capacity = 120.0, soc = 0.5):
        super(UMADemoDEC, self).__init__()
        # Define action and observation space
        # They must be gym.gym.spaces objects
        # Example when using discrete actions:
        self.action_space = gym.spaces.Discrete(65)
        # Example for using image as input:
        self.obs_space = gym.spaces.Box(low=0, high=100, shape=(1,))
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility    
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        self.soc = soc
        self.sb = StorageBattery(soc=self.soc)
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        self.obs = math.floor(self.objective_curve[self._state+1])
        
    def get_sb_soc(self):
        return self.sb.get_soc()
    
    def get_cons(self):
            return self.objective_curve[self._state-1]
        
    def get_action_cons(self):
        return self.consumption
        
        
    def step(self, action):
        # Execute one time step within the environment
        self.ac.turnOff()
        self.cs.stop()
        self.sb.stop()
        if self._episode_ended:
            self.reset()
         # Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #Huge Change temperature 
        elif action == 3:
            c = self.ac.hugeChange()
        #EV Charge
        elif action == 4:
            c = self.cs.charge(1) + self.ac.turnOff()
        #EV Discharge
        elif action == 5:
            c = self.cs.discharge(1) + self.ac.turnOff()
        #SB Charge20
        elif action == 6:
            c = self.sb.charge20() + self.ac.turnOff()
        #SB Charge40
        elif action == 7:
            c = self.sb.charge40() + self.ac.turnOff()
        #SB Charge60
        elif action == 8:
            c = self.sb.charge60() + self.ac.turnOff()
        #SB Discharge20
        elif action == 9:
            c = self.sb.discharge20() + self.ac.turnOff()
        #SB Discharge40
        elif action == 10:
            c = self.sb.discharge40() + self.ac.turnOff()
        #SB Discharge60
        elif action == 11:
            c = self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature and EV Charge
        elif action == 12:
            c = self.ac.smallChange() + self.cs.charge(1)
        #Small Change Temperature and EV Discharge
        elif action == 13:
            c = self.ac.smallChange() + self.cs.discharge(1)
        #Small Change Temperature and SB Charge20
        elif action == 14:
            c = self.ac.smallChange() + self.sb.charge20()
        #Small Change Temperature and SB Charge40
        elif action == 15:
            c = self.ac.smallChange() + self.sb.charge40()
        #Small Change Temperature and SB Charge20
        elif action == 16:
            c = self.ac.smallChange() + self.sb.charge60()
        #Small Change Temperature and SB Discharge20
        elif action == 17:
            c = self.ac.smallChange() + self.sb.discharge20()
        #Small Change Temperature and SB Discharge40
        elif action == 18:
            c = self.ac.smallChange() + self.sb.discharge40()
        #Small Change Temperature and SB Discharge60
        elif action == 19:
            c = self.ac.smallChange() + self.sb.discharge60()
        #Big Change Temperature and EV Charge
        elif action == 20:
            c = self.ac.bigChange() + self.cs.charge(1)
        #Big Change Temperature and EV Discharge
        elif action == 21:
            c = self.ac.bigChange() + self.cs.discharge(1)
        #Big Change Temperature and SB Charge20
        elif action == 22:
            c = self.ac.bigChange() + self.sb.charge20()
        #Big Change Temperature and SB Charge40
        elif action == 23:
            c = self.ac.bigChange() + self.sb.charge40()
        #Big Change Temperature and SB Charge60
        elif action == 24:
            c = self.ac.bigChange() + self.sb.charge60()
        #Big Change Temperature and SB Discharge20
        elif action == 25:
            c = self.ac.bigChange() + self.sb.discharge20()
        #Big Change Temperature and SB Discharge40
        elif action == 26:
            c = self.ac.bigChange() + self.sb.discharge40()
        #Big Change Temperature and SB Discharge60
        elif action == 27:
            c = self.ac.bigChange() + self.sb.discharge60()
        #Huge Change Temperature and EV Charge
        elif action == 28:
            c = self.ac.hugeChange() + self.cs.charge(1)
        #Huge Change Temperature and EV Discharge
        elif action == 29:
            c = self.ac.hugeChange() + self.cs.discharge(1)
        #Huge Change Temperature and SB Charge20
        elif action == 30:
            c = self.ac.hugeChange() + self.sb.charge20()
        #Huge Change Temperature and SB Charge40
        elif action == 31:
            c = self.ac.hugeChange() + self.sb.charge40()
        #Huge Change Temperature and SB Charge60
        elif action == 32:
            c = self.ac.hugeChange() + self.sb.charge60()
        #Huge Change Temperature and SB Discharge20
        elif action == 33:
            c = self.ac.hugeChange() + self.sb.discharge20()
        #Huge Change Temperature and SB Discharge40
        elif action == 34:
            c = self.ac.hugeChange() + self.sb.discharge40()
        #Huge Change Temperature and SB Discharge60
        elif action == 35:
            c = self.ac.hugeChange() + self.sb.discharge60()
        #EV Charge and SB Charge20
        elif action == 36:
            c = self.cs.charge(1) + self.sb.charge20() + self.ac.turnOff()
        #EV Charge and SB Charge40
        elif action == 37:
            c = self.cs.charge(1) + self.sb.charge40() + self.ac.turnOff()
        #EV Charge and SB Charge60
        elif action == 38:
            c = self.cs.charge(1) + self.sb.charge60() + self.ac.turnOff()
        #EV Charge and SB Discharge20
        elif action == 39:
            c = self.cs.charge(1) + self.sb.discharge20() + self.ac.turnOff()
        #EV Charge and SB Discharge40
        elif action == 40:
            c = self.cs.charge(1) + self.sb.discharge40() + self.ac.turnOff()
        #EV Charge and SB Discharge60
        elif action == 41:
            c = self.cs.charge(1) + self.sb.discharge60() + self.ac.turnOff()
        #EV Discharge and SB Charge20
        elif action == 42:
            c = self.cs.discharge(1) + self.sb.charge20() + self.ac.turnOff()
        #EV Discharge and SB Charge40
        elif action == 43:
            c = self.cs.discharge(1) + self.sb.charge40() + self.ac.turnOff()
        #EV Discharge and SB Charge60
        elif action == 44:
            c = self.cs.discharge(1) + self.sb.charge60() + self.ac.turnOff()
        #EV Discharge and SB Discharge20
        elif action == 45:
            c = self.cs.discharge(1) + self.sb.discharge20() + self.ac.turnOff()
        #EV Discharge and SB Discharge40
        elif action == 46:
            c = self.cs.discharge(1) + self.sb.discharge40() + self.ac.turnOff()
        #EV Discharge and SB Discharge60
        elif action == 47:
            c = self.cs.discharge(1) + self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature, EV Charge and SB Charge20
        elif action == 48:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge20()
        #Small Change Temperature, EV Charge and SB Charge40
        elif action == 49:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge40()
        #Small Change Temperature, EV Charge and SB Charge60
        elif action == 50:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.charge60()
        #Small Change Temperature, EV Charge and SB Discharge20
        elif action == 51:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge20()
        #Small Change Temperature, EV Charge and SB Discharge40
        elif action == 52:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge40()
        #Small Change Temperature, EV Charge and SB Discharge60
        elif action == 53:
            c = self.ac.smallChange() + self.cs.charge(1) + self.sb.discharge60()
        #Big Change Temperature, EV Charge and SB Charge20
        elif action == 54:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge20()
        #Big Change Temperature, EV Charge and SB Charge40
        elif action == 55:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge40()
        #Big Change Temperature, EV Charge and SB Charge60
        elif action == 56:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.charge60()
        #Big Change Temperature, EV Charge and SB Discharge20
        elif action == 57:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge20()
        #Big Change Temperature, EV Charge and SB Discharge40
        elif action == 58:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge40()
        #Big Change Temperature, EV Charge and SB Discharge60
        elif action == 59:
            c = self.ac.bigChange() + self.cs.charge(1) + self.sb.discharge60()
        #Huge Change Temperature, EV Charge and SB Charge20
        elif action == 60:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.charge20()
        #Huge Change Temperature, EV Charge and SB Charge40
        elif action == 61:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.charge40()
        #Huge Change Temperature, EV Charge and SB Charge60
        elif action == 62:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.charge60()
        #Huge Change Temperature, EV Charge and SB Discharge20
        elif action == 63:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.discharge20()
        #Huge Change Temperature, EV Charge and SB Discharge40
        elif action == 64:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.discharge40()
        #Huge Change Temperature, EV Charge and SB Discharge60
        elif action == 65:
            c = self.ac.hugeChange() + self.cs.charge(1) + self.sb.discharge60()

        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
        self._state += 1    
        if val<0 or self._state >= len(self.objective_curve)-1 :
            self._episode_ended = True 
            self.reward += 1 if self._state == len(self.objective_curve)-1 else -1
        else:
            if val == 0:
                self.reward += 0
            else:
                self.reward += abs(val/self.objective_curve[self._state-1])
        
        return math.floor(self.objective_curve[self._state]), self.reward, self._episode_ended, {}


    def reset(self):
        # Reset the state of the environment to an initial state
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        #Storage battery
        self.sb = StorageBattery(self.soc)
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        
        return math.floor(self.objective_curve[self._state+1])
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.sb.render()
        self.ac.render()
        self.cs.render()



class UMADemoDEC_No_Batteries(gym.Env):
    """UMA DEMOSITE SCENARIO INCREMENTAL CONSUMPTION"""
    metadata = {'render.modes': ['human']}

    def __init__(self, objective_curve):
        super(UMADemoDEC_No_Batteries, self).__init__()
        # Define action and observation space
        # They must be gym.gym.spaces objects
        # Example when using discrete actions:
        self.action_space = gym.spaces.Discrete(11)
        # Example for using image as input:
        self.obs_space = gym.spaces.Box(low=0, high=100, shape=(1,))
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility    
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        self.obs = math.floor(self.objective_curve[self._state+1])
    
    def get_cons(self):
            return self.objective_curve[self._state-1]

    def get_action_cons(self):
        return self.consumption
        
        
    def step(self, action):
        # Execute one time step within the environment
        self.ac.turnOff()
        self.cs.stop()
        if self._episode_ended:
            self.reset()
         # Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #Huge Change temperature 
        elif action == 3:
            c = self.ac.hugeChange()
        #EV Charge
        elif action == 4:
            c = self.cs.charge(1) + self.ac.turnOff()
        #EV Discharge
        elif action == 5:
            c = self.cs.discharge(1) + self.ac.turnOff()
        #Small Change Temperature and EV Charge
        elif action == 6:
            c = self.ac.smallChange() + self.cs.charge(1)
        #Small Change Temperature and EV Discharge
        elif action == 7:
            c = self.ac.smallChange() + self.cs.discharge(1)
        #Big Change Temperature and EV Charge
        elif action == 8:
            c = self.ac.bigChange() + self.cs.charge(1)
        #Big Change Temperature and EV Discharge
        elif action == 9:
            c = self.ac.bigChange() + self.cs.discharge(1)
        #Huge Change Temperature and EV Charge
        elif action == 10:
            c = self.ac.hugeChange() + self.cs.charge(1)
        #Huge Change Temperature and EV Discharge
        elif action == 11:
            c = self.ac.hugeChange() + self.cs.discharge(1)
            
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
        self._state += 1    
        
        if val<0 or self._state >= len(self.objective_curve)-1 :
            self._episode_ended = True 
            self.reward += 1 if self._state == len(self.objective_curve)-1 else -1
        else:
            if val == 0:
                self.reward += 0
            else:
                self.reward += abs(val/self.objective_curve[self._state-1])
        
        return math.floor(self.objective_curve[self._state]), self.reward, self._episode_ended, {}


    def reset(self):
        # Reset the state of the environment to an initial state
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        # EV Charging Station
        self.cs = ChargingStation()
        self.cs.carArrival(1)
        self.cs.carArrival(2)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        
        return math.floor(self.objective_curve[self._state+1])
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.ac.render()
        self.cs.render()



class UMADemoDEC_No_Car(gym.Env):
    """UMA DEMOSITE SCENARIO DECREMENTAL CONSUMPTION"""
    metadata = {'render.modes': ['human']}

    def __init__(self, objective_curve, capacity = 120.0, soc = 0.5):
        super(UMADemoDEC_No_Car, self).__init__()
        # Define action and observation space
        # They must be gym.gym.spaces objects
        # Example when using discrete actions:
        self.action_space = gym.spaces.Discrete(20)
        # Example for using image as input:
        self.obs_space = gym.spaces.Box(low=0, high=100, shape=(1,))
        #Current step
        self._state = 0
        self._episode_ended = False        

        #Set base_consumption
        self.objective_curve = objective_curve
        #Set flexibility    
        #Air conditioning of the room
        self.ac = Airconditioning()
        #Storage battery
        self.soc = soc
        self.sb = StorageBattery(soc=self.soc)
        # EV Charging Station
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        self.obs = math.floor(self.objective_curve[self._state+1])
        
    def get_sb_soc(self):
        return self.sb.get_soc()
    
    def get_cons(self):
        return self.objective_curve[self._state-1]
    
    def get_action_cons(self):
        return self.consumption
        
        
    def step(self, action):
        # Execute one time step within the environment
        self.ac.turnOff()
        self.sb.stop()
        if self._episode_ended:
            self.reset()
         # Do nothing.
        if action == 0:
            c = self.ac.turnOff()
        #Small change temperature
        elif action == 1:
            c = self.ac.smallChange()
        #Big Change temperature 
        elif action == 2:
            c = self.ac.bigChange()
        #Huge Change temperature 
        elif action == 3:
            c = self.ac.hugeChange()
        #SB Charge20
        elif action == 4:
            c = self.sb.charge20() + self.ac.turnOff()
        #SB Charge40
        elif action == 5:
            c = self.sb.charge40() + self.ac.turnOff()
        #SB Charge60
        elif action == 6:
            c = self.sb.charge60() + self.ac.turnOff()
        #SB Discharge20
        elif action == 7:
            c = self.sb.discharge20() + self.ac.turnOff()
        #SB Discharge40
        elif action == 8:
            c = self.sb.discharge40() + self.ac.turnOff()
        #SB Discharge60
        elif action == 9:
            c = self.sb.discharge60() + self.ac.turnOff()
        #Small Change Temperature and SB Charge20
        elif action == 10:
            c = self.ac.smallChange() + self.sb.charge20()
        #Small Change Temperature and SB Charge40
        elif action == 11:
            c = self.ac.smallChange() + self.sb.charge40()
        #Small Change Temperature and SB Charge20
        elif action == 12:
            c = self.ac.smallChange() + self.sb.charge60()
        #Small Change Temperature and SB Discharge20
        elif action == 13:
            c = self.ac.smallChange() + self.sb.discharge20()
        #Small Change Temperature and SB Discharge40
        elif action == 14:
            c = self.ac.smallChange() + self.sb.discharge40()
        #Small Change Temperature and SB Discharge60
        elif action == 15:
            c = self.ac.smallChange() + self.sb.discharge60()
        #Big Change Temperature and SB Charge20
        elif action == 16:
            c = self.ac.bigChange() + self.sb.charge20()
        #Big Change Temperature and SB Charge40
        elif action == 17:
            c = self.ac.bigChange() + self.sb.charge40()
        #Big Change Temperature and SB Charge60
        elif action == 18:
            c = self.ac.bigChange() + self.sb.charge60()
        #Big Change Temperature and SB Discharge20
        elif action == 19:
            c = self.ac.bigChange() + self.sb.discharge20()
        #Big Change Temperature and SB Discharge40
        elif action == 20:
            c = self.ac.bigChange() + self.sb.discharge40()
        #Big Change Temperature and SB Discharge60
        elif action == 21:
            c = self.ac.bigChange() + self.sb.discharge60()
        #Huge Change Temperature and SB Charge20
        elif action == 22:
            c = self.ac.hugeChange() + self.sb.charge20()
        #Huge Change Temperature and SB Charge40
        elif action == 23:
            c = self.ac.hugeChange() + self.sb.charge40()
        #Huge Change Temperature and SB Charge60
        elif action == 24:
            c = self.ac.hugeChange() + self.sb.charge60()
        #Huge Change Temperature and SB Discharge20
        elif action == 25:
            c = self.ac.hugeChange() + self.sb.discharge20()
        #Huge Change Temperature and SB Discharge40
        elif action == 26:
            c = self.ac.hugeChange() + self.sb.discharge40()
        #Huge Change Temperature and SB Discharge60
        elif action == 27:
            c = self.ac.hugeChange() + self.sb.discharge60()
        
        val = self.objective_curve[self._state] + c
        self.consumption = c
        self.cumulative_consumption += -abs(val)
        self._state += 1    
        if val<0 or self._state >= len(self.objective_curve)-1 :
            self._episode_ended = True 
            self.reward += 1 if self._state == len(self.objective_curve)-1 else -1
        else:
            if val == 0:
                self.reward += 0
            else:
                self.reward += abs(val/self.objective_curve[self._state-1])
        
        return math.floor(self.objective_curve[self._state]), self.reward, self._episode_ended, {}


    def reset(self):
        # Reset the state of the environment to an initial state
        self._state = 0
        self._episode_ended = False
        self.ac = Airconditioning()
        #Storage battery
        self.sb = StorageBattery(self.soc)
        self.consumption = 0
        self.cumulative_consumption = 0
        self.reward = 0
        
        return math.floor(self.objective_curve[self._state+1])
    
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        self.sb.render()
        self.ac.render()