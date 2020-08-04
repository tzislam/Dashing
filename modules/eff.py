

import matplotlib.pyplot as plt
import numpy as np
import os

def print_loss(data_loader):

    procs = data_loader.proc_configs
    all_procs = [1, 4, 8, 12, 16, 20, 24, 28, 32]
    
    for reg in data_loader.get_regions():
        #print("\n--------------")
        #print("Region: ", reg)

        eff_loss = data_loader.get_app_eff_loss(reg)
        #print(eff_loss)
        
        ax = plt.axes()
        ax.plot(np.arange(len(eff_loss)), eff_loss)
        plt.title(reg)
        ax.set_ylim([0,1.05])

        padding = len(procs) - len(all_procs)
        labels = []
        for _ in range(padding):
            labels.append('')
        [labels.append(proc) for proc in procs]
        plt.xticks(np.arange(len(procs)), labels)

