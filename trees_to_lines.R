library(sf)
library(terra)
library(jsonlite)
library(lidR)

trees  <- st_read("/Users/michael/dev/kullbergcraft/data/tree_tops_pitfree.gpkg")


dtm_files <- list.files("/Users/michael/dev/kullbergcraft/data/dem_tiles",
                        pattern = "\\.tif$|\\.img$", full.names = TRUE)
dtm <- vrt(dtm_files)

f <- "/Users/michael/dev/kullbergcraft/data/laz_files/70_6/23F025_707_60_2500.laz"
las <- readLAS(f, select = "xyzr")
stopifnot(st_crs(trees) == st_crs(las))

# las_sub <- clip_rectangle(las,
# xleft = 601053, ybottom = 7073594,  # adjust to your area of interest
# xright = 601278, ytop = 7073760)


las_area <- st_bbox(las)


clipped_trees <- st_crop(trees, las_area)


coords    <- st_coordinates(clipped_trees)
z_top     <- clipped_trees$Z          # relative elevation from lidR
z_bottom  <- extract(dtm, vect(clipped_trees))[, 2]

x_offset <- 0
y_offset <- 0
z_offset <- z_bottom

tree_lines <- data.frame(
  x        = coords[, 1] - x_offset,
  y        = coords[, 2] - y_offset,
  z_bottom = z_bottom,
  z_top    = z_top + z_bottom
)

write_json(tree_lines, "trees_pitfree.json", auto_unbox = TRUE)
