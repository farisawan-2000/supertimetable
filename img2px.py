from PIL import Image
import png, sys, os

infile = sys.argv[1]

outfile = "img.bin"

im = Image.open(infile)

w, h = im.size
print(w, h)

pxcount = 0
with open(outfile, "wb+") as f:
    for i in range(h):
        for j in range(w)[::8]:
            bf = [im.getpixel((k, i)) for k in range(j, j + 8)]

            result = 0
            for o in bf:
                result <<= 1
                result |= (o ^ 1)

            result ^= 0xFF
            print(i, j, bf, result, result.to_bytes(1, 'big'))
            f.write(result.to_bytes(1, 'big'))
            pxcount += 8
        # for j in range(w):
        #     print(i, j)
        #     bf = im.getpixel((j, i))
        #     if bf == 1:
        #         f.write(0xFF.to_bytes(1, 'big'))
        #     else:
        #         f.write(0x00.to_bytes(1, 'big'))
        #     pxcount+=1


print(pxcount)
assert(pxcount == w * h)
