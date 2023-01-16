#!/usr/bin/python3

import argparse
import os
import pandas as pd
import sys
import re
import json

parser = argparse.ArgumentParser(
    description='Create dataset from summarized metrics')
parser.add_argument(
    '-i',
    action='store',
    required=True,
    help="Path to input summary"
)
parser.add_argument(
    '--out',
    type=str,
    required=False,
    help="Path to output dataset"
)

args = parser.parse_args()

dirname, _ = os.path.split(os.path.abspath(__file__))
filepath = os.path.join(dirname, "dataset")
units_file = os.path.join(dirname, "data/units.json")
if not os.path.exists(filepath):
    os.makedirs(filepath)
tsv_path = args.out if (args.out is not None) \
    else os.path.join(
        filepath,
        "dataset.ods"
    )
if os.path.isdir(tsv_path):
    "-out is a directory"
    sys.exit(-1)
try:
    experiment = "_".join(args.i.split("/")[-1].split(".")[0].split("_")[3:])
except:
    experiment = ""
type = "dcgm" if "dcgm" in args.i else "mlperf"
columns = [
    "name",
    "timestamp",
    "benchmark",
    "experiment",
    "model_name",
    "gpu_profile",
    "gpu",
    "gpu_id",
    "scenario",
    "qps",
    "mean",
    "time",
    "queries",
    "system_latency",
    "execution_speed",
    "50",
    "80",
    "90",
    "95",
    "99",
    "99.9",
    # 'DCGM_FI_DEV_FB_FREE',
    # 'DCGM_FI_DEV_FB_USED',
    # 'DCGM_FI_DEV_GPU_TEMP',
    # 'DCGM_FI_DEV_MEMORY_TEMP',
    # 'DCGM_FI_DEV_MEM_COPY_UTIL',
    # 'DCGM_FI_DEV_POWER_USAGE',
    # 'DCGM_FI_DEV_TOTAL_ENERGY_CONSUMPTION',
    # 'DCGM_FI_PROF_DRAM_ACTIVE',
    # 'DCGM_FI_PROF_GR_ENGINE_ACTIVE',
    # 'DCGM_FI_PROF_PCIE_RX_BYTES',
    # 'DCGM_FI_PROF_PCIE_TX_BYTES',
]

with open(units_file, "r") as f:
    units = json.loads(f.read())
columns.extend(list([f'{k} {v}' for k, v in units.items()]))

if os.path.exists(tsv_path):
    df = pd.read_csv(tsv_path, sep="\t")
else:
    df = pd.DataFrame(
        [],
        columns=columns)
metrics_tmp = pd.read_csv(args.i, sep="\t")
for row in range(len(metrics_tmp)):
    name = metrics_tmp.loc[row, "name"]
    if "total" in name:
        continue
    benchmark = metrics_tmp.loc[row, "benchmark"]
    if df.loc[
        (df["name"] == name) &
        (df["benchmark"] == benchmark) &
        (df["experiment"] == experiment)
    ].empty:
        s = pd.Series([None] * len(df.columns), index=df.columns)
        df.loc[len(df.index)] = s
        df.loc[len(df.index) - 1, "name"] = name
        df.loc[len(df.index) - 1, "benchmark"] = benchmark
        df.loc[len(df.index) - 1, "experiment"] = experiment
    if type == "dcgm":
        column = metrics_tmp.loc[row, "metric_name"]
        if not column in columns:
            continue
        df.loc[
            (df["name"] == name) &
            (df["benchmark"] == benchmark) &
            (df["experiment"] == experiment),
            column
        ] = metrics_tmp.loc[row, "mean_value"]
        for metric in ["model_name", "gpu", "gpu_id", "timestamp", "gpu_profile"]:
            df.loc[
                (df["name"] == name) &
                (df["benchmark"] == benchmark) &
                (df["experiment"] == experiment),
                metric
            ] = metrics_tmp.loc[row, metric]
    else:
        for column in metrics_tmp.columns:
            if re.match("\d+\.\d+", column) and column != "99.9":
                df_column = column.split(".")[0]
            else:
                df_column = column
            if column in ["name", "benchmark"] or not df_column in columns:
                continue
            df.loc[
                (df["name"] == name) &
                (df["benchmark"] == benchmark) &
                (df["experiment"] == experiment),
                df_column
            ] = metrics_tmp.loc[row, column]

df.to_csv(tsv_path, mode='w', index=False, sep="\t")
