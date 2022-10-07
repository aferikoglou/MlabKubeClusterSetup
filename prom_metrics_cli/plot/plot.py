#!/usr/bin/python3

from curses import noecho
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import argparse
import re
import sys
import logging
from utils.utils import write_tsv, find_max_id, validate_filename


parser = argparse.ArgumentParser(description='Parse matplotlib labels.')
parser.add_argument('-x', action='store', type=str,
                    help='xlabel')
parser.add_argument('-y', action='store', type=str,
                    help='ylabel')
parser.add_argument('-yf', action='store', type=str,
                    help='ylabel extracted from json field. Overrides -y argument')
parser.add_argument('-l', '--legend-list', nargs='+', default=[], 
help="Manually import a list of legends for matplotlib")
parser.add_argument('-f', action='store', help="Json field from which to extract legends")
parser.add_argument(
    '-o', 
    action='store', 
    required=True ,  
    help="Name of the output png. Name can only contain - _ :\
    or alphanumerics and can't start or end with - or _"
)
parser.add_argument(
    '--out-dir', 
    type=str, 
    default="",  
    help="Out files' directory."
)
parser.add_argument(
    '-filter', 
    action='store', 
    required=False,  
    help="Json string where keys correspond to json fields \
    and values correspond to the values you want to keep. Values can also be regex."
)
parser.add_argument(
    '--total', 
    action='store_true', 
    default=False,  
    help="Add all the metrics from the json object in a single diagram"
)
parser.add_argument('--linewidth', type=int, default = 1,  help="Plot's line's linewidth")
parser.add_argument('--figwidth', type=int, default = 10,  help="Figure's width")
parser.add_argument('--figheight', type=int, default = 10,  help="Figure's height")
parser.add_argument(
    '--tsv-out', 
    type=str, 
    required=False,  
    help="Tsv output's filename. If not specified -o argument will be used. \
    If --total is provided then --tsv-out will be ignored"
)

args = parser.parse_args()

if not validate_filename(args.o):
    logging.error("Filename validation failed, exiting")
    parser.print_help()
    sys.exit(1)


if args.tsv_out is not None and not validate_filename(args.tsv_out):
    logging.error("Filename validation failed, exiting")
    parser.print_help()
    sys.exit(1)

dirname, _ = os.path.split(os.path.abspath(__file__))
filepath = os.path.join(args.out_dir, args.o) if (args.out_dir is not None and len(args.out_dir) > 0) else os.path.join(dirname, "figures", args.o)
logs_filepath = os.path.join(filepath, "logs.txt")
tsv_name = args.tsv_out if (args.tsv_out is not None) else args.o
        
if args.filter is not None:
    try:
        filter = json.loads(args.filter)
    except:
        filter = None
        logging.warning("filter parameter is not json serializable, ignoring.")
else:
    filter = None

data = input()

try:
    data = json.loads(data)
except:
    data = "".join(data.split(" ")[2:])
    try:
        data = json.loads(data)
    except:
        data = input()
        try:
            data = json.loads(data)
        except:
            data = "".join(data.split(" ")[2:])
            try:
                data = json.loads(data)
            except:
                logging.error("Input data not json serializable")
                sys.exit(1)

lines = 0
plt.figure().set_figwidth(args.figwidth)
plt.figure().set_figheight(args.figheight)
gpus = []
model_names = []
pods = []
time_x = []
position_y = []
for i, result in enumerate(data["data"]["result"]):
    try:
        gpu = result["metric"]["gpu"]
    except:
        gpu = ""
    try:
        model_name = result["metric"]["modelName"]
    except:
        model_name = ""
    try:
        pod = result["metric"]["exported_pod"]
    except:
        pod = ""
    
    if args.total:
        gpus.append(gpu)
        model_names.append(model_name)
        pods.append(pod)

    if filter is not None:
        skip = False
    
        for k, v in filter.items():
            pattern = re.compile(v.replace('-', '_'))
            if k not in result["metric"].keys():
                logging.warning(f'{k} not in result dict, ignoring filter')
                continue

            if not re.search(pattern, result["metric"][k].replace('-', '_')):
                logging.warning(f'{v} not in "{k}", skipping result No.{str(i)}')
                skip = True
                break

        if skip:
            continue

    lines += 1

    time_x = []
    position_y = []
    if not args.total or i == 0:
        base = float(result["values"][0][0])
    
    for v in result["values"]:
        time_x.append(float(v[0]) - base)
        position_y.append(float(v[1]))

    plt.xlabel(args.x)
    if args.yf is None or args.yf not in result["metric"].keys():
        metric_name = args.y
        plt.ylabel(args.y)
    else:
        metric_name = result["metric"][args.yf]
        plt.ylabel(result["metric"][args.yf])

    if args.f is not None and args.f in result["metric"].keys():
        try:
            legend = result["metric"][args.f]
        except:
            legend = pod
    else:
        legend = pod

    if not os.path.exists(filepath):
        os.makedirs(filepath)


    plt.plot(time_x, position_y, linewidth=args.linewidth, label=legend)
    if not args.total:
        mean_value = round(np.mean(position_y), 3)
        variance = round(np.var(position_y), 3)
        
        d = {}
        for var_name in [
            "gpu", 
            "model_name", 
            "metric_name", 
            "mean_value", 
            "variance", 
        ]:
            d[var_name] = eval(var_name)

        write_tsv(
            path=filepath + "/" + tsv_name + ".tsv",
            name=args.tsv_out if (args.tsv_out is not None) else args.o,
            **d,
        )

        max_id = find_max_id(filepath, args.o)
        plt.legend()
        plt.tight_layout()
        plt.savefig(filepath + "/" + args.o + "_" + str(max_id) + '.png')
        plt.figure().clear()    
    

if args.total and lines > 0:
    mean = round(np.mean(position_y), 3)
    var = round(np.var(position_y), 3)
    write_tsv(
        path=filepath + "/" + tsv_name + ".tsv",
        name=args.o,
        metric_name=metric_name, 
        mean_value=mean, 
        variance=var
    )

    max_id = find_max_id(filepath, args.o)
    plt.legend()
    plt.tight_layout()
    plt.savefig(filepath + "/" + args.o + "_" + str(max_id) + '.png',)
    