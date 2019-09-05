import pandas as pd
import numpy as np
        

class Dimensioning:
    def __init__(self, battery_object):
        
        from battery import Battery
        self.battery = battery_object

    def show_soc(self):
        print(self.battery.soc)