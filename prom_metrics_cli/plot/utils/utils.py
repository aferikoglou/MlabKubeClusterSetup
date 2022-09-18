import re
import csv
import os

def write_tsv(path: str, **kwargs) -> None:
    fieldnames = list(kwargs.keys())
    rows = [kwargs]

    exists = False
    if os.path.exists(path) and os.path.getsize(path) > 0:
        exists = True

    # write rows to the csv file
    with open(path, "a", encoding="UTF8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t")
        if not exists:
            writer.writeheader()
        writer.writerows(rows)
        f.flush()


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


def parse_mlperf_metrics(path: str) -> dict:
    with open(path, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        last_line = file.readline().decode()
    metrics = [(x[0], x[1].strip(',')) if len(x) > 1 else x[0] for x in [y.split("=") for y in last_line.split(" ")]]
    d = {}
    for x in metrics:
        if isinstance(x, tuple):
            d[x[0]] = x[1]
        else:
            d['scenario'] = x
    return d
