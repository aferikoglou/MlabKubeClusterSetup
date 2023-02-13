#!/usr/bin/python3

import json
import argparse
import matplotlib.pyplot as plt
from utils.utils import find_max_id

import matplotlib.pyplot as plt
import pandas as pd
import os

def itemgetter(x: tuple):
    if '_' in x[0]:
        a = x[0].split('_')[0]
        b = x[0].split('_')[1]
        return (b, a)
    return x[0]

parser = argparse.ArgumentParser(
    description='Create barplots from summarized metrics')
parser.add_argument(
    '-i',
    action='store',
    required=True,
    help="Path to summary file"
)
parser.add_argument(
    '-o',
    action='store',
    required=False,
    help="Path to save output figures"
)
parser.add_argument(
    '-x-axis',
    action='store',
    choices=["configuration", "engine"],
    required=True,
    help="Defines what should be depicted in x axis"
)
parser.add_argument(
    '-height',
    action='store',
    default=8,
    help="Barplot's height"
)
parser.add_argument(
    '-width',
    action='store',
    default=12,
    help="Barplot's width"
)
args = parser.parse_args()

mlperflogs_df = pd.read_csv(args.i, sep="\t")
dirname, _ = os.path.split(os.path.abspath(__file__))

out_path = args.o if args.o is not None else os.path.join(dirname, "barplots")
experiment = args.i.split("/")[-1].split(".")[0]
out_path = os.path.join(out_path, experiment)
out_path = os.path.join(out_path, str(find_max_id(out_path, "")))
if not os.path.exists(out_path):
    os.makedirs(out_path)

if args.x_axis == "engine":
    with open(os.path.join(dirname, "data/abbreviated_pod_names.json")) as f:
        abbreviated_pod_names = json.loads(f.read())

benchmarks_count = {}
for column in mlperflogs_df.columns:
    for row in range(len(mlperflogs_df)):
        name = mlperflogs_df.loc[row, 'name']
        if name == "total":
            continue
        benchmark = mlperflogs_df.loc[row, 'benchmark']
        if "dcgm" in args.i:
            if column != "mean_value":
                continue
            metric_name = mlperflogs_df.loc[row, 'metric_name']
        else:
            metric_name = column

        if name not in benchmarks_count:
            benchmarks_count[name] = {}
        if benchmark not in benchmarks_count[name]:
            benchmarks_count[name][benchmark] = {}
        if metric_name not in benchmarks_count[name][benchmark]:
            benchmarks_count[name][benchmark][metric_name] = 1
        else:
            benchmarks_count[name][benchmark][metric_name] += 1

d = {}
for column in mlperflogs_df.columns:
    if column in ['name', 'benchmark', 'gpu', 'model_name', 'metric_name', 'variance', 'scenario', 'mAP', 'timestamp', 'gpu_profile', 'gpu_id', "max_value", "min_value"]:
        continue
    for row in range(len(mlperflogs_df)):
        name = mlperflogs_df.loc[row, 'name']
        if name == "total":
            continue
        benchmark = mlperflogs_df.loc[row, 'benchmark']
        metric_name = mlperflogs_df.loc[row,
                                        'metric_name'] if "dcgm" in args.i else column
        
        key, x_axis = (benchmark, name) if args.x_axis == "engine" else (name, benchmark)
        if args.x_axis == "engine":
            x_axis = abbreviated_pod_names[x_axis]

        if key not in d:
            d[key] = {}
        if metric_name not in d[key]:
            d[key][metric_name] = {'x': [], 'y': []}

        if x_axis not in d[key][metric_name]['x']:
            d[key][metric_name]['x'].append(x_axis)
            try:
                d[key][metric_name]['y'].append(round(float(
                    mlperflogs_df.loc[row, column]) / float(benchmarks_count[name][benchmark][metric_name]), 4))
            except:
                d[key][metric_name]['y'].append(float(0))
        else:
            i = d[key][metric_name]['x'].index(x_axis)
            try:
                d[key][metric_name]['y'][i] += round(float(mlperflogs_df.loc[row, column]) / float(
                    benchmarks_count[name][benchmark][metric_name]), 4)
            except:
                pass

for k, v in d.items():
    print()
    print(k)

    outfile = os.path.join(out_path, k)
    if not os.path.exists(outfile):
        os.makedirs(outfile)
    for k1, v1 in v.items():
        print(k1)
        data = list([(a, b) for a, b in zip(v1['x'], v1['y'])])
        data = sorted(data, key=itemgetter) if args.x_axis == "configuration" else sorted(data)
        X = [x[0] for x in data]
        Y = [x[1] for x in data]
        
        plt.figure(figsize=(args.width, args.height))
        plt.bar(X, Y)
        plt.ylabel(k1)
        plt.title(k)
        plt.tight_layout()
        plt.savefig(os.path.join(outfile, k1 + '.png'))
        plt.clf()
