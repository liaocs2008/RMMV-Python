import json
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from PyRMMV import RMMVMap

def plot_map(fname, rmmvmap, output_fname):
    with open(fname, "r") as j:
        contents = json.loads(j.read())

    h, w = contents["height"], contents["width"]
    target = np.array(contents["data"]).reshape([6, h, w])

    plt.figure()
    print(fname)
    res = []
    for i, row in enumerate(target[0]):
        row_tiles = []
        print(" ".join(map(str, row.tolist())))
        for j, tile_id in enumerate(row):
            t = rmmvmap.get_tile(tile_id)
            row_tiles.append(t)
        row_tiles = np.hstack(row_tiles)
        res.append(row_tiles)
    res = np.vstack(res)

    plt.title(fname)
    plt.imshow(Image.fromarray(res))
    print(f"save output figure to {output_fname}")
    plt.savefig(output_fname)


if __name__ == "__main__":
    rmmvmap = RMMVMap(A1="resources/World_A1.png", A2="resources/World_A2.png")
    plot_map("resources/Map001.json", rmmvmap, "resources/outputs/Map001.jpg")
