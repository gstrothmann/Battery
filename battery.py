class Battery:
    def __init__(self, max_power = 1000, net_capacity = 1000, round_trip_efficiency = 0.92, initial_soc = 0.5, timestep_minutes = 60):
        import pandas as pd
        import numpy as np
        from applications import Applications
        
        self.power = max_power
        self.capacity = net_capacity,
        self.eff_chg = np.sqrt(round_trip_efficiency)
        self.eff_dch = np.sqrt(round_trip_efficiency)
        self.soc = 0.5
        self.timestep_minutes = timestep_minutes
        self.efc = 0
        self.power_curve = []
        self.capacity_curve = []
        self.applications = Applications(self)
    
    def reset(self):
        '''Resets the values for the SOC and EFC as well as the power and capacity curve.
        
        INPUT: None
        OUTPUT: None
        '''
        self.power_curve = []
        self.capacity_curve = []
        self.soc = 0.5 
        self.efc = 0