import pandas as pd
import numpy as np
from battery import Battery
        

class Dimensioning:
    def __init__(self, battery_object):
        
        self.battery = battery_object

    def show_soc(self):
        print(self.battery.soc)