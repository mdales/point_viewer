"""
Extract a land cover raster for the COPC tile extent and export:
  landcover.png   — RGB image, one pixel per 10 m cell, colors from the GeoTIFF palette
  landcover.json  — bounds, pixel size, and class legend (id → name and hex color)

Run from the point_viewer directory:
  python extract_landcover.py
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image
import rasterio
from rasterio.crs import CRS
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds

# ── Config ────────────────────────────────────────────────────────────────────

SRC = Path("../kullbergcraft/data/NMD2018_basskikt_ogeneraliserad_Sverige_v1_1/"
           "nmd2018bas_ogeneraliserad_v1_1.tif")

OUT_PNG  = Path("landcover.png")
OUT_JSON = Path("landcover.json")

# Extent of the 9 COPC tiles in SWEREF99TM (EPSG:3006), with a small margin
EXTENT_SWEREF = {
    "xmin": 597000.0,
    "ymin": 7069500.0,
    "xmax": 606000.0,
    "ymax": 7078000.0,
}

# NMD 2018 base layer class names (class code → Swedish/English name).
# Codes not listed here will appear as "Unknown".
NMD_NAMES = {
    0:   "Utanför kartläggningen",   # Outside mapping area
    2:   "Öppen våtmark",            # Open wetland
    3:   "Åkermark",                 # Arable land
    41:  "Övrig öppen mark, ej vegeterad",   # Non-vegetated other open land
    42:  "Övrig öppen mark, vegeterad",      # Vegetated other open land
    51:  "Exploaterad mark, byggnad",        # Artificial surfaces – building
    52:  "Exploaterad mark, ej byggnad/väg", # Artificial surfaces – other
    53:  "Exploaterad mark, väg/järnväg",    # Artificial surfaces – road/railway
    61:  "Inlandsvatten",            # Inland water
    62:  "Marint vatten",            # Marine water
    111: "Tallskog, ej våtmark",     # Pine forest not on wetland
    112: "Granskog, ej våtmark",     # Spruce forest not on wetland
    113: "Blandskog barrskog, ej våtmark",   # Mixed coniferous not on wetland
    114: "Blandskog, ej våtmark",    # Mixed forest not on wetland
    115: "Lövskog, ej våtmark",      # Deciduous forest not on wetland
    116: "Ädellövskog, ej våtmark",  # Deciduous hardwood not on wetland
    117: "Lövskog m. ädellöv, ej våtmark",  # Deciduous with hardwood not on wetland
    118: "Temporärt ej skog, ej våtmark",   # Temporarily non-forest not on wetland
    121: "Tallskog, våtmark",        # Pine forest on wetland
    122: "Granskog, våtmark",        # Spruce forest on wetland
    123: "Blandskog barrskog, våtmark",     # Mixed coniferous on wetland
    124: "Blandskog, våtmark",       # Mixed forest on wetland
    125: "Lövskog, våtmark",         # Deciduous forest on wetland
    126: "Ädellövskog, våtmark",     # Deciduous hardwood on wetland
    127: "Lövskog m. ädellöv, våtmark",    # Deciduous with hardwood on wetland
    128: "Temporärt ej skog, våtmark",     # Temporarily non-forest on wetland
}

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    with rasterio.open(SRC) as src:
        print(f"Source CRS : {src.crs}")
        print(f"Source size: {src.width} × {src.height} px")
        print(f"Pixel size : {src.res}")

        # Reproject the desired extent into the source CRS if needed
        src_crs = src.crs
        sweref  = CRS.from_epsg(3006)

        if src_crs == sweref:
            xmin, ymin, xmax, ymax = (
                EXTENT_SWEREF["xmin"], EXTENT_SWEREF["ymin"],
                EXTENT_SWEREF["xmax"], EXTENT_SWEREF["ymax"],
            )
        else:
            xmin, ymin, xmax, ymax = transform_bounds(
                sweref, src_crs,
                EXTENT_SWEREF["xmin"], EXTENT_SWEREF["ymin"],
                EXTENT_SWEREF["xmax"], EXTENT_SWEREF["ymax"],
            )
            print(f"Reprojected extent: {xmin:.1f} {ymin:.1f} {xmax:.1f} {ymax:.1f}")

        window    = from_bounds(xmin, ymin, xmax, ymax, transform=src.transform)
        transform = src.window_transform(window)
        data      = src.read(1, window=window)

        print(f"Cropped size: {data.shape[1]} × {data.shape[0]} px")
        print(f"Unique classes: {sorted(np.unique(data).tolist())}")

        # Read the embedded color table (maps pixel value → (R, G, B, A))
        try:
            colormap = src.colormap(1)
        except Exception:
            colormap = {}
            print("Warning: no colormap found in file — pixels will be grey")

    # Build an RGB image from the color table
    h, w   = data.shape
    rgb    = np.zeros((h, w, 3), dtype=np.uint8)
    legend = {}

    for class_id in np.unique(data):
        class_id = int(class_id)
        rgba     = colormap.get(class_id, (180, 180, 180, 255))
        r, g, b  = int(rgba[0]), int(rgba[1]), int(rgba[2])
        mask = data == class_id
        rgb[mask, 0] = r
        rgb[mask, 1] = g
        rgb[mask, 2] = b
        hex_color = f"#{r:02x}{g:02x}{b:02x}"
        legend[str(class_id)] = {
            "name":  NMD_NAMES.get(class_id, "Unknown"),
            "color": hex_color,
        }

    Image.fromarray(rgb, "RGB").save(OUT_PNG)
    print(f"Saved {OUT_PNG}  ({OUT_PNG.stat().st_size // 1024} KB)")

    # Save metadata — bounds in SWEREF99TM so JS can do the lookup
    # transform.c = xMin of raster, transform.f = yMax of raster (top-left origin)
    # If source was not SWEREF, we saved the reprojected window but JS coords are
    # SWEREF, so we restate bounds in SWEREF.
    meta = {
        "xMin":      EXTENT_SWEREF["xmin"],
        "yMax":      EXTENT_SWEREF["ymax"],
        "pixelSize": abs(src.res[0]),   # metres per pixel (assumed square)
        "width":     w,
        "height":    h,
        "legend":    legend,
    }
    OUT_JSON.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    print(f"Saved {OUT_JSON}")


if __name__ == "__main__":
    main()
