from utils.utils import parse_mlperf_metrics, write_tsv, validate_filename
import os 
import argparse
import sys
import logging

parser = argparse.ArgumentParser(description='Parse mlperf metrics.')
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
    d = {}
    d["name"] = args.o
    d.update(parse_mlperf_metrics(logs_filepath))
    
    write_tsv(
        path=filepath + "/" + tsv_name + "_logs.tsv",
        **d
    )
    
except Exception as e:
    logging.error(f"Couldn't parse logs.txt file: {e}")
