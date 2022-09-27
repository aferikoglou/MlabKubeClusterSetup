#!/usr/bin/python3

from utils.utils import find_max_id
import sys
import argparse
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os

parser = argparse.ArgumentParser(description='Parse metrics of all benchmarks into a single tsv file.')
parser.add_argument(
    '-i', 
    action='store', 
    required=True ,  
    help="Path to input dcgm metrics."
)
parser.add_argument(
    '--tsv-out', 
    type=str, 
    required=False,
    help="Path to output folder. \
        If not provided heatmaps will be saved at \
            /mlab-k8s-cluster-setup/prom_metrics_cli/plot/figures/heatmaps"
)

args = parser.parse_args()

if args.tsv_out is not None and os.path.isfile(args.tsv_out):
    print("-i should be a directory")
    sys.exit(0)

mlperflogs_df = pd.read_csv(args.i, sep="\t")
dirname, _ = os.path.split(os.path.abspath(__file__))

if args.tsv_out is not None:
    out_path = args.tsv_out  
else:
    filepath = os.path.join(dirname, "figures", "heatmaps")

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    max_id_dir = "out_" + str(find_max_id(filepath, "out"))
    out_path = os.path.join(filepath, max_id_dir)
    os.makedirs(out_path)


d = {}
for row in range(len(mlperflogs_df)):
    name = mlperflogs_df.loc[row, 'name']
    benchmark = mlperflogs_df.loc[row, 'benchmark']
    column = mlperflogs_df.loc[row, 'metric_name']
    if column not in d:
        d[column] = {}
    if benchmark not in d[column]:
        d[column][benchmark] = {}

    d[column][benchmark][name] = mlperflogs_df.loc[row, 'mean_value']

for k, v in d.items():
    for k1, v1 in v.items():
        for k2, v2 in v1.items():
            if d[k][k1][k2] is not None:
                d[k][k1][k2] = float(d[k][k1][k2])
            else:
                d[k][k1][k2] = float(0)

for k, v in d.items():
    d[k] = pd.DataFrame(d[k])
    
    ax = sns.heatmap(
        d[k],
        annot=True
    )

    plt.tight_layout()
    plt.savefig(out_path + "/" + k + '.png')
    plt.figure().clear()
