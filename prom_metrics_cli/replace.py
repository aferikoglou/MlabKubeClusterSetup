#
# Script used to convert single quotes to double quotes from source file
# and save the result to target file
#

import re

source = input("Enter the source file path")
target = input("Enter the target file path")

rep = {"\"": "'", "'": "\""}
rep = dict((re.escape(k), v) for k, v in rep.items())

with open(source, "r") as f:
    with open(target, "w") as f_o:
        lines = f.readlines()
        for line in lines:
            pattern = re.compile("|".join(rep.keys()))
            line = pattern.sub(lambda m: rep[re.escape(m.group(0))], line)
            f_o.write(line)
