#!/usr/bin/python3

import atexit
import argparse
import logging
import subprocess
import os
from itertools import combinations
import sys
dirname, _ = os.path.split(os.path.abspath(__file__))
sys.path.append(os.path.join(dirname, ".."))
from prom_metrics_cli.plot.utils import utils
    
def handler():
    global logs_file, save, succeeded, save_dir, pods_dir
    for file in os.listdir(save_dir):
        os.replace(os.path.join(save_dir, file), os.path.join(pods_dir, file))

    if succeeded:
        return
    with open(logs_file, "a") as f:
        f.write(f"{str(save)}\n")
    print(f"Script interrupted at benchmark: {save}\nCheckpoint saved at {logs_file}")


def run_combinations(
    pods, 
    size, 
    pods_dir, 
    save_dir, 
    script, 
    url, 
    config, 
    sleep, 
    tsv_out, 
    checkpoint, 
    restart, 
    notify, 
    logs_file,
    yaml,
    benchmark,
    filter,
    logger
):
    global succeeded, save
    counter = 1
    pods_dict = {}
    dirname, _ = os.path.split(os.path.abspath(__file__))
    if notify:
        beep = lambda x: os.system("echo -n '\a';sleep 0.1;" * x)
    
    for pod in pods:
        if pod in pods_dict:
            continue
        pods_dict[pod] = counter
        counter += 1
    
    if restart:
        with open(logs_file, "r") as f:
            checkpoint = f.readlines()[-1]

    if checkpoint != "":
        checkpoint = checkpoint.strip('\n').strip('(').strip(')').split(',')
        if checkpoint[-1] == "":
            checkpoint = checkpoint[:-1]
        for i in range(len(checkpoint)):
            checkpoint[i] = checkpoint[i].strip("'")
        size = len(checkpoint)
    

    combos = list(combinations(pods, size,))
    if checkpoint != "": 
        try:
            if not restart:
                new_checkpoint = []
                for c in checkpoint:
                    new_checkpoint.extend([i for i in pods_dict if pods_dict[i] == int(c)])
                checkpoint = new_checkpoint
            checkpoint = combos.index(tuple(checkpoint))
            combos = combos[checkpoint:]
        except:
            print("Checkpoint should be a comma seperated string containing pods' indices in ascending order")
            sys.exit(0)
    
    first = True
    for combo in combos:
        save = combo
        print(combo)
        
        if first:
            atexit.register(handler)
            first = False
        
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

        name = ",".join([str(pods_dict[x]) for x in combo]) \
            if benchmark is None else \
            benchmark + "_" + ",".join([str(pods_dict[x]) for x in combo])
            
        base_out_path = os.path.join(dirname, "../prom_metrics_cli/plot/figures/combinations", f"({name})")
        if not os.path.exists(base_out_path):
            os.makedirs(base_out_path)
        out_path = os.path.join(base_out_path, str(utils.find_max_id(base_out_path, '')))
        if not os.path.exists(out_path):
            os.makedirs(out_path)

        args = [
            script, 
            "-url", 
            url, 
            "-c", 
            config, 
            "-a", 
            "-s", 
            str(sleep), 
            "-b", 
            str(size), 
            "--benchmark", 
            name, 
            "--tsv-out", 
            tsv_out,
            "-o", 
            out_path, 
            "--tsv"
        ]
        if filter is not None:
            args.extend(["--filter", filter])
        if yaml is not None:
            args.extend(["--yaml", yaml])

        subprocess.run(args)
        if notify:
            beep(4)

    succeeded = True
                        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute benchmarks for all combinations of mlperf_gpu_pods. Unused pods for each benchmark are temporarily saved in ~/.benchmarks/save/.')
    parser.add_argument('--size', action='store', type=int, default=1, help='Combination size')
    parser.add_argument('--url', action='store', type=str, default="http://192.168.1.236:30090/", help='Prometheus url')
    parser.add_argument('--config', action='store', type=str, default="", help='Kubernetes configuration file path. Default = $HOME/.kube/config')
    parser.add_argument('--sleep', action='store', type=int, default=0, help='Sleep interval between benchmarks')
    parser.add_argument('--tsv-out', action='store', type=str, default="combinations.ods", help='Output tsv file name')
    parser.add_argument('--checkpoint', action='store', type=str, default="", help="Comma seperated pods' indices in ascending order, empty to start from beggining. Overrides --size")
    parser.add_argument('--notify', action='store_true', default=False, help="Get notified with a beep sound in the end of each benchmark")
    parser.add_argument('--restart', action='store_true', default=False, help="Restart benchmarks from last saved combination. Overrides --size and --checkpoint")
    parser.add_argument('--restore', action='store_true', default=False, help="Restore pods to pods' dir")
    parser.add_argument('--yaml', action='store', type=str, help="Path to yaml files. Default = ./mlperf_gpu_pods")
    parser.add_argument('--benchmark', action='store', type=str, required=False, help="Optional benchmark name")
    parser.add_argument('--filter', action='store', type=str, required=False, help="Json object used to filter out prometheus results")

    args = parser.parse_args()

    logger = logging.getLogger('logger')

    succeeded = False
    save = None
    home = os.getenv("HOME")
    save_dir = os.path.join(home, ".benchmarks", "save")
    save_dir = os.path.join(save_dir, utils.find_max_id(save_dir, ''))
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if os.path.isfile(save_dir):
        print("Save path is a file")
        sys.exit(0)
    dirname, _ = os.path.split(os.path.abspath(__file__))
    pods_dir = args.yaml if args.yaml is not None else os.path.join(dirname, "mlperf_gpu_pods/A30/1")
    logs_file = os.path.join(dirname, "combinations-checkpoint.txt")

    if args.config == "":
        args.config = os.path.join(home, ".kube/config")

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    if args.restore:
        for file in os.listdir(save_dir):
            os.replace(os.path.join(save_dir, file), os.path.join(pods_dir, file))
        sys.exit(0)

    pods_list = [
        "onnx_mobilenet",
        "onnx_resnet50",
        "onnx_ssd_mobilenet",
        "tensorflow_mobilenet",
        "tensorflow_resnet50",
        "tensorflow_ssd_mobilenet",
    ]
    script = os.path.join(dirname, "benchmark_gpu_pods.sh")

    run_combinations(
        pods_list, 
        args.size, 
        pods_dir, 
        save_dir, 
        script, 
        args.url, 
        args.config, 
        args.sleep, 
        args.tsv_out, 
        args.checkpoint, 
        args.restart, 
        args.notify, 
        logs_file, 
        args.yaml, 
        args.benchmark,
        args.filter,
        logger
    )
