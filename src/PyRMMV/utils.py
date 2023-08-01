import logging

logging.basicConfig(filename="PyRMMV.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

DEFAULT_TILE = {"ul": 13, "ur": 14, "ll": 17, "lr": 18}
DEFAULT_INDEX_DICT = {
    # Outside Corner (OC) for 2,3,6,7
    # Inside Corner (IC) for >=8

    0: {},
    1: {"ul": 2},
    2: {"ur": 3},
    3: {"ul": 2, "ur": 3},

    4: {"lr": 7},
    5: {"lr": 7, "ul": 2},
    6: {"lr": 7, "ur": 3},
    7: {"lr": 7, "ul": 2, "ur": 3},

    8: {"ll": 6},
    9: {"ll": 6, "ul": 2},
    10: {"ll": 6, "ur": 3},
    11: {"ll": 6, "ul": 2, "ur": 3},

    12: {"ll": 6, "lr": 7},
    13: {"ll": 6, "lr": 7, "ul": 2},
    14: {"ll": 6, "lr": 7, "ur": 3},
    15: {"ll": 6, "lr": 7, "ul": 2, "ur": 3},

    16: {"ul": 12, "ll": 16},
    17: {"ul": 12, "ll": 16, "ur": 3},
    18: {"ul": 12, "ll": 16, "lr": 7},
    19: {"ul": 12, "ll": 16, "ur": 3, "lr": 7},

    20: {"ul": 9, "ur": 10},
    21: {"ul": 9, "ur": 10, "lr": 7},
    22: {"ul": 9, "ur": 10, "ll": 6},
    23: {"ul": 9, "ur": 10, "ll": 6, "lr": 7},

    24: {"ur": 15, "lr": 19},
    25: {"ur": 15, "lr": 19, "ll": 6},
    26: {"ur": 15, "lr": 19, "ul": 2},
    27: {"ur": 15, "lr": 19, "ll": 6, "ul": 2},

    28: {"ll": 21, "lr": 22},
    29: {"ll": 21, "lr": 22, "ul": 2},
    30: {"ll": 21, "lr": 22, "ur": 3},
    31: {"ll": 21, "lr": 22, "ul": 2, "ur": 3},

    32: {"ul": 12, "ur": 15, "ll": 16, "lr": 19},
    33: {"ul": 9, "ur": 10, "ll": 21, "lr": 22},

    34: {"ul": 8, "ur": 9, "ll": 12},
    35: {"ul": 8, "ur": 9, "ll": 12, "lr": 7},

    36: {"ul": 10, "ur": 11, "lr": 15},
    37: {"ul": 10, "ur": 11, "lr": 15, "ll": 6},

    38: {"lr": 23, "ur": 15, "ll": 21},
    39: {"lr": 23, "ur": 15, "ll": 21, "ul": 2},

    40: {"ul": 16, "ll": 20, "lr": 21},
    41: {"ul": 16, "ll": 20, "lr": 21, "ur": 3},

    42: {"ul": 0, "ur": 1, "ll": 12, "lr": 15},
    43: {"ul": 0, "ur": 9, "ll": 4, "lr": 21},
    44: {"ul": 16, "ur": 19, "ll": 4, "lr": 5},
    45: {"ul": 10, "ur": 1, "ll": 22, "lr": 5},
    46: {"ul": 8, "ur": 11, "ll": 20, "lr": 23},

    47: {"ul": 8, "ur": 11, "ll": 20, "lr": 23},
}
