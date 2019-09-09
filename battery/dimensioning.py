import pandas as pd
import numpy as np
from .battery import Battery
        

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
        String with the needed battery power, capaicty and efc.
        '''
        
        # calculate needed power from difference loadcurve-peak_limit
        needed_power = np.ceil(max(loadcurve)-peak_limit)
        
        # first reset the battery and set soc to 1.0
        self.battery.reset()
        self.battery.soc = 1.0
        
        # set power to needed power and capacity to a very high value
        self.battery.power = needed_power
        self.battery.capacity = 1e+6
        
        # perform the peak shaving application
        df_peakshaving = self.battery.applications.peakshaving(loadcurve, peak_limit)
        
        # calculate how much of the large capacity was actually used
        soc_diff = 1.0 - min(df_peakshaving.battery_soc)
        needed_capacity = np.ceil(soc_diff * 1e+06)
        
        # set needed capacity to battery capacity
        self.battery.capacity = needed_capacity
        
        # now re-run the peak shaving application with the correct capacity:
        self.battery.reset()
        self.battery.applications.peakshaving(loadcurve, peak_limit);
        
        return f'Battery power: {needed_power} kW, capacity: {needed_capacity} kWh, efc: {self.battery.get_efc()}'
    
    def loadfollowing(self, production_curve, loadcurve):
        '''
        Modifies the battery object so that it has the minimum power and capacity
        required in order to shift all the production to the consumption side that
        is needed in order to supply the consumption side with 100% of the produced
        energy.
        
        INPUT:
        production_curve - list of production values (float) [kW]
        loadcurve - list of consumer loads (float) [kW]

        OUTPUT:
        String with the needed battery power, capaicty and efc.
        '''
        
        equivalent_peak_shaving_curve = loadcurve - production_curve
        power_to_shift_up_by = abs(min(equivalent_peak_shaving_curve))
        equivalent_peak_shaving_curve_shifted = equivalent_peak_shaving_curve + power_to_shift_up_by
        
        needed_dimensions = self.battery.dimensioning.peakshaving(equivalent_peak_shaving_curve_shifted, power_to_shift_up_by)
        
        return needed_dimensions