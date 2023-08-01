# https://forums.rpgmakerweb.com/index.php?threads/how-to-determine-your-tileid.91129/
# https://forums.rpgmakerweb.com/index.php?threads/autotile-tile-ids.2829/

import numpy as np
from PIL import Image
from typing import Dict, Tuple

from .utils import logger
from .utils import DEFAULT_TILE, DEFAULT_INDEX_DICT


class TilesetsBase:
    """
    TilesetsBase follows the manual in RMMV VX Ace, where a tileset defines a tile type shown in the map editor.

    Args:
        fname: input picture file location

        h_ratio: number of tiles (DxD) per column

        w_ratio: number of tiles (DxD) per row

        D: tile size dimension, assuming tile is squared.

        tileset_name: tileset name in {A1, A2, A3, A4, A5, B, C, D, E}

        tile_id_range: tile id range changes with tileset_name

        index_dict: index direction updates

        default_tile: default tile composition

    """

    def __init__(
            self,
            fname: str,
            h_ratio: int,
            w_ratio: int,
            D: int,
            tileset_name: str,
            tile_id_range: Tuple,
            index_dict: Dict,
            default_tile: Dict,
    ):
        self.D = D
        self.default_tile = default_tile
        self.index_dict = index_dict
        self.rows = h_ratio
        self.cols = w_ratio
        self.tileset_name = tileset_name

        assert len(tile_id_range) == 2 and tile_id_range[1] > tile_id_range[0] >= 0
        self.tile_id_range = tile_id_range

        if not fname:
            logger.warning(f"[{self.tileset_name}] empty input image name")
            return

        image = Image.open(fname)
        width, height = image.size
        assert width == w_ratio * D and w_ratio % 2 == 0, f"[{self.tileset_name}] width={width}, D={D}, w_ratio={w_ratio}"
        assert height == h_ratio * D and h_ratio % 3 == 0, f"[{self.tileset_name}] height={width}, D={D}, h_ratio={h_ratio}"
        np_img = np.array(image)

        # turn into tilesets
        np_img = np_img.reshape([h_ratio // 3, 3 * D, w_ratio // 2, 2 * D, -1])
        np_img = np_img.transpose([0, 2, 1, 3, -1])  # [h/3,w/2, 3D, 2D, -1]

        # transpose each tileset
        np_img = np_img.reshape([h_ratio // 3, w_ratio // 2, 6, D // 2, 4, D // 2, -1])
        np_img = np_img.transpose([0, 1, 2, 4, 3, 5, 6])  # [h/3, w/2, 6, 4, D/2, D/2, -1]
        self.tilesets = np_img

    def check_valid_tile_id(self, tile_id):
        return self.tile_id_range[0] <= tile_id <= self.tile_id_range[1]

    def get_tileset(self, tile_id):
        logger.debug(f"[{self.tileset_name}] tile_id={tile_id}")
        tileset = None
        if not self.check_valid_tile_id(tile_id):
            logger.error(f"[{self.tileset_name}] invalid tile_id={tile_id} for {self.tile_id_range}")
        else:
            index = (tile_id - self.tile_id_range[0]) // 48
            logger.debug(f"[{self.tileset_name}] tileset index={index}")
            row = index // self.cols
            col = index % self.cols
            tileset = self.tilesets[row, col]
        return tileset

    def generate_tile(self, ul, ur, ll, lr, input_tileset):
        logger.debug(f"[{self.tileset_name}] ul={ul}, ur={ur}, ll={ll}, lr={lr}")
        rows, cols = input_tileset.shape[:2]

        def parse_y_x(v, c):
            if type(v) == int:
                return v // c, v % c
            else:
                return v

        ul = parse_y_x(ul, cols)
        ur = parse_y_x(ur, cols)
        ll = parse_y_x(ll, cols)
        lr = parse_y_x(lr, cols)

        row1 = np.hstack([input_tileset[ul], input_tileset[ur]])
        row2 = np.hstack([input_tileset[ll], input_tileset[lr]])
        ans = np.vstack([row1, row2])
        return ans

    def get_tile(self, tile_id, return_index=False):
        tileset = self.get_tileset(tile_id)
        if tileset is None:
            return None

        offset = tile_id - self.tile_id_range[0]
        index = offset % 48
        logger.debug(f"[{self.tileset_name}] tile index={index}")
        tile_setting = dict(self.default_tile)
        if index not in self.index_dict:
            raise Exception(f"[{self.tileset_name}] tile index={index} not supported yet")
        else:
            tile_setting.update(self.index_dict[index])
        tile_setting['input_tileset'] = tileset
        tile = self.generate_tile(**tile_setting)
        if return_index:
            return tile, index
        else:
            return tile


class TilesetsA1(TilesetsBase):
    """
    Tilesets class for A1 autotiles.
    """

    def __init__(self, fname, h_ratio, w_ratio, D, tileset_name, tile_id_range, index_dict, default_tile):
        super().__init__(fname, h_ratio, w_ratio, D, tileset_name, tile_id_range, index_dict, default_tile)

        # remove extra animation part in each group
        if not hasattr(self, "tilesets"):
            logger.warning(f"[{self.tileset_name}] not initialized")
        else:
            select_cols = np.array([0, 3, 4, 7])
            self.shrink_tilesets = self.tilesets[:, select_cols]

    def get_tileset(self, tile_id):
        tileset = None
        if not self.check_valid_tile_id(tile_id):
            logger.warning(f"[{self.tileset_name}] invalid tile_id={tile_id} for {self.tile_id_range}")
        else:
            # A1 uses z-order like curve
            index = (tile_id - self.tile_id_range[0]) // 48
            logger.debug(f"[{self.tileset_name}] tileset index={index}")
            z_order = np.array([
                [0, 2, 4, 5],
                [1, 3, 6, 7],
                [8, 9, 12, 13],
                [10, 11, 14, 15],
            ])
            rs, cs = np.where(z_order == index)
            assert len(rs) == 1
            tileset = self.shrink_tilesets[rs[0], cs[0]]
        return tileset


# To implement
class TilesetsA5(TilesetsBase):
    def __init__(self, fname, h_ratio, w_ratio, D, tileset_name, tile_id_range, index_dict, default_tile):
        super().__init__(fname, h_ratio, w_ratio, D, tileset_name, tile_id_range, index_dict, default_tile)


# To implement
class TilesetsBCDE(TilesetsBase):
    def __init__(self, fname, h_ratio, w_ratio, D, tileset_name, tile_id_range, index_dict, default_tile):
        super().__init__(fname, h_ratio, w_ratio, D, tileset_name, tile_id_range, index_dict, default_tile)


class RMMVMap:
    """
    A map class consists of 9 different tilesets.
    """

    def __init__(self, A1="", A2="", A3="", A4="", A5="", B="", C="", D="", E=""):
        self.tilesets_list = [
            TilesetsA1(A1, 12, 16, 48, "A1", (2048, 2815), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBase(A2, 12, 16, 48, "A2", (2816, 4351), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBase(A3, 12, 16, 48, "A3", (4352, 5887), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBase(A4, 12, 16, 48, "A4", (5888, 8191), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsA5(A5, 16, 8, 48, "A5", (1536, 1663), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBCDE(B, 16, 16, 48, "B", (0, 255), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBCDE(C, 16, 16, 48, "C", (256, 511), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBCDE(D, 16, 16, 48, "D", (512, 767), DEFAULT_INDEX_DICT, DEFAULT_TILE),
            TilesetsBCDE(E, 16, 16, 48, "E", (768, 1023), DEFAULT_INDEX_DICT, DEFAULT_TILE),
        ]

    def __str__(self):
        tilesets_names = [tilesets.tileset_name for tilesets in self.tilesets_list if tilesets.tileset_name]
        tilesets_names = " ".join(tilesets_names)
        res = f"RMMVMap using tilesets {tilesets_names}"
        return res

    def get_tile(self, tile_id, return_index=False):
        res = None
        for tilesets in self.tilesets_list:
            res = tilesets.get_tile(tile_id, return_index=return_index)
            if res is not None:
                logger.debug(f"[{tilesets.tileset_name}] tile_id={tile_id} found!")
                break
        return res
