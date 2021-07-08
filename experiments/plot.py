import pdb
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas
import sys

#GPUs = gpus[:]
#idle_pwr = [27, 60, 15]

x_label = ['P100-only', 'P100+T4']
fig, axs = plt.subplots(1, 1, figsize=(3.5,3.5), gridspec_kw={'hspace': 0, 'wspace': 0.3, 'top': 0.9, 'left':0.22, 'right':0.99, 'bottom':0.12})
x = np.arange(len(x_label))
width = 0.3
powers = [5735, 3881]
bar_label = ['31 P100', '11 P100\n+ 26 T4']

def autolabel(rects,ax,labels):
    """
    Attach a text label above each bar displaying its height
    """
    for i,rect in enumerate(rects):
        height = rect.get_height()
#        pdb.set_trace()
        ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                labels[i],
                ha='center', va='bottom')


rect = axs.bar(x, powers, width=width, color='darkorange') #TODO
axs.set_xticks(x)
axs.set_xticklabels(x_label)
axs.set_title('xView Inference Power', fontsize=14)
axs.set_ylabel('Power (W)', fontsize=13)
axs.set_ylim(0, max(powers) * 1.2)
autolabel(rect, axs, bar_label)
axs.grid(which='major', axis='y', ls='dotted')

plt.savefig(f'plots/xview.png')

