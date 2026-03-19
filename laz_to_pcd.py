import argparse
import json
import math
from pathlib import Path

import numpy as np
import laspy
import pandas as pd
from pypcd4 import PointCloud, Encoding


def heightColor(t: float) -> tuple[float, float, float]:
  # mako-inspired: dark navy -> teal -> yellow-white
  stops = [
    [13, 27, 75],
    [26, 107, 138],
    [49, 200, 132],
    [247, 247, 158],
  ]
  t = max(0, min(1, t))
  s = t * (len(stops) - 1)
  i = min(math.floor(s), len(stops) - 2)
  f = s - i
  return tuple([(val + f * (stops[i + 1][j] - val)) for j, val in enumerate(stops[i])])

def json_to_pcd(
    points_paths: list[Path],
    output_path: Path,
) -> None:

    global_min_z = math.inf
    global_max_z = -math.inf
    # global_min_y = math.inf
    # global_max_y = -math.inf
    # global_min_x = math.inf
    # global_max_x = -math.inf

    for path in points_paths:
        input = laspy.read(path)

        min_z = input.z.min()
        if min_z < global_min_z:
            global_min_z = min_z
        max_z = input.z.max()
        if max_z > global_max_z:
            global_max_z = max_z
        # min_y = input.y.min()
        # if min_y < global_min_y:
        #     global_min_y = min_y
        # max_y = input.y.max()
        # if max_y > global_max_y:
        #     global_max_y = max_y
        # min_x = input.x.min()
        # if min_x < global_min_x:
        #     global_min_x = min_x
        # max_x = input.x.max()
        # if max_x > global_max_x:
        #     global_max_x = max_x

    range_z = global_max_z - global_min_z
#
#     mid_x = global_max_x - global_min_x
#     mid_y = global_max_y - global_min_y

    stacks = []
    for path in points_paths:
        input = laspy.read(path)

        colours = []
        for z in input.z:
            r, g, b = heightColor((z - global_min_z) / range_z)
            colours.append([r, g, b])
        cols = np.array(colours)
        encoded_cols = PointCloud.encode_rgb(cols)

        raw = np.vstack((input.x, input.y, input.z, encoded_cols)).T
        stacks.append(raw)
    raw = np.concat(stacks)

    pc = PointCloud.from_xyzrgb_points(raw)
    pc.save(output_path, encoding=Encoding.BINARY_COMPRESSED)

    with open(output_path.with_suffix(".json"), "w", encoding="utf-8") as f:
      json.dump({
        "name": "Kullberg",
        "zMin": min_z,
        "zMax": max_z,
      }, f)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--points',
        action="append",
        type=Path,
        help="Path JSON point data.",
        required=True,
        dest="points_path"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        dest="output_path",
        help="Destination folder for raster files."
    )
    args = parser.parse_args()
    print(args)
    json_to_pcd(
        args.points_path,
        args.output_path,
    )

if __name__ == "__main__":
    main()
