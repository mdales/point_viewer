library(lidR)
library(sf)
library(terra)

dtm_files <- list.files("/Users/michael/dev/kullbergcraft/data/dem_tiles", pattern = "\\.tif$|\\.img$", full.names = TRUE)
dtm <- vrt(dtm_files)

f <- "/Users/michael/dev/kullbergcraft/data/laz_files/70_5/23F024_707_59_0025.laz"  # just pick one

las <- readLAS(f, select = "xyzr")
las <- normalize_height(las, dtm)
chm <- rasterize_canopy(las, res = 0.5, algorithm = pitfree())
ttops <- locate_trees(chm, lmf(ws = function(x) x * 0.07 + 2, hmin = 5))

st_write(ttops, "test_tile.gpkg", delete_dsn = TRUE)

# Quick visual check
plot(chm)
plot(sf::st_geometry(ttops), add = TRUE, pch = 3, col = "red")