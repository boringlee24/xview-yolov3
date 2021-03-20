from scipy.optimize import linprog
import json
import pdb
import numpy as np

with open('config.json') as f:
    inputs = json.load(f)

throughput = [-x for x in inputs['throughput_qps']]
target_lat = inputs['target_lat']
latency = [x - target_lat for x in inputs['latency_ms']]
power = inputs['power_W']

############ optimization kernel ###############

obj = power
lhs_ineq = [throughput, latency]
rhs_ineq = [-inputs['target_qps'], 0]
opt = linprog(c=obj, A_ub=lhs_ineq, b_ub=rhs_ineq, method='revised simplex')
optima = np.ceil(opt.x)

###############################################

hardware = inputs['hardware']
power_opt = sum(np.multiply(power, optima))
print(f'optimal power: {power_opt} Watt')
for i, item in enumerate(hardware):
    print(f'Use {int(optima[i])} {item}')


