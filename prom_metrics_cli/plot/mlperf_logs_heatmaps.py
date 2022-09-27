#!/usr/bin/python3

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
for column in mlperflogs_df.columns:
    if column in ['name', 'benchmark', 'scenario', ]:
        continue
    d[column] = {}
    for row in range(len(mlperflogs_df)):
        name = mlperflogs_df.loc[row, 'name']
        benchmark = mlperflogs_df.loc[row, 'benchmark']
        if benchmark not in d[column]:
            d[column][benchmark] = {}
        d[column][benchmark][name] = mlperflogs_df.loc[row, column]

new_d = {}
for k, v in d.items():
    for k1, v1 in v.items():
        for k2, v2 in v1.items():
            if k == "tiles":
                g = [x.split(':') for x in v2.split(',')]
                for x1, x2 in g:
                    if x1 not in new_d:
                        new_d[x1] = {}
                    if k1 not in new_d[x1]:
                        new_d[x1][k1] = {}

                    new_d[x1][k1][k2] = float(x2)
            elif isinstance(v2, str) and v2.endswith('%'):
                d[k][k1][k2] = float(v2.strip('%')) / 100

            if k != 'tiles':
                if d[k][k1][k2] is not None:
                    d[k][k1][k2] = float(d[k][k1][k2])
                else:
                    d[k][k1][k2] = float(0)

del d['tiles']
d.update(new_d)
for k, v in d.items():
    if k == "mAP":
        continue
    d[k] = pd.DataFrame(d[k])

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
