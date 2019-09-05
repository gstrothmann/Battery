import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Battery:
    def __init__(self, max_power = 1000, net_capacity = 1000, round_trip_efficiency = 0.92, initial_soc = 0.5, timestep_minutes = 60):
        
        from applications import Applications
        from dimensioning import Dimensioning
        
        self.power = max_power
        self.capacity = net_capacity
        self.eff_chg = np.sqrt(round_trip_efficiency)
        self.eff_dch = np.sqrt(round_trip_efficiency)
        self.soc = 0.5
        self.timestep_minutes = timestep_minutes
        self.efc = 0
        self.power_curve = []
        self.soc_curve = []
        self.datetime_curve = []
        self.energy_curve = []
        self.applications = Applications(self)
        self.dimensioning = Dimensioning(self)
        self.start_datetime = pd.datetime(2020,1,1,0,0)
    
    def reset(self):
        '''Resets the values for the SOC and EFC as well as the power and capacity curve.
        
        INPUT: None
        OUTPUT: None
        '''
        self.power_curve = []
        self.soc_curve = []
        self.energy_curve = []
        self.datetime_curve = []
        self.soc = 0.5 
        self.efc = 0
        
    def get_battery_curves(self):
        '''Returns a pandas dataframe containing a power curve and an soc curve of the battery activiy.
        
        INPUT: None
        OUTPUT: Pandas Dataframe
        '''
        
        return pd.DataFrame({'datetime':self.datetime_curve, 'soc':self.soc_curve, 'power_output':self.power_curve, 'energy_output':self.energy_curve})
    
    def charge_with_energy(self, energy, warnings_on = True):
        '''
        Charges the Battery object with the amount of energy specified. 
        Due to charging losses, not the whole amount of energy specified will be stored inside the battery.
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        Optionally prints out a warning if the amount of energy specified exceeds the possible amount.
        
        INPUT:
        energy - amount of energy to be fed into the battery before charging losses (kWh)
        warnings_on (optional) - if True, the function gives a warning if the specified amount exceeds the possible limit or is negative
        
        OUTPUT: None
        '''
        specified_charging_energy = energy
        charging_energy = specified_charging_energy
        
        # calculate amount of energy that can be charged based on the current soc and the battery capacity
        max_possible_charging_energy_soc = (1.0-self.soc)*self.capacity/self.eff_chg
        
        # calculate amount of energy that can be charged based on the max battery system power
        max_possible_charging_energy_power = self.power * self.eff_chg * self.timestep_minutes/60
        
        # take min value of the previous two
        max_possible_charging_energy = min(max_possible_charging_energy_soc, max_possible_charging_energy_power)
        
        # calculate actual charging energy based on specified amount and limit
        if specified_charging_energy > max_possible_charging_energy:
            charging_energy = max_possible_charging_energy
            if warnings_on:
                print('Specified energy exceeds technical limit. Amount is reduced.')
        elif specified_charging_energy < 0:
            charging_energy = 0
            if warnings_on:
                print('Specified energy must be a positive value. Value set to 0.')
        
        # Perform actual battery charging      
            
        # add records to datetime-, power- and soc-list. Each entry represents the status of the system 
        # at the beginning of the specified time. That means, that the resulting soc will be added with 
        # a 1-step-delay compared to the power.
        
        # add record to datetime list
        if len(self.datetime_curve) == 0:
            # no entries in the lists so far; creating first one from start_datetime variable
            self.datetime_curve.append(self.start_datetime)
        else:
            self.datetime_curve.append(self.datetime_curve[-1] + pd.Timedelta(minutes = self.timestep_minutes))
        
        # add record to power list; positive values for charging
        charging_power = charging_energy*60/self.timestep_minutes
        self.power_curve.append(charging_power)
        
        # add record to energy list; positive values for charging
        self.energy_curve.append(charging_power*self.timestep_minutes/60)
        
        # first add previous soc-record to soc-list...
        self.soc_curve.append(self.soc)
        
        # ...now change soc-value for beginning of next timestep
        self.soc = self.soc + charging_energy*self.eff_chg/self.capacity
        
        
    def charge_with_power(self, power, warnings_on = True):
        '''
        Charges the Battery object with the power specified. 
        Due to charging losses, not the whole amount of energy specified will be stored inside the battery.
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        Optionally prints out a warning if the amount of energy specified exceeds the possible amount.
        
        INPUT:
        power - amount of energy to be fed into the battery (kW)
        warnings_on (optional) - if True, the function gives a warning if the specified amount exceeds the possible limit or is negative
        
        OUTPUT: None
        '''
        
        # convert from specified power to energy and then pass to function charge_with_energy(...)
        energy = power*self.timestep_minutes/60
        
        self.charge_with_energy(energy, warnings_on)
        
    def charge_max_possible(self):
        '''
        Charges the Battery object with the maximum possible power specified based on the current soc and the maximum system power input. 
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        
        INPUT: None
        OUTPUT: None
        '''    
        
        self.charge_with_power(self.power, warnings_on = False)
        
    def discharge_with_energy(self, energy, warnings_on = True):
        '''
        Discharges the Battery object with the amount of energy specified. 
        The specified energy is the energy that will actually be available outside the battery. 
        Due to charging losses, the amount that is "lost" from inside the battery is larger than this.
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        Optionally prints out a warning if the amount of energy specified exceeds the possible amount.
        
        INPUT:
        energy - amount of energy to be provided from the battery (kWh)
        warnings_on (optional) - if True, the function gives a warning if the specified amount exceeds the possible limit or is negative
        
        OUTPUT: None
        '''
        specified_discharging_energy = energy
        discharging_energy = specified_discharging_energy
        
        # calculate amount of energy that can be provided based on the current soc and the battery capacity
        max_possible_discharging_energy_soc = self.soc*self.capacity*self.eff_dch
        
        # calculate amount of energy that can be provided based on the max battery system power
        max_possible_discharging_energy_power = self.power * self.timestep_minutes/60
        
        # take min value of the previous two
        max_possible_discharging_energy = min(max_possible_discharging_energy_soc, max_possible_discharging_energy_power)
        
        # calculate actual discharging energy based on specified amount and limit
        if specified_discharging_energy > max_possible_discharging_energy:
            discharging_energy = max_possible_discharging_energy
            if warnings_on:
                print('Specified energy exceeds technical limit. Amount is reduced.')
        elif specified_discharging_energy < 0:
            discharging_energy = 0
            if warnings_on:
                print('Specified energy must be a positive value. Value set to 0.')
        
        # Perform actual battery discharging      
            
        # add records to datetime-, power- and soc-list. Each entry represents the status of the system 
        # at the beginning of the specified time. That means, that the resulting soc will be added with 
        # a 1-step-delay compared to the power.
        
        # add record to datetime list
        if len(self.datetime_curve) == 0:
            # no entries in the lists so far; creating first one from start_datetime variable
            self.datetime_curve.append(self.start_datetime)
        else:
            self.datetime_curve.append(self.datetime_curve[-1] + pd.Timedelta(minutes = self.timestep_minutes))
        
        # add record to power list; negative values for discharging
        discharging_power = discharging_energy*60/self.timestep_minutes
        self.power_curve.append(-discharging_power)
        
        # add record to energy list; negative values for discharging
        self.energy_curve.append(-discharging_power*self.timestep_minutes/60)
        
        # first add previous soc-record to soc-list...
        self.soc_curve.append(self.soc)
        
        # ...now change soc-value for beginning of next timestep
        self.soc = self.soc - discharging_energy/(self.capacity*self.eff_dch)
        
        
    def discharge_with_power(self, power, warnings_on = True):
        '''
        Discharges the Battery object with the power specified. 
        The specified value is the power that will actually be available outside the battery. 
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        Optionally prints out a warning if the amount of energy specified exceeds the possible amount.
        
        INPUT:
        power - amount of energy to be provided by the battery (kW)
        warnings_on (optional) - if True, the function gives a warning if the specified amount exceeds the possible limit or is negative
        
        OUTPUT: None
        '''
        
        # convert from specified power to energy and then pass to function charge_with_energy(...)
        energy = power*self.timestep_minutes/60
        
        self.discharge_with_energy(energy, warnings_on)
        
    def discharge_max_possible(self):
        '''
        Discharges the Battery object with the maximum possible power specified based on the current soc and the maximum system power input. 
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        
        INPUT: None
        OUTPUT: None
        '''    
        
        self.discharge_with_power(self.power, warnings_on = False)
        
    def do_nothing(self):
        '''
        The battery will neither charge nor discharge for one timestep.
        This creates a new record in the battery curve, including a new timestamp, power- and soc-value.
        
        INPUT: None
        OUTPUT: None
        ''' 
        
        self.charge_with_power(0, warnings_on = False)
        
    def get_efc(self):
        '''
        Returns amount of equivalent full cycles based on the Battery SOC record. 
        One equivalent full cycle is equal to one complete charge- and discharge cycle of the battery.
        
        INPUT: None
        OUTPUT: efc - Equivalent full cycles of Battery (float)
        ''' 
        
        efc = 0
        if len(self.soc_curve) < 2:
            efc = 0
        else:
            # create two soc-lists: one with a dropped first element, one with a dropped last element.
            soc_curve_drop_first = self.soc_curve[1:]
            soc_curve_drop_last = self.soc_curve[:-2]
            
            # create a list with the absolute values of the differences of these lists:
            soc_curve_abs_diffs = [abs(f-l) for f,l in zip(soc_curve_drop_first, soc_curve_drop_last)]
            
            # calculate efc by adding the absolute differences and dividing by 2 (for charge- & discharge)
            efc = sum(soc_curve_abs_diffs)/2
            
        return efc