#!/usr/bin/python3

import re
from utils.utils import strip_datetimes
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
            /mlab-k8s-cluster-setup/prom_metrics_cli/plot/summary/summary.ods"
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
        "mlperf_summary_" + str(find_max_id(filepath, "summary")) + ".ods"
    )
header = False if (os.path.exists(tsv_path)) else True

regex = re.compile(r'_\d$')

# Count benchmarks with common model/backend according to their names
benchmarks = os.listdir(args.i)
benchmarks_count = {}
total_benchmark_count = 0
for dir in benchmarks:
    benchmark_dir = os.path.join(args.i, dir)
    if os.path.isfile(benchmark_dir):
        continue
    files = os.listdir(benchmark_dir)
    for file in files:
        if file.endswith("logs.tsv"):
            metrics_tmp = pd.read_csv(os.path.join(benchmark_dir, file), sep="\t")
            name = metrics_tmp.loc[0, "name"].replace('-', '_')
            name = name.lower()
            if name == 'total':
                continue
            name = name.replace('mlperf_gpu_', '') \
                    .replace('a30', '') \
                    .replace('v100', '') \
                    .replace('k8s_aferik_gpu', '') \
                    .replace('k8s_aferik_gpu_a30', '')
            name = strip_datetimes(name).strip(' ').strip('_')
            name = re.sub(regex, '', name)
            total_benchmark_count += 1
            if name not in benchmarks_count:
                benchmarks_count[name] = 1
            else:
                benchmarks_count[name] += 1
                break

df = pd.DataFrame(
    [], 
    columns=[
        "name", 
        "benchmark",
        "scenario", 
        "qps", 
        "mean", 
        "time", 
        "queries", 
        "system_latency", 
        "execution_speed",
    ],
)
for dir in benchmarks:
    benchmark_dir = os.path.join(args.i, dir)
    if os.path.isfile(benchmark_dir):
        continue
    files = os.listdir(benchmark_dir)
    for file in files:
        if file.endswith("logs.tsv"):
            metrics_tmp = pd.read_csv(os.path.join(benchmark_dir, file), sep="\t")
            name = metrics_tmp.loc[0, "name"].replace('-', '_')
            name = name.lower()
            if name == 'total':
                name = 'total'
                metrics_tmp.loc[0, "name"] = name
                df.loc[len(df.index)] = metrics_tmp.loc[0]
                continue
            name = name.replace('mlperf_gpu_', '') \
                    .replace('a30', '') \
                    .replace('v100', '') \
                    .replace('k8s_aferik_gpu', '') \
                    .replace('k8s_aferik_gpu_a30', '')
            name = strip_datetimes(name).strip(' ').strip('_')
            name = re.sub(regex, '', name)

            if name in df["name"].values:
                for column in metrics_tmp.columns:
                    try:
                        if column == "qps":
                            df.loc[df['name'] == name, "qps"] += metrics_tmp.loc[0, "qps"]
                        elif column == "mean":
                            df.loc[df['name'] == name, "mean"] += \
                                float(metrics_tmp.loc[0, "mean"]) / benchmarks_count[name]
                        elif column == "time":
                            if metrics_tmp.loc[0, "time"] > df.loc[df['name'] == name, "time"].values[0]: 
                                df.loc[df['name'] == name, "time"] = metrics_tmp.loc[0, "time"]
                        elif column == "system_latency":
                            if metrics_tmp.loc[0, "system_latency"] > df.loc[df['name'] == name, "system_latency"].values[0]: 
                                df.loc[df['name'] == name, "system_latency"] = round(metrics_tmp.loc[0, "system_latency"], 4)
                        elif column == "acc":
                            df.loc[df['name'] == name, "acc"] += \
                                (float(metrics_tmp.loc[0, "acc"].strip('%')) / 100) / benchmarks_count[name]
                        elif column == "queries":
                            df.loc[df['name'] == name, "queries"] += metrics_tmp.loc[0, "queries"]
                        elif column == "tiles":
                            g = [x.split(':') for x in metrics_tmp.loc[0, "tiles"].split(',')]
                            tmp = {}
                            for x1, x2 in g: 
                                if x1 not in df.columns or df.loc[df['name'] == name, x1].isnull().values.any():
                                    df.loc[df['name'] == name, x1] = round(float(x2) / benchmarks_count[name], 4)
                                else:
                                    df.loc[df['name'] == name, x1] += round(float(x2) / benchmarks_count[name], 4)
                        elif column == "mAP":
                            df.loc[df['name'] == name, "mAP"] += \
                                (float(metrics_tmp.loc[0, "mAP"].strip('%')) / 100) / benchmarks_count[name]
                    except:
                        pass
            else:
                metrics_tmp.loc[0, "name"] = name
                df.loc[len(df.index)] = metrics_tmp.loc[0]
                try:
                    df.loc[len(df.index) - 1, "system_latency"] = round(df.loc[len(df.index) - 1, "system_latency"], 4)
                except:
                    pass
                try:
                    df.loc[len(df.index) - 1, "acc"] = \
                    (float(df.loc[len(df.index) - 1, "acc"].strip('%')) / 100) / benchmarks_count[name]
                except:
                    pass
                try:
                    df.loc[len(df.index) - 1, "mean"] = \
                    float(df.loc[len(df.index) - 1, "mean"]) / benchmarks_count[name]
                except:
                    pass
                try:
                    df.loc[len(df.index) - 1, "mAP"] = \
                        (float(df.loc[len(df.index) - 1, "mAP"].strip('%')) / 100) / benchmarks_count[name]
                except:
                    pass
                try:
                    g = [x.split(':') for x in metrics_tmp.loc[0, "tiles"].split(',')]
                    tmp = {}
                    for x1, x2 in g: 
                        if x1 not in df.columns or df.loc[df['name'] == name, x1].isnull().values.any():
                            df.loc[df['name'] == name, x1] = round(float(x2) / benchmarks_count[name], 4)
                        else:
                            df.loc[df['name'] == name, x1] += round(float(x2) / benchmarks_count[name], 4)
                except:
                    pass    
            break

df['benchmark'] = [args.benchmark] * len(df)
for row in range(len(df)):
    name = df.loc[row, 'name']
    if name == 'total':
        df.loc[row, 'execution_speed'] = round(total_benchmark_count / df.loc[row, 'system_latency'], 4)    
        continue
    df.loc[row, 'execution_speed'] = round(benchmarks_count[name] / df.loc[row, 'system_latency'], 4)

df.sort_values(by=['name'], inplace=True)
df.to_csv(tsv_path, mode='a', index=False, header=header, sep="\t")
