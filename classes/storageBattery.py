class StorageBattery():
    def __init__(self, capacity = 120.0, soc = 0.5):
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
        self.consumption = min(5, abs(self.soc - 5))
        self.soc -=  self.consumption
        return self.consumption
    
    def discharge40(self):
        """
            Simulation of 40Kwh discharge (40kwh = 10kw per 15 minutes)
            
        """
        self.consumption = min(10, abs(self.soc - 10))
        self.soc -= self.consumption
        return self.consumption
        
    
    def discharge60(self):
        """
            Simulation of 60Kwh discharge (60kwh = 15kw per 15 minutes)
            : return consumption
        """
        self.consumption = min(15, abs(self.soc - 15))
        self.soc -= self.consumption
        return self.consumption
    
    def stop(self):
        """
            Stop processing
        """
        self.consumption = 0
        
    def get_soc(self):
        """
            get state of charge
        """
        return self.soc
        
    def render(self, mode="human"):
        """
            Print the ev charging station status
        """
        
        print ("SB -> Capacity: {}, State of Charge: {}, Consumption: {}".format(self.capacity, self.soc, self.consumption))
    
    def reset(self):
        self.soc = self.capacity * self.state if self.state else self.capacity * 0.5 
        self.consumption = 0