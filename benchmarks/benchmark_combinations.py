#!/usr/bin/python3

import time
import argparse
import logging
import subprocess
import os
from itertools import combinations
import sys
dirname, _ = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirname, ".."))
from prom_metrics_cli.plot.utils import utils

def run_combinations(pods, size, pods_dir, save_dir, script, url, config, sleep, tsv_out, checkpoint, logger):
    counter = 1
    pods_dict = {}
    dirname, _ = os.path.split(os.path.abspath(__file__))
    beep = lambda x: os.system("echo -n '\a';sleep 0.1;" * x)
    
    for pod in pods:
        if pod in pods_dict:
            continue
        pods_dict[pod] = counter
        counter += 1
    
    combos = list(combinations(pods, size,))
    if checkpoint != "": 
        try:
            checkpoint = checkpoint.split(',')
            new_checkpoint = []
            for c in checkpoint:
                new_checkpoint.extend([i for i in pods_dict if pods_dict[i] == int(c)])
            checkpoint = combos.index(tuple(new_checkpoint))
            combos = [x for x in combos if combos.index(x) >= checkpoint]
        except:
            print("Checkpoint should be a comma seperated string containing pods' indices in ascending order")
            sys.exit(0)

    for combo in combos:
        print(str(combo))
        for file in os.listdir(pods_dir):
            if any([x in file for x in combo]):
                continue
            os.replace(os.path.join(pods_dir, file), os.path.join(save_dir, file))
                    
        if len(os.listdir(pods_dir)) != size:
            for file in os.listdir(save_dir):
                if any([x in file for x in combo]):
                    os.replace(os.path.join(save_dir, file), os.path.join(pods_dir, file))
                
        if len(os.listdir(pods_dir)) != size:
            msg = "Pods for combination {" + ",".join(list(combo)) + "} unavailable, skipping..."
            logger.warning(msg)
            continue

        benchmark = ",".join([str(pods_dict[x]) for x in combo])
        base_out_path = f"../prom_metrics_cli/plot/figures/combinations/({benchmark})"
        if not os.path.exists(base_out_path):
            os.makedirs(base_out_path)
        out_path = os.path.join(dirname, base_out_path, str(utils.find_max_id("/".join(base_out_path.split("/")[:-1]), f"({benchmark})")))
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        subprocess.run([script, "-url", url, "-c", config, "-a", "-s", str(sleep), "-b", str(size), "--benchmark", benchmark, "--tsv-out", tsv_out, "-o", out_path, "--tsv"])
        # beep(4)

    for file in os.listdir(save_dir):
        os.replace(os.path.join(save_dir, file), os.path.join(pods_dir, file))
                        

parser = argparse.ArgumentParser(description='Execute benchmarks for all combinations of mlperf_gpu_pods. Unused pods for each benchmark are temporarily saved in ~/.benchmarks/save/.')
parser.add_argument('--size', action='store', type=int, required=True, help='Combination size')
parser.add_argument('--url', action='store', type=str, default="http://192.168.1.236:30090/", help='Prometheus url')
parser.add_argument('--config', action='store', type=str, default="/home/dimgatz/.kube/config", help='Kubernetes configuration file path')
parser.add_argument('--sleep', action='store', type=int, default=0, help='Sleep interval between benchmarks')
parser.add_argument('--tsv-out', action='store', type=str, default="combinations.ods", help='Output tsv file name')
parser.add_argument('--checkpoint', action='store', type=str, default="", help="Comma seperated pods' indices in ascending order, empty to start from beggining")
args = parser.parse_args()

logger = logging.getLogger('logger')

home = os.getenv("HOME")
save_dir = os.path.join(home, ".benchmarks", "save")
dirname, _ = os.path.split(os.path.abspath(__file__))
pods_dir = os.path.join(dirname, "mlperf_gpu_pods")

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

pods_list = [
    "onnx_mobilenet",
    "onnx_resnet50",
    "onnx_ssd_mobilenet",
    "tensorflow_mobilenet",
    "tensorflow_resnet50",
    "tensorflow_ssd_mobilenet",
    "tflite_mobilenet",
]
script = os.path.join(dirname, "benchmark_gpu_pods.sh")
run_combinations(pods_list, args.size, pods_dir, save_dir, script, args.url, args.config, args.sleep, args.tsv_out, args.checkpoint, logger)
