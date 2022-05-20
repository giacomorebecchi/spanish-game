import numpy as np


def costchar(x, y, c_m):
    return 0.0 if x == y else c_m


def strings_score(a, b, c_skip=1.0, c_misalignment=np.inf, skipchar="-"):

    la = len(a)
    lb = len(b)

    # create a matrix c of size (len(a)+1, len(b)+1)
    c = np.zeros((la + 1, lb + 1))

    whence = np.zeros((la + 1, lb + 1), dtype=int)
    # initialize the base case
    c[0, :] = np.arange(lb + 1) * c_skip
    c[:, 0] = np.arange(la + 1) * c_skip

    whence[0, :] = -1
    whence[:, 0] = 1
    whence[0, 0] = -10000  # sentinel value
    # fill the rest step by step
    for k1 in range(1, la + 1):
        for k2 in range(1, lb + 1):
            w_top = c[k1 - 1, k2] + c_skip
            w_left = c[k1, k2 - 1] + c_skip
            w_diag = c[k1 - 1, k2 - 1] + costchar(a[k1 - 1], b[k2 - 1], c_misalignment)
            w = min(w_left, w_top, w_diag)
            c[k1, k2] = w
            if w == w_left:
                d = -1
            elif w == w_top:
                d = 1
            else:
                d = 0
            whence[k1, k2] = d
    # read out the optimal cost from the bottom right corner
    optcost = c[-1, -1]

    # reconstruct the optimal alignment and the directions
    a1 = ""
    b1 = ""
    k1, k2 = la, lb
    directions = []
    #    optcost1 = 0.0
    while (k1, k2) != (0, 0):
        d = whence[k1, k2]
        if d == -1:  # left
            a1 = skipchar + a1
            b1 = b[k2 - 1] + b1
            k2 -= 1
        #            optcost1 += c_skip
        elif d == 1:  # top
            a1 = a[k1 - 1] + a1
            b1 = skipchar + b1
            k1 -= 1
        #            optcost1 += c_skip
        else:  # diag
            a1 = a[k1 - 1] + a1
            b1 = b[k2 - 1] + b1
            #            optcost1 += costchar(a[k1-1], b[k2-1], c_misalignment)
            k1 -= 1
            k2 -= 1

        directions.insert(0, d)
    #    assert abs(optcost - optcost1) < 1e-12
    return optcost, a1, b1, directions
