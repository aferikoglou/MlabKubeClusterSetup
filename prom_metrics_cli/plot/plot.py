import matplotlib.pyplot as plt
import json
import os
import argparse
import re
import sys
import logging


def validate_filename(filename):
    pattern  = r'^[a-zA-Z0-9][:a-zA-Z0-9_-]+[a-zA-Z0-9]$'
    pat = re.compile(pattern)
    return re.fullmatch(pat, filename)


def find_max_id(dirname: str, outfile: str)-> int:
    max_id = 0
    for filename in os.listdir(dirname):
        tmp = filename.split(".")
        if (not len(tmp) > 1) or (not "_".join(tmp[0].split("_")[:-1]).startswith(outfile)):
            continue
        try:
            tmp = int(tmp[0].split("_")[-1])
        except:
            continue

        if tmp > max_id:
            max_id = tmp

    return max_id + 1


parser = argparse.ArgumentParser(description='Parse matplotlib labels.')
parser.add_argument('-x', action='store', type=str,
                    help='xlabel')
parser.add_argument('-y', action='store', type=str,
                    help='ylabel')
parser.add_argument('-yf', action='store', type=str,
                    help='ylabel extracted from json field. Overrides -y argument')
parser.add_argument('-l', '--legend-list', nargs='+', default=[], help="Manually import a list of legends for matplotlib")
parser.add_argument('-f', action='store', help="Json field from which to extract legends")
parser.add_argument('-o', action='store',  required = True ,  help="Name of the output png. Name can only contain - _ :\
    or alphanumerics and can't start or end with - or _")
parser.add_argument('-filter', action='store', required = False,  help="Json string where keys correspond to json fields \
    and values correspond to the values you want to keep. Values can also be regex.")
parser.add_argument('--total', action='store_true', default = False,  help="Add all the metrics from the json object in a single diagram")

args = parser.parse_args()

if not validate_filename(args.o):
    print("Filename validation failed, exiting")
    parser.print_help()
    sys.exit(1)

dirname, _ = os.path.split(os.path.abspath(__file__))
filepath = dirname + "/figures/" + args.o

if args.filter is not None:
    try:
        filter = json.loads(args.filter)
    except:
        logging.warning("filter parameter is not json serializable, ignoring.")

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

legend = []
lines = 0
for i, result in enumerate(data["data"]["result"]):
    skip = False
    for k, v in filter.items():
        pattern = re.compile(v)
        print(pattern)
        if k not in result["metric"] or not re.search(pattern, result["metric"][k]):
            logging.warning(f"{v} not found in {k}, skipping result No.{str(i)}")
            skip = True
            break

    if skip:
        continue

    lines += 1

    if not args.total or i == 0:
        base = float(result["values"][0][0])
    time = []
    position = []
    for v in result["values"]:
        time.append(float(v[0]) - base)
        position.append(float(v[1]))

    plt.plot(time, position)
    plt.xlabel(args.x)
    if args.yf is None or args.yf not in result["metric"].keys():
        plt.ylabel(args.y)
    else:
        plt.ylabel(result["metric"][args.yf])

    if args.f is not None and args.f in result["metric"].keys():
        legend.append(result["metric"][args.f])

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if len(args.legend_list) > 0:
        legend = []
        for l in args.legend_list:
            legend.append(l)
        plt.legend(legend)
    elif args.f is not None:
        plt.legend(legend)

    if not args.total:
        max_id = find_max_id(filepath, args.o)
        plt.tight_layout()
        plt.savefig(filepath + "/" + args.o + "_" + str(max_id) + '.png')
        plt.figure().clear()

if args.total and lines > 0:
    max_id = find_max_id(filepath, args.o)
    plt.tight_layout()
    plt.savefig(filepath + "/" + args.o + "_" + str(max_id) + '.png')
