#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random

v = [(26,1000),(26,100),(5,7)]

for ct in range(len(v)):
    N, Q = v[ct]

    with open("in_{:d}.txt".format(ct+1), "w") as f:
        f.write("{:d} {:d}".format(N, Q))
        f.write("\n")
    with open("out_{:d}.txt".format(ct+1), "w") as f:
        a = [i for i in range(0, N)]
        random.shuffle(a)
        s = ""
        for t in a:
            s += chr(ord('A') + t)
        f.write(s)
        f.write("\n")
