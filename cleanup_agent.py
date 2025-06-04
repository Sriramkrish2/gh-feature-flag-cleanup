#!/usr/bin/env python3

import sys

if len(sys.argv) < 3:
    print("Usage: cleanup_agent.py <file> <flag>")
    sys.exit(1)

file = sys.argv[1]
flag = sys.argv[2]

with open(file, "r") as f:
    lines = f.readlines()

with open(file, "w") as f:
    for line in lines:
        if flag not in line:
            f.write(line)
