import matplotlib.pyplot as plt

import sys, os


fb = []
with open(sys.argv[1], "rb") as f:
    fb = f.read()



exes = []
exes2 = []
wyes = []
wyes2 = []
result = []

w = 64
h = 64

pxcount = 0

# for i in range(int(w/8)):
#     for j in range(h):
#         byt = fb[j * int(w/8) + i]
#         for k in range(8):
#             if ((byt >> k) & 1) == 1:
#                 exes.append((i * 8) + (8 - k))
#                 wyes.append(h - j)
#         pxcount += 8

for i in range(int(w/4)):
    for j in range(h):
        idx = (j) * int(w/4) + (i - 1)
        print(i, j, idx)
        short1 = fb[idx]
        short2 = fb[idx + 1]
        short = (short1 << 8) | short2
        # print("0x%04X" % short, end=" ")
        for k in range(16)[::2]:
            # print("0x%x" % ((short >> k) & 0b_11), end=", ")
            if ((short >> k) & 0b_11) & 0b_01:
                exes.append(((i * 8) + (8 - k)) / 2)
                wyes.append(h - j)
            if ((short >> k) & 0b_11) & 0b_10:
                exes2.append(((i * 8) + (8 - k)) / 2)
                wyes2.append(h - j)
            pxcount += 1

print(w, h, w*h, pxcount)
# assert(pxcount == w * h)

plt.scatter(exes, wyes)
plt.scatter(exes2, wyes2)
plt.show()
