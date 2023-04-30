import matplotlib.pyplot as plt

import sys, os


fb = []
with open(sys.argv[1], "rb") as f:
    fb = f.read()



exes = []
wyes = []
result = []

w = 400
h = 200

pxcount = 0
for i in range(int(w/8)):
    for j in range(h):
        byt = fb[j * int(w/8) + i]
        for k in range(8):
            if ((byt >> k) & 1) == 1:
                exes.append((i * 8) + (8 - k))
                wyes.append(h - j)
        pxcount += 8


assert(pxcount == 400 * 200)

plt.scatter(exes, wyes)
plt.show()
