import argparse
import json
import math
from pathlib import Path

import numpy as np
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
    points_path: Path,
    output_path: Path,
) -> None:
    input = pd.read_json(points_path)

    min_z = input.Z.min()
    max_z = input.Z.max()
    range_z = max_z - min_z

    colours = []
    for _, row in  input.iterrows():
        r, g, b = heightColor((row.Z - min_z) / range_z)
        colours.append([r, g, b])
    cols = np.array(colours)
    encoded_cols = PointCloud.encode_rgb(cols)
    input["rgb"] = encoded_cols

    raw = input.to_numpy()

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

    json_to_pcd(
        args.points_path,
        args.output_path,
    )

if __name__ == "__main__":
    main()
