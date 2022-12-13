#!/usr/bin/python3

import os
import pandas as pd 
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(
    description='Create boxplots from dataset (only for configuration experiment)')
parser.add_argument(
    '-i',
    action='store',
    required=True,
    help="Path to dataset"
)
parser.add_argument(
    '-o',
    action='store',
    required=False,
    help="Path to save output figures"
)
parser.add_argument(
    '-e',
    action='store',
    required=False,
    help="Filter only samples with this experiment"
)

args = parser.parse_args()

dirname, _ = os.path.split(os.path.abspath(__file__))
out_path = args.o if args.o is not None else os.path.join(dirname, "boxplots")
dcgm_out = os.path.join(out_path, 'DCGM')
mlperf_out = os.path.join(out_path, 'mlperf')

metrics = pd.read_csv(args.i, sep='\t')
models = {
    'resnet50': {}, 
    'mobilenet': {}, 
    'ssd_mobilenet': {}
}
backends = {
    'tensorflow': {}, 
    'onnx': {}
}
for row in range(len(metrics)):
    if args.e is not None:
        if metrics.loc[row, 'experiment'] != args.e:
            continue
    name = metrics.loc[row, 'name']
    if 'ssd_mobilenet' in name:
        model = 'ssd_mobilenet'
    elif 'mobilenet' in name:
        model = 'mobilenet'
    elif 'resnet50' in name:
        model = 'resnet50'
    else:
        print('No valid model in name')
        continue
    if 'tensorflow' in name:
        backend = 'tensorflow'
    elif 'onnx' in name:
        backend = 'onnx'
    else:
        print('No valid backend in name')
        continue
    for column in metrics.columns:
        if column in ["name", "timestamp", "benchmark", "experiment", "model_name", "gpu_profile", "gpu", "scenario", "mAP"]:
            continue
        # Models
        if column not in models[model]:
            models[model][column] = {}
        if metrics.loc[row, 'benchmark'] not in models[model][column]:
            models[model][column][metrics.loc[row, 'benchmark']] = [metrics.loc[row, column]]
        else:
            models[model][column][metrics.loc[row, 'benchmark']].append(metrics.loc[row, column])

        # Backends
        if column not in backends[backend]:
            backends[backend][column] = {}
        if metrics.loc[row, 'benchmark'] not in backends[backend][column]:
            backends[backend][column][metrics.loc[row, 'benchmark']] = [metrics.loc[row, column]]
        else:
            backends[backend][column][metrics.loc[row, 'benchmark']].append(metrics.loc[row, column])

for model in models.keys():
    mlperf_out_total = os.path.join(mlperf_out, model)
    dcgm_out_total = os.path.join(dcgm_out, model)
    if not os.path.exists(dcgm_out_total):
        os.makedirs(dcgm_out_total)
    if not os.path.exists(mlperf_out_total):
        os.makedirs(mlperf_out_total)

    for column in models[model]:
        fig = plt.figure()
        plt.tight_layout()
        ax = fig.add_subplot()

        ax.boxplot(models[model][column].values())
        ax.set_xticklabels(models[model][column].keys())
        ax.set_ylabel(column)
        if 'DCGM' in column:
            plt.savefig(os.path.join(dcgm_out_total, f'{column}.png'))
        else:
            plt.savefig(os.path.join(mlperf_out_total, f'{column}.png'))
        plt.clf()

for backend in backends.keys():
    mlperf_out_total = os.path.join(mlperf_out, backend)
    dcgm_out_total = os.path.join(dcgm_out, backend)
    if not os.path.exists(dcgm_out_total):
        os.makedirs(dcgm_out_total)
    if not os.path.exists(mlperf_out_total):
        os.makedirs(mlperf_out_total)

    for column in backends[backend]:
        fig = plt.figure()
        plt.tight_layout()
        ax = fig.add_subplot()

        ax.boxplot(backends[backend][column].values())
        ax.set_xticklabels(backends[backend][column].keys())
        ax.set_ylabel(column)
        if 'DCGM' in column:
            plt.savefig(os.path.join(dcgm_out_total, f'{column}.png'))
        else:
            plt.savefig(os.path.join(mlperf_out_total, f'{column}.png'))
        plt.clf()
