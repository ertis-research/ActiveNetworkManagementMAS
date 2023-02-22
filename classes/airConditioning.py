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