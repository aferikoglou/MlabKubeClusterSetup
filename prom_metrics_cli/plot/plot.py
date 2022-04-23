from matplotlib import container
import matplotlib.pyplot as plt
import json
import os
import argparse
import re
import sys

def validate_filename(filename):
    pattern  = r'^[a-z0-9][a-z0-9_-]+[a-z0-9]$'
    pat = re.compile(pattern)
    return re.fullmatch(pat, filename)

def find_max_id(dirname: str, outfile: str)-> int:
    max_id = 0
    for filename in os.listdir(dirname + "/figures"):
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
parser.add_argument('-l', '--legend-list', nargs='+', default=[], help="Manually import a list of legends for matplotlib")
parser.add_argument('-f', action='store', help="Json field from which to extract legends")
parser.add_argument('-o', action='store', required = True,  help="Name of the output png. Name can only contain - _ \
    or alphanumerics and can't start or end with - or _")

args = parser.parse_args()

if not validate_filename(args.o):
    parser.print_help()
    sys.exit(1)

print(args)

dirname, _ = os.path.split(os.path.abspath(__file__))

data = input()

if not data.startswith("{"):
    data = "".join(data.split(" ")[2:])
try:
    print(data)
    data = json.loads(data)
except:
    print("Input data not json serializable")

legend = []
for result in data["data"]["result"]:

    base = float(result["values"][0][0])
    time = []
    position = []
    for v in result["values"]:
        time.append(float(v[0]) - base)
        position.append(float(v[1]))

    plt.plot(time, position)
    plt.xlabel(args.x)
    plt.ylabel(args.y)
    if args.f is not None:
        legend.append(result["metric"][args.f])

    if not os.path.exists(dirname + "/figures"):
        os.makedirs(dirname + "/figures")

max_id = find_max_id(dirname, args.o)

if len(args.legend_list) > 0:
    legend = []
    for l in args.legend_list:
        legend.append(l)
    plt.legend(legend)
elif args.f is not None:
    plt.legend(legend)

plt.savefig(dirname + '/figures/' + args.o + "_" + str(max_id) + '.png')
