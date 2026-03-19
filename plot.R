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
las <- normalize_height(las, dtm)

chm <- rasterize_canopy(las, res = 0.5, algorithm = p2r(0.2))
ttops <- locate_trees(chm, lmf(ws = function(x) x * 0.07 + 2, hmin = 5))

# Save to disk immediately before anything else
writeRaster(chm, "/Users/michael/dev/kullbergcraft/chm_temp.tif", overwrite = TRUE)
st_write(ttops, "/Users/michael/dev/kullbergcraft/ttops_temp.gpkg", delete_dsn = TRUE)

# Plot from the saved files
chm_df <- as.data.frame(chm, xy = TRUE)
colnames(chm_df) <- c("x", "y", "height")
chm_df <- chm_df[!is.na(chm_df$height), ]

ttops_df <- data.frame(st_coordinates(ttops), height = ttops$Z)
colnames(ttops_df) <- c("x", "y", "height")

ggplot() +
  geom_raster(data = chm_df, aes(x = x, y = y, fill = height)) +
  scale_fill_viridis_c(name = "Height (m)", option = "mako", na.value = "black") +
  geom_point(data = ttops_df, aes(x = x, y = y),
             colour = "red", size = 0.3, alpha = 0.6) +
  theme_void() +
  theme(
    plot.background = element_rect(fill = "black"),
    legend.text = element_text(colour = "white"),
    legend.title = element_text(colour = "white")
  ) +
  labs(title = "Canopy Height Model with detected tree tops",
       subtitle = "Kullberg, northern Sweden")

ggsave("lidar_treetops.png", width = 12, height = 10, dpi = 150)

# DSM - rasterize the raw (non-normalised) point cloud
las_raw <- readLAS(f, select = "xyzr")
dsm <- rasterize_canopy(las_raw, res = 0.5, algorithm = p2r(0.2))

# DTM - crop the DTM vrt to the tile extent
dtm_crop <- crop(dtm, ext(chm))

# Plot function to avoid repetition
plot_raster <- function(r, title, subtitle = "Kullberg, northern Sweden", 
                        palette = "mako", filename) {
  df <- as.data.frame(r, xy = TRUE)
  colnames(df) <- c("x", "y", "value")
  df <- df[!is.na(df$value), ]
  
  ggplot() +
    geom_raster(data = df, aes(x = x, y = y, fill = value)) +
    scale_fill_viridis_c(name = "Height (m)", option = palette, na.value = "black") +
    theme_void() +
    theme(
      plot.background = element_rect(fill = "black"),
      legend.text = element_text(colour = "white"),
      legend.title = element_text(colour = "white"),
      plot.title = element_text(colour = "white"),
      plot.subtitle = element_text(colour = "white")
    ) +
    labs(title = title, subtitle = subtitle)
  
  ggsave(filename, width = 12, height = 10, dpi = 150)
  cat(sprintf("Saved %s\n", filename))
}

plot_raster(dsm, "Digital Surface Model", filename = "dsm.png")
plot_raster(dtm_crop, "Digital Terrain Model", filename = "dtm.png")




# Get the extent of your tile as an sf object in WGS84 (required by maptiles)
tile_extent <- st_as_sf(st_as_sfc(st_bbox(chm, crs = crs(chm))))
tile_extent_wgs84 <- st_transform(tile_extent, 4326)

# Fetch satellite imagery
sat <- get_tiles(tile_extent_wgs84, provider = "Esri.WorldImagery", zoom = 15)

# Plot
sat_df <- as.data.frame(sat, xy = TRUE)
colnames(sat_df) <- c("x", "y", "r", "g", "b", "alpha")

# Combine RGB channels
sat_df$colour <- rgb(sat_df$r, sat_df$g, sat_df$b, maxColorValue = 255)

ggplot() +
  geom_raster(data = sat_df, aes(x = x, y = y, fill = colour)) +
  scale_fill_identity() +
  theme_void() +
  labs(title = "Satellite imagery", subtitle = "Kullberg, northern Sweden")

ggsave("satellite.png", width = 12, height = 10, dpi = 150)