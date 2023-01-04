#!/usr/bin/python3

import matplotlib.pyplot as plt
import os
import re
import argparse
import pandas as pd
import json

parser = argparse.ArgumentParser(
    description='Plot metrics of each pod when colocated with every other pod')
parser.add_argument(
    '-i',
    action='store',
    required=True,
    help="Path to input dataset"
)
parser.add_argument(
    '--out',
    type=str,
    required=False,
    help="Path to output folder"
)
parser.add_argument(
    '--height',
    type=int,
    default=5,
    help="Height of figures"
)
parser.add_argument(
    '--width',
    type=int,
    default=12,
    help="Width of figures"
)

args = parser.parse_args()

regex = re.compile(r'^(\w+_)*\d+,\d+$')
metrics = pd.read_csv(args.i, sep="\t")

dirname, _ = os.path.split(os.path.abspath(__file__))
out_path = args.out if args.out is not None else os.path.join(
    dirname, 'interference')
if not os.path.exists(out_path):
    os.makedirs(out_path)
pods_file = os.path.join(dirname, 'data', 'pods.json')
with open(pods_file, "r") as f:
    pods = json.loads(f.read())

d = {'A30': {}, 'V100': {}}
for row in range(len(metrics)):
    
    if not regex.match(metrics.loc[row, "benchmark"]):
        continue
    key = 'V100' if 'V100' in metrics.loc[row, "benchmark"] else 'A30'
    for column in metrics.columns:
        if column in [
            "name", 
            "benchmark", 
            "experiment", 
            "model_name", 
            "gpu", 
            "scenario", 
            "mAP", 
            "gpu_profile", 
            "gpu_id", 
            "timestamp"
        ]:
            continue

        benchmark = re.findall(r'\d+,\d+$', metrics.loc[row, 'benchmark'])[0]
        
        first = str((int(benchmark.split(',')[0]) - 1) // 3 + 1)
        second = str((int(benchmark.split(',')[1]) - 1) // 3 + 1)
        pod = pods[first] \
            if pods[first] not in metrics.loc[row, 'name'] \
                else pods[second]
        name = pods[first] \
            if pods[first] in metrics.loc[row, 'name'] \
                else pods[second]
        if name not in d[key].keys():
            d[key][name] = {}
        if column not in d[key][name]:
            d[key][name][column] = {'x': [pod],
                                    'y': [metrics.loc[row, column]]}
        else:
            d[key][name][column]['x'].append(pod)
            d[key][name][column]['y'].append(metrics.loc[row, column])

for device in d.keys():
    for pod in d[device].keys():
        tmp_outpath = os.path.join(out_path, device, pod)
        if not os.path.exists(tmp_outpath):
            os.makedirs(tmp_outpath)
        for column in d[device][pod].keys():
            print(device, pod, column)
            fig, ax = plt.subplots(figsize=(args.width, args.height))
            
            count = {}
            X = d[device][pod][column]['x']
            Y = d[device][pod][column]['y']
            for i in range(len(X)):
                if X[i] not in count:
                    count[X[i]] = 1
                else:
                     count[X[i]] += 1
            data = {}
            for i in range(len(X)):
                if X[i] not in data:
                    data[X[i]] = Y[i] / count[X[i]]
                else:
                     data[X[i]] += Y[i] / count[X[i]]

            ax.bar(data.keys(), data.values())
            plt.ylabel(column)
            # ax.xaxis.set_tick_params(labelsize=4)
            fig.tight_layout()
            fig.savefig(os.path.join(tmp_outpath, column + '.png'))
            fig.clf()
