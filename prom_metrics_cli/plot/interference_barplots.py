#!/usr/bin/python3

import matplotlib.pyplot as plt
import os
import re
import argparse
import pandas as pd

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

pods = {
    '1': "onnx_mobilenet",
    '2': "onnx_resnet50",
    '3': "onnx_ssd_mobilenet",
    '4': "tensorflow_mobilenet",
    '5': "tensorflow_resnet50",
    '6': "tensorflow_ssd_mobilenet",
    '7': "tflite_mobilenet",
}

regex = re.compile(r'^(\w_)*\d,\d$')
metrics = pd.read_csv(args.i, sep="\t")

dirname, _ = os.path.split(os.path.abspath(__file__))
out_path = args.out if args.out is not None else os.path.join(
    dirname, 'interference')
if not os.path.exists(out_path):
    os.makedirs(out_path)

# karta -> pod -> metrikh -> suntopo8ethmena pods -> {x: [], y: []}
d = {'A30': {}, 'V100': {}}
for row in range(len(metrics)):
    if not regex.match(metrics.loc[row, "benchmark"]):
        continue
    key = 'V100' if 'V100' in metrics.loc[row, "benchmark"] else 'A30'
    for column in metrics.columns:
        if column in ["name", "benchmark", "experiment", "model_name", "gpu", "scenario", "mAP"]:
            continue

        benchmark = re.findall(r'\d,\d$', metrics.loc[row, 'benchmark'])[0]
        name = metrics.loc[row, 'name']
        pod = pods[benchmark.split(',')[0]] if pods[benchmark.split(
            ',')[0]] != metrics.loc[row, 'name'] else pods[benchmark.split(',')[1]]
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
            ax.bar(d[device][pod][column]['x'],
                   d[device][pod][column]['y'])
            plt.ylabel(column)
            fig.tight_layout()
            fig.savefig(os.path.join(tmp_outpath, column + '.png'))
            fig.clf()
