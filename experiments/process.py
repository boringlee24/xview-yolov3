import pdb
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas
import sys

gpus = ['cpu', 'k80d', 'm60a', 't4a', 'p100d', 'v100a'] # cpu node is c0191
GPUs = ['CPU', 'K80', 'M60', 'T4', 'P100', 'V100']
#GPUs = gpus[:]
#idle_pwr = [27, 60, 15]

fig, axs = plt.subplots(1, 3, figsize=(12,3.5), gridspec_kw={'hspace': 0, 'wspace': 0.3, 'top': 0.9, 'left':0.08, 'right':0.99, 'bottom':0.08})
x = np.arange(len(gpus))
width = 0.4

qps_list = []
lat_list = []
tail_list = []
# first plot throughput across different gpus
for i, gpu in enumerate(gpus):
    path = f'logs/lat_list_{gpu}.json'
       
    with open(path) as f:
        lats = json.load(f)
    lat_mean = round(np.mean(lats))
    lat_list.append(lat_mean)
    tail_list.append(np.percentile(lats,95))
    qps = 1000 / lat_mean
    qps_list.append(qps)

def autolabel(rects,ax):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
#        pdb.set_trace()
        ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                '%s' % round(height,2),
                ha='center', va='bottom')


rect = axs[0].bar(x, lat_list, width=width) #TODO
axs[0].set_xticks(x)
axs[0].set_xticklabels(GPUs)
axs[0].set_title('inference mean latency', fontsize=14)
axs[0].set_ylabel('latency\n(ms)', fontsize=13)
axs[0].set_ylim(0, max(lat_list) * 1.1)
autolabel(rect, axs[0])

rect = axs[1].bar(x, qps_list, width=width) #TODO
axs[1].set_xticks(x)
axs[1].set_xticklabels(GPUs)
axs[1].set_title('inference throughput', fontsize=14)
axs[1].set_ylabel('throughput\n(query-per-second)', fontsize=13)
autolabel(rect, axs[1])
axs[1].set_ylim(0, max(qps_list) * 1.1)

energy_list = []
column = ' power.draw [W]'
for i, gpu in enumerate(gpus):
    if gpu == 'cpu':
        pwr = 50
    else:
        path = f'logs/{gpu}.csv'
        df = pandas.read_csv(path)
#        pwr = np.mean(df[column]) #- idle_pwr[i] #watt
        pwr = np.percentile(df[column], 90) #TODO

    time = lat_list[i]/1000 #second
    energy_list.append(pwr)

rect = axs[2].bar(x, energy_list, width)
axs[2].set_xticks(x)
axs[2].set_xticklabels(GPUs)
axs[2].set_title('inference power', fontsize=14)
axs[2].set_ylabel('Power (Watt)', fontsize=13)
autolabel(rect, axs[2])
axs[2].set_ylim(0, max(energy_list) * 1.1)

for ax in axs:
    ax.grid(which='major', axis='y', ls='dotted')


plt.savefig(f'plots/data.png')

