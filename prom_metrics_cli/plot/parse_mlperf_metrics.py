from utils.utils import parse_mlperf_metrics, write_tsv, validate_filename
import os 
import argparse
import sys
import logging

parser = argparse.ArgumentParser(description='Parse matplotlib labels.')
parser.add_argument(
    '-o', 
    action='store', 
    required=True ,  
    help="Name of the output png. Name can only contain - _ :\
    or alphanumerics and can't start or end with - or _"
)
parser.add_argument(
    '--tsv-out', 
    type=str, 
    required=False,  
    help="Tsv output's filename. If not specified -o argument will be used"
)

args = parser.parse_args()

dirname, _ = os.path.split(os.path.abspath(__file__))
filepath = os.path.join(dirname, "figures", args.o)
logs_filepath = os.path.join(dirname, "figures", args.o, "logs.txt")
tsv_name = args.tsv_out if (args.tsv_out is not None) else args.o

if not validate_filename(args.o):
    logging.error("Filename validation failed, exiting")
    parser.print_help()
    sys.exit(1)

if args.tsv_out is not None and not validate_filename(args.tsv_out):
    logging.error("Filename validation failed, exiting")
    parser.print_help()
    sys.exit(1)

try:
    scenario, qps, mean, time, acc, queries, tiles = parse_mlperf_metrics(logs_filepath)
        
    d = {}
    for var_name in [ 
        "scenario", 
        "qps", 
        "mean", 
        "time", 
        "acc", 
        "queries", 
        "tiles"
    ]:
        d[var_name] = eval(var_name)
    write_tsv(
        path=filepath + "/" + tsv_name + "_logs.tsv",
        **d
    )
    d["name"] = args.o

except:
    logging.error("Couldn't parse logs.txt file")
