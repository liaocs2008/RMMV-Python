# https://forums.rpgmakerweb.com/index.php?threads/how-to-determine-your-tileid.91129/
# This is to reproduce the floor type shown in the link.

import matplotlib.pyplot as plt
from PIL import Image
from PyRMMV import RMMVMap

if __name__ == "__main__":
    A1_pic = "resources/Outside_A1.png"
    output_fname = "resources/outputs/floor_type.jpg"

    rmmvmap = RMMVMap(A1=A1_pic)
    fig, ax = plt.subplots(nrows=6, ncols=8)
    for i in range(48):
        res = rmmvmap.get_tile(2432 + i)
        r = i // 8
        c = i % 8
        ax[r, c].imshow(Image.fromarray(res))
        ax[r, c].set_axis_off()
    fig.tight_layout()
    plt.savefig(output_fname)
    print(f"save floor type to {output_fname}")
