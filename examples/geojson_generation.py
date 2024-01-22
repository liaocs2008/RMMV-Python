import json
import numpy as np
import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
from PIL import Image
from shapely.geometry.multipolygon import MultiPolygon
from scipy.signal import convolve2d

from autotile_map_generation import plot_map
from PyRMMV import RMMVMap


# https://leetcode.com/problems/max-area-of-island/solutions/3491040/python-two-approaches-dfs-dsu/
def maxAreaOfIsland(grid, island_defined_on=0):
    def find(u):
        if u == parent[u]:
            return u
        else:
            parent[u] = find(parent[u])
            return parent[u]

    def union(u, v):
        pu, pv = find(u), find(v)
        if pu == pv:
            return
        if size[pv] > size[pu]:
            parent[pu] = pv
            size[pv] += size[pu]
        else:
            parent[pv] = pu
            size[pu] += size[pv]

    m = len(grid)
    n = len(grid[0])
    f = 0
    parent = [i for i in range(m * n)]
    # size=[1 for i in range(m*n)]
    size = []
    for x in range(m):
        for y in range(n):
            if grid[x][y] == island_defined_on:
                size.append(1)
            else:
                size.append(0)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == island_defined_on:
                f = 1
                a = i * n + j
                for u, v in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                    if 0 <= u < m and 0 <= v < n and grid[u][v] == island_defined_on:
                        b = u * n + v
                        union(a, b)
    if f == 0:
        return 0

    for i in range(m):
        for j in range(n):
            x = i * n + j
            p = parent[x]
            size[x] = size[p]

    return size


def remove_small_island(input_img, island_defined_on=0):
    new_np_img = input_img.copy()
    grid = input_img.tolist()
    area = maxAreaOfIsland(grid, island_defined_on)
    area = np.array(area)
    max_area = np.max(area)
    area = area.reshape(input_img.shape)
    h, w = area.shape
    for i in range(h):
        for j in range(w):
            if area[i,j] < max_area and area[i,j] > 0:
                # remove small island, 0->1, 1->0
                new_np_img[i, j] = 1 - island_defined_on
    return new_np_img


def fill_binary_map(bmap):
    h, w = bmap.shape
    p = 4
    padded_bmap = np.zeros([h + p * 2, w + p * 2]).astype(np.int32)
    padded_bmap[p:-p, p:-p] = bmap

    # turn 0 to -1, and 1 to 1
    flip_padded_bmap = padded_bmap * 2 - 1
    kernel = np.array([
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ])
    res = convolve2d(flip_padded_bmap, kernel, mode='same', boundary='fill', fillvalue=-1)

    # seperate layers
    c1 = res == 9  # pure land
    c2 = res == -9  # pure water
    padded_bmap[c1] = 1
    padded_bmap[c2] = 0

    # get the original size
    ans = padded_bmap[p:-p, p:-p]
    ans = ans.astype(np.bool_)
    return ans


def turn_figure_into_all_connected_bmap(fig_fname):
    img = Image.open(fig_fname).convert('L')  # turn into binary figure
    h, w = img.size
    if w < h:
        w = int(w * 256 / h)
        h = 256
    else:
        h = int(h * 256 / w)
        w = 256
    img = img.resize([h, w])

    np_img = np.array(img)
    np_img = ~np_img  # invert B&W
    np_img[np_img > 0] = 1

    new_np_img = remove_small_island(np_img, 0)
    new_np_img = remove_small_island(new_np_img, 1)

    # preprocess to make a fulfilled binary map, there are holes from generated image
    bmap = fill_binary_map(new_np_img)
    return bmap


def turn_geojson_into_figure(
    geojson_fname,
    fig_name,
    country_topk_area=None,
    region_col="sovereignt",
):
    df = gpd.read_file(geojson_fname)
    list_df = []
    if country_topk_area is None:
        # take the top 1 area in each region
        country_topk_area = [(c, 1) for c in df[region_col].unique()]

    for country, topk in country_topk_area:  # topk area to keep in this country
        print(country)
        sub_df = df[df[region_col] == country].copy()

        polygon_areas = []
        for polygon in sub_df['geometry'].to_crs({'proj': 'cea'}).explode(index_parts=True):
            km2 = polygon.area / 1e6
            polygon_areas.append(km2)

        if len(polygon_areas) > topk:
            ind = np.argpartition(polygon_areas, -topk)[-topk:]
            topk_ploygon = sub_df['geometry'].explode(index_parts=True).values[ind]
            sub_df['geometry'] = MultiPolygon(topk_ploygon)

        list_df.append(sub_df)

    new_df = gpd.GeoDataFrame(pd.concat(list_df, ignore_index=True))
    list_polygons = new_df['geometry'].explode(index_parts=True).values
    tmp = MultiPolygon(list_polygons)
    tmp = gpd.GeoDataFrame({'geometry': [tmp]})
    tmp = tmp.dissolve() # merge borderlines

    fig = plt.figure(frameon=False)
    ax = fig.add_subplot(111)
    ax.set_axis_off()
    tmp.plot(ax=ax)
    plt.savefig(fig_name, dpi=300, bbox_inches='tight')


def generate_map_json(
    geojson_fname,
    country_topk_area,
    tmp_fig_fname,
    result_map_json,
    region_col,
    template_map_json = "map_template.json",
):
    # turn geojson into pictures
    turn_geojson_into_figure(geojson_fname, tmp_fig_fname, country_topk_area, region_col)

    # generate figure
    bmap = turn_figure_into_all_connected_bmap(tmp_fig_fname)
    rmmvmap = RMMVMap(A1="resources/World_A1.png", A2="resources/World_A2.png")
    water = rmmvmap.estimate_and_fill(2048, bmap==0)
    land = rmmvmap.estimate_and_fill(2816, bmap==1)
    valued_map = water + land

    # generate finalized json
    with open(template_map_json) as f:
        template_map = json.loads(f.read())
    new_map = dict(template_map)
    new_map['height'] = valued_map.shape[0]
    new_map['width'] = valued_map.shape[1]
    new_map['data'] = valued_map.ravel().tolist() + [0] * (5 * valued_map.shape[0] * valued_map.shape[1])
    with open(result_map_json, "w") as f:
        json.dump(new_map, f)

    plot_map(result_map_json, rmmvmap, tmp_fig_fname)


if __name__ == "__main__":

    generate_map_json(
        geojson_fname = "resources/north-america.geojson",
        country_topk_area = [("United States of America", 2), ("Canada", 1)],
        tmp_fig_fname = "resources/outputs/NA.jpg",
        result_map_json = "resources/outputs/NA_map.json",
        region_col = "sovereignt",
    )
