import matplotlib.pyplot as plt
import json
import os
import argparse
import re
import sys
import logging

def validate_filename(filename):
    pattern  = r'^[a-z0-9][a-z0-9_-]+[a-z0-9]$'
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
parser.add_argument('-o', action='store', required = True,  help="Name of the output png. Name can only contain - _ \
    or alphanumerics and can't start or end with - or _")
parser.add_argument('-filter', action='store', required = False,  help="Json string where keys correspond to json fields \
    and the values correspond to the values you want to keep.")

args = parser.parse_args()

if not validate_filename(args.o):
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

if not data.startswith("{"):
    data = "".join(data.split(" ")[2:])
try:
    print(data)
    data = json.loads(data)
except:
    logging.warning("Input data not json serializable")
    sys.exit(-1)

# If a key does not belong in data dict remove it from the filter dict
filter_copy = filter.copy()
for key in filter_copy.keys():
    found = False
    for result in data["data"]["result"]:
        if key in result["metric"].keys():
            found = True
            break
    if not found:
        logging.warning(key, "not found in any Json field, deleting.")
        del filter[key]

legend = []
for i, result in enumerate(data["data"]["result"]):
    skip = False
    for k, v in filter.items():
        if k not in result["metric"].keys() or result["metric"][k] != v:
            logging.warning(v + " not found in data's keys, skipping result No." + str(i))
            skip = True
            break

    if skip:
        continue

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

    if args.f is not None:
        legend.append(result["metric"][args.f])

if not os.path.exists(filepath):
    os.makedirs(filepath)

max_id = find_max_id(filepath, args.o)

if len(args.legend_list) > 0:
    legend = []
    for l in args.legend_list:
        legend.append(l)
    plt.legend(legend)
elif args.f is not None:
    plt.legend(legend)

plt.savefig(filepath + "/" + args.o + "_" + str(max_id) + '.png')
