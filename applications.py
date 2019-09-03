class Applications:
    def __init__(self, battery_object):
        import pandas as pd
        import numpy as np
        from battery import Battery
        self.battery = battery_object

    def show_soc(self):
        print(self.battery.soc)