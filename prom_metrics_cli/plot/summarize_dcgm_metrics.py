#!/usr/bin/python3

import pandas as pd
from utils.utils import find_max_id
import os 
import argparse

parser = argparse.ArgumentParser(description='Parse metrics of all benchmarks into a single tsv file.')
parser.add_argument(
    '-i', 
    action='store', 
    required=True ,  
    help="Path to input log files/figures."
)
parser.add_argument(
    '--tsv-out', 
    type=str, 
    required=False,
    help="Tsv output's path. \
        If not provided summary will be saved at \
            /mlab-k8s-cluster-setup/prom_metrics_cli/plot/summary/summary.tsv"
)
parser.add_argument(
    '--benchmark', 
    type=str, 
    required=True,
    help="Name of the benchmark"
)

args = parser.parse_args()

dirname, _ = os.path.split(os.path.abspath(__file__))
filepath = os.path.join(dirname, "summary")
if not os.path.exists(filepath):
    os.makedirs(filepath)
tsv_path = args.tsv_out if (args.tsv_out is not None) \
    else os.path.join(
        filepath,
        "dcgm_summary_" + str(find_max_id(filepath, "summary")) + ".ods"
    )
header = False if (os.path.exists(tsv_path)) else True


# Count benchmarks with common model/backend according to their names and metric_names
benchmarks = os.listdir(args.i)
benchmarks_count = {}
for dir in benchmarks:
    benchmark_dir = os.path.join(args.i, dir)
    files = os.listdir(benchmark_dir)
    for file in files:
        if file.endswith(".tsv") and not file.endswith("logs.tsv"):
            metrics_tmp = pd.read_csv(os.path.join(benchmark_dir, file), sep="\t")
            for row in range(len(metrics_tmp)):
                name_list = metrics_tmp.loc[row, "name"].replace('-', '_').split('_')
                if name_list[0] == "total":
                    name = "total"
                else:
                    name = "_".join(name_list[2:5]) \
                    if "ssd" in metrics_tmp.loc[row, "name"] \
                    else "_".join(name_list[2:4])
                metric_name = metrics_tmp.loc[row, "metric_name"]
                if name not in benchmarks_count:
                    benchmarks_count[name] = {}
                if metric_name not in benchmarks_count[name]:
                    benchmarks_count[name][metric_name] = 1
                else:
                    benchmarks_count[name][metric_name] += 1
            break

df = pd.DataFrame([], columns=["name", "benchmark", "gpu", "model_name", "metric_name", "mean_value", "variance"])
metrics = {}
for dir in benchmarks:
    benchmark_dir = os.path.join(args.i, dir)
    files = os.listdir(benchmark_dir)
    for file in files:
        if file.endswith(".tsv") and not file.endswith("logs.tsv"):
            metrics_tmp = pd.read_csv(os.path.join(benchmark_dir, file), sep="\t")
            for row in range(len(metrics_tmp)):
                if metrics_tmp.loc[row, "name"] is None or metrics_tmp.loc[row, "name"] == "":
                    continue
                name_list = metrics_tmp.loc[row, "name"].replace('-', '_').split('_')
                if name_list[0] == "total": name = "total"
                else:
                    name = "_".join(name_list[2:5]) \
                    if "ssd" in metrics_tmp.loc[row, "name"] \
                    else "_".join(name_list[2:4])
                metric_name = metrics_tmp.loc[row, "metric_name"]

                if not df.loc[(df["name"] == name) & (df["metric_name"] == metric_name)].empty:
                    for column in metrics_tmp.columns:
                        if column in ["name", "gpu", "model_name", "metric_name"]:
                            continue
                        try:
                            df.loc[(df["name"] == name) & (df["metric_name"] == metric_name), column] += \
                                float(metrics_tmp.loc[row, column]) / benchmarks_count[name][metric_name]
                        except:
                            pass
                else:
                    metrics_tmp.loc[row, "name"] = name
                    df.loc[len(df.index)] = metrics_tmp.loc[row]
                    try:
                        df.loc[len(df.index) - 1, "mean_value"] = df.loc[len(df.index) - 1, "mean_value"] / benchmarks_count[name][metric_name]
                    except:
                        pass
            break

df['benchmark'] = [args.benchmark] * len(df)

df.to_csv(tsv_path, mode='a', index=False, header=header, sep="\t")
