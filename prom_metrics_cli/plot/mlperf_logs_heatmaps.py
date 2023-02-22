#!/usr/bin/python3

import json
from collections import OrderedDict
from utils.utils import find_max_id
import sys
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse


def itemgetter(x: tuple):
    if "_" in x[0]:
        a = x[0].split("_")[0]
        b = x[0].split("_")[1]
        return (b, a)
    return x[0]


parser = argparse.ArgumentParser(
    description="Parse metrics of all benchmarks into a single tsv file."
)
parser.add_argument(
    "-i", action="store", required=True, help="Path to input mlperf logs."
)
parser.add_argument(
    "--out",
    type=str,
    required=False,
    help="Path to output folder. \
        If not provided heatmaps will be saved at \
            /mlab-k8s-cluster-setup/prom_metrics_cli/plot/figures/heatmaps/mlperf_logs",
)
parser.add_argument(
    "-a",
    action="store_true",
    default=False,
    help="If defined annotations will be included in heatmaps",
)
parser.add_argument("-height", type=int, default=6, help="Figures' height")
parser.add_argument("-width", type=int, default=10, help="Figures' width")

args = parser.parse_args()

if args.out is not None and os.path.isfile(args.out):
    print("-i should be a directory")
    sys.exit(0)

mlperflogs_df = pd.read_csv(args.i, sep="\t")
dirname, _ = os.path.split(os.path.abspath(__file__))
pods_file = os.path.join(dirname, "data/abbreviated_pod_names.json")
with open(pods_file, "r") as f:
    pods_dict = json.loads(f.read())

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
    name = mlperflogs_df.loc[row, "name"]
    benchmark = mlperflogs_df.loc[row, "benchmark"]
    if name not in benchmarks_count:
        benchmarks_count[name] = {}
    if benchmark not in benchmarks_count[name]:
        benchmarks_count[name][benchmark] = 1
    else:
        benchmarks_count[name][benchmark] += 1

d = {}
for column in mlperflogs_df.columns:
    if column in ["name", "timestamp", "benchmark", "scenario", "mAP"]:
        continue
    d[column] = {}
    for row in range(len(mlperflogs_df)):
        if pd.isnull(mlperflogs_df.loc[row, column]):
            continue
        name = mlperflogs_df.loc[row, "name"]
        if "total" in name:
            continue
        benchmark = mlperflogs_df.loc[row, "benchmark"]
        if benchmark not in d[column]:
            d[column][benchmark] = {}
        if name not in d[column][benchmark]:
            d[column][benchmark][name] = round(
                float(mlperflogs_df.loc[row, column])
                / float(benchmarks_count[name][benchmark]),
                4,
            )
        else:
            d[column][benchmark][name] += round(
                float(mlperflogs_df.loc[row, column])
                / float(benchmarks_count[name][benchmark]),
                4,
            )


for k, v in d.items():
    stripped_names_dict = {}
    for k1 in d[k].keys():
        stripped_names_dict[k1] = {}
        for k2, v2 in d[k][k1].items():
            stripped_names_dict[k1][str(pods_dict[k2])] = v2
    d[k] = pd.DataFrame(
        OrderedDict(sorted(stripped_names_dict.items(), key=itemgetter))
    )

    try:
        sns.set(rc={"figure.figsize": (args.width, args.height)})
        ax = sns.heatmap(d[k], annot=args.a)

        plt.title(k)
        plt.tight_layout()
        if k in ["50.0", "80.0", "90.0", "95.0", "99.0", "99.9"]:
            plt.savefig(out_path + "/" + k + "-percentile.png")
        else:
            plt.savefig(out_path + "/" + k + ".png")
        plt.clf()
    except Exception as e:
        print(k, f"\n{d[k]}")
        print(e)
