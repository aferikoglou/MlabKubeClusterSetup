#!/usr/bin/python3

from collections import OrderedDict
import numpy as np
from utils.utils import find_max_id
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse

parser = argparse.ArgumentParser(description='Parse metrics of all benchmarks into a single tsv file.')
parser.add_argument(
    '-i', 
    action='store', 
    required=True ,  
    help="Path to input mlperf logs."
)
parser.add_argument(
    '--out', 
    type=str, 
    required=False,
    help="Path to output folder. \
        If not provided heatmaps will be saved at \
            /mlab-k8s-cluster-setup/prom_metrics_cli/plot/figures/heatmaps/mlperf_logs"
)

args = parser.parse_args()

if args.out is not None and os.path.isfile(args.out):
    print("-i should be a directory")
    sys.exit(0)

mlperflogs_df = pd.read_csv(args.i, sep="\t")
dirname, _ = os.path.split(os.path.abspath(__file__))

if args.out is not None:
    filepath = args.out
else:
    filepath = os.path.join(dirname, "heatmaps", "mlperf_logs")

if not os.path.exists(filepath):
    os.makedirs(filepath)

benchmark = "_".join(args.i.split("/")[-1].split(".")[0].split("_")[3:])
if benchmark == "":
    benchmark = "out"
benchmark_dir = os.path.join(filepath, benchmark)
if not os.path.exists(benchmark_dir):
    os.makedirs(benchmark_dir)
max_id_dir = os.path.join(benchmark, str(find_max_id(benchmark_dir, "")))
out_path = os.path.join(filepath, max_id_dir)
if not os.path.exists(out_path):
    os.makedirs(out_path)

benchmarks_count = {}
for row in range(len(mlperflogs_df)):
    name = mlperflogs_df.loc[row, 'name']
    benchmark = mlperflogs_df.loc[row, 'benchmark']
    if name not in benchmarks_count:
        benchmarks_count[name] = {}
    if benchmark not in benchmarks_count[name]:
        benchmarks_count[name][benchmark] = 1
    else:
        benchmarks_count[name][benchmark] += 1

d = {}
for column in mlperflogs_df.columns:
    if column in ['name', 'benchmark', 'scenario', ]:
        continue
    d[column] = {}
    for row in range(len(mlperflogs_df)):
        if np.isnan(mlperflogs_df.loc[row, column]):
            continue
        name = mlperflogs_df.loc[row, 'name']
        benchmark = mlperflogs_df.loc[row, 'benchmark']
        if benchmark not in d[column]:
            d[column][benchmark] = {}
        if name not in d[column][benchmark]:
            d[column][benchmark][name] = round(float(mlperflogs_df.loc[row, column]) / float(benchmarks_count[name][benchmark]), 4)
        else:
            d[column][benchmark][name] += round(float(mlperflogs_df.loc[row, column]) / float(benchmarks_count[name][benchmark]), 4)

for k, v in d.items():
    if k == "mAP":
        continue
    d[k] = pd.DataFrame(OrderedDict(sorted(d[k].items())))

    ax = sns.heatmap(
        d[k],
        annot=True
    )

    plt.tight_layout()
    if k in ['50.0', '80.0', '90.0', '95.0', '99.0', '99.9']:
        plt.savefig(out_path + "/" + k + '-percentile.png')
    else:
        plt.savefig(out_path + "/" + k + '.png')
    plt.figure().clear()
