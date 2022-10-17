#!/usr/bin/python3

import argparse
import logging
import subprocess
import os
from itertools import combinations

def run_combinations(pods, size, pods_dir, save_dir, script, logger):
    for combo in combinations(pods, size,):
        print(str(combo))
        l = list(combo)
        for file in os.listdir(pods_dir):
            for i, c in enumerate(l):
                os.replace(os.path.join(pods_dir, file), os.path.join(save_dir, file))
                del l[i]
                break

        if len(os.listdir(pods_dir)) != size:
            l = list(combo)
            for file in os.listdir(save_dir):
                for i, c in enumerate(l):
                    if c in file:
                        os.replace(os.path.join(save_dir, file), os.path.join(pods_dir, file))
                        del l[i]
                        break
        
        if len(os.listdir(pods_dir)) != size:
            msg = "Pods for combination {" + ",".join(list(combo)) + "} unavailable, skipping..."
            logger.warning()
            continue

        p = subprocess.run([script, "-url", "http://192.168.1.236:30090/", "-c", "/home/dimgatz/.kube/config", "-a", "-s", "0", "-b", str(len(combo)), "--benchmark", ",".join(combo), "--tsv-out", "combinations.ods"])

    for file in os.listdir(save_dir):
        os.replace(os.path.join(save_dir, file), os.path.join(pods_dir, file))
                        

parser = argparse.ArgumentParser(description='Execute benchmarks for all combinations of mlperf_gpu_pods. Unused pods for each benchmark are temporarily saved in ~/.benchmarks/save/.')
parser.add_argument('--size', action='store', type=int, required=True, help='Combination size')
args = parser.parse_args()

logger = logging.getLogger('logger')

home = os.getenv("HOME")
save_dir = os.path.join(home, ".benchmarks", "save")
dirname, _ = os.path.split(os.path.abspath(__file__))
pods_dir = os.path.join(dirname, "mlperf_gpu_pods")

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

pods = [
    "onnx_mobilenet",
    "onnx_resnet50",
    "onnx_ssd_mobilenet",
    "tensorflow_mobilenet",
    "tensorflow_resnet50",
    "tensorflow_ssd_mobilenet",
    "tflite_mobilenet",
]
script = os.path.join(dirname, "benchmark_gpu_pods.sh")
run_combinations(pods, args.size, pods_dir, save_dir, script, logger)
