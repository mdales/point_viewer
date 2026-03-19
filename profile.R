plan(sequential)
dtm_local <- vrt(dtm_files)
f <- "/Users/michael/dev/kullbergcraft/data/laz_files/70_5/23F024_707_59_0025.laz"
t0 <- proc.time()
las <- readLAS(f, select = "xyzr")
las <- normalize_height(las, dtm_local)
chm <- rasterize_canopy(las, res = 0.5, algorithm = p2r(0.2))
ttops <- locate_trees(chm, lmf(ws = function(x) x * 0.07 + 2, hmin = 5))
cat(sprintf("Time: %.1fs, Trees: %d\n", (proc.time() - t0)["elapsed"], nrow(ttops)))