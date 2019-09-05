import pandas as pd
import numpy as np
from battery import Battery
        

class Dimensioning:
    def __init__(self, battery_object):
        
        self.battery = battery_object

    def peakshaving(self, loadcurve, peak_limit):
        
        '''
        Modifies the battery object so that it has the minimum power and capacity
        required in order to successfully shave all peaks.
        
        HINT: Usually the peak shaving application uses 15 min steps, make sure to set 
        timestep_minutes=15 in that case. Also depending on the observed year, the variable
        start_datetime can be adjusted accordingly, passing a pandas datetime object.
        
        INPUT:
        loadcurve - list of customer loads (float) [kW]
        peak_limit - customer load limit that must not be exceeded  (float) [kW]
        
        OUTPUT:
        String with the needed battery power and capaicty.
        '''
        
        # calculate needed power from difference loadcurve-peak_limit
        needed_power = np.ceil(max(loadcurve)-peak_limit)
        
        # first reset the battery and set soc to 1.0
        self.battery.reset()
        self.battery.soc = 1.0
        
        # set power to needed power and capacity to a very high value
        self.battery.power = needed_power
        self.battery.capacity = 1e+9
        
        # perform the peak shaving application
        df_peakshaving = self.battery.applications.peakshaving(loadcurve, peak_limit)
        
        # calculate how much of the large capacity was actually used
        soc_diff = 1.0 - min(df_peakshaving.battery_soc)
        needed_capacity = np.ceil(soc_diff * 1e+09)
        
        # set needed capacity to battery capacity
        self.battery.capacity = needed_capacity
        
        return f'Battery power: {needed_power} kW, capacity: {needed_capacity} kWh'
            