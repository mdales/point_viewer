library(lidR)
library(terra)
library(sf)
dtm_files <- list.files("/Users/michael/dev/kullbergcraft/data/dem_tiles", 
                        pattern = "\\.tif$|\\.img$", full.names = TRUE)
dtm <- vrt(dtm_files)
dtm_ext <- ext(dtm)

laz_dirs <- c("/Users/michael/dev/kullbergcraft/data/laz_files/70_5", 
              "/Users/michael/dev/kullbergcraft/data/laz_files/70_6")
laz_files <- unlist(lapply(laz_dirs, list.files,
                           pattern = "\\.laz$|\\.las$",
                           full.names = TRUE))


for (i in seq_along(laz_files)) {
  h <- readLASheader(laz_files[[i]])
  laz_ext <- ext(h$`Min X`, h$`Max X`, h$`Min Y`, h$`Max Y`)
  overlaps <- relate(laz_ext, dtm_ext, "intersects")
  cat(sprintf("%s: %s\n", basename(laz_files[[i]]), ifelse(overlaps, "OK", "NO DTM")))
}