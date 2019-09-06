import pandas as pd
import numpy as np
from .battery import Battery
        

class Applications:
    def __init__(self, battery_object):
        
        self.battery = battery_object

    def show_soc(self):
        print(self.battery.soc)
        
    def arbitrage(self, price_list, buy_price, sell_price):
        '''
        Compares buy- and sell price to prices passed in the price list.
        Whenever the list price drops below the buy-price, the battery is charged as much as possible.
        When the list price is higher than the sell-price, the battery is discharged as much as possible.
        
        INPUT:
        price_list - List of prices (float) [€/MWh]
        buy_price - highest price for purchasing energy (float) [€/MWh]
        sell_price - lowest price for selling energy from the battery (float) [€/MWh]
        
        OUTPUT:
        df_arbitrage - dataframe summarizing all transactions from arbitrage application
        '''
        if buy_price >= sell_price:
            raise ValueError('buy_price must be lower than sell_price')
        
        transaction_datetime_list = []
        transaction_type_list = []
        transaction_volume_list = []
        transaction_price_list = []
        transaction_revenue_list = []
        
        for list_price in price_list:
            if list_price <= buy_price:
                
                # buying energy:
                self.battery.charge_max_possible()
                transaction_datetime_list.append(self.battery.datetime_curve[-1])
                transaction_type_list.append('buy')
                transaction_price_list.append(list_price)
                transaction_volume_list.append(self.battery.energy_curve[-1]/1000)
                transaction_revenue_list.append(-self.battery.energy_curve[-1]*list_price/1000)
                
            elif list_price >= sell_price:
                
                # selling energy:
                self.battery.discharge_max_possible()
                transaction_datetime_list.append(self.battery.datetime_curve[-1])
                transaction_type_list.append('sell')
                transaction_price_list.append(list_price)
                transaction_volume_list.append(self.battery.energy_curve[-1]/1000)
                transaction_revenue_list.append(-self.battery.energy_curve[-1]*list_price/1000)
                
            else:
                
                # doing nothing. There ist no entry in df_arbitrage for this timestep
                self.battery.do_nothing()
        
        df_arbitrage = pd.DataFrame({'datetime':transaction_datetime_list, 
                                     'transaction_type':transaction_type_list,
                                     'price_eur_per_MWh':transaction_price_list,
                                     'volume_MWh':transaction_volume_list,
                                     'revenue_eur':transaction_revenue_list})

        return df_arbitrage
    
    def peakshaving(self, loadcurve, peak_limit):
        
        '''
        Uses the battery to reduce cunsumption peaks to the specified limit.
        Whenever the loadcurve value is above the specified peak limit, the battery discharges to get the loadcurve to the peak limit.
        When the loadcurve value drops below the peak limit, the battery is being charged if necessary.
        
        HINT: Usually the peak shaving application uses 15 min steps, make sure to set 
        timestep_minutes=15 in that case. Also depending on the observed year, the variable
        start_datetime can be adjusted accordingly, passing a pandas datetime object.
        
        INPUT:
        loadcurve - list of customer loads (float) [kW]
        peak_limit - customer load limit that must not be exceeded  (float) [kW]
        
        OUTPUT:
        df_peakshaving - dataframe with original loadcurve, battery output, battery soc and new loadcurve
        '''
        
        ps_datetime_list = []
        ps_battery_power_list = []
        ps_soc_list = []
        
        for load in loadcurve:
            if load > peak_limit:
                self.battery.discharge_with_power(load-peak_limit, warnings_on = False)
                
            else:
                self.battery.charge_with_power(peak_limit-load, warnings_on = False)
                
            ps_datetime_list.append(self.battery.datetime_curve[-1])
            ps_battery_power_list.append(self.battery.power_curve[-1])
            ps_soc_list.append(self.battery.soc_curve[-1])
            
        resulting_loadcurve = [l+b for l,b in zip(loadcurve, ps_battery_power_list)]
        
        if max(resulting_loadcurve) > peak_limit:
            print('WARNING: peak shaving was not successful')
        
        df_peakshaving = pd.DataFrame({'datetime':ps_datetime_list,
                                       'original_loadcurve':loadcurve,
                                       'battery_power':ps_battery_power_list,
                                       'new_loadcurve':resulting_loadcurve,
                                       'battery_soc':ps_soc_list})
    
        return df_peakshaving
            