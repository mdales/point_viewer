library(lidR)
library(terra)
library(ggplot2)
library(sf)
library(maptiles)

dtm_files <- list.files("/Users/michael/dev/kullbergcraft/data/dem_tiles",
                        pattern = "\\.tif$|\\.img$", full.names = TRUE)
dtm <- vrt(dtm_files)


f <- "/Users/michael/dev/kullbergcraft/data/laz_files/70_6/23F025_707_60_2500.laz"
las <- readLAS(f, select = "xyzr")
las_area <- st_bbox(las)

dtm_sub <- crop(dtm, st_bbox(las))
dtm_limits <- minmax(dtm_sub)


#las <- normalize_height(las, dtm)

# Clip a small area and decimate
# las_sub <- clip_rectangle(las,
#                          xleft = 600116, ybottom = 7074424,  # adjust to your area of interest
#                          xright = 600370, ytop = 7074650)
 las_sub <- clip_rectangle(las,
                          xleft = 601053, ybottom = 7073594,  # adjust to your area of interest
                          xright = 601278, ytop = 7073760)
las_sub <- decimate_points(las_sub, homogenize(10, 1))  # 10pts/m²

# Export just xyz + height for colouring
pts <- as.data.frame(las@data[, c("X", "Y", "Z")])

# Centre the coordinates so they're not huge numbers
pts$X <- pts$X - mean(pts$X)
pts$Y <- pts$Y - mean(pts$Y)
pts$Z <- pts$Z - dtm_limits["min", 1]

cat(sprintf("Exporting %d points\n", nrow(pts)))
jsonlite::write_json(pts, "pointcloud.json", digits = 3)


7073760.1, 601053.6
7073594.7, 601278.7