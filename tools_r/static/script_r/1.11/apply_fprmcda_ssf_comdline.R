# ---- Run an application of fprmcda passing arguments in commandline
# Inputs arguments:
# Application Domain, Model boundaries, coastline, pairwise matrix, 
# Fishing Gear per port, no_take boolean, components
# Examples
# Rscript apply_fprmcda_ssf_comdline.r /userpath /output_dir Greece 20.26699 21.50498 37.9079 38.9125 coastLine components_cuts_grades.csv pairwise_matrix.csv Fishing_Gear.csv no_take.tif bathymetry.tif coast_dist.tif marine_traffic.tif
# Rscript apply_fprmcda_ssf_comdline.r /userpath /output_dir Greece 20.26699 21.50498 37.9079 38.9125 coastLine components_cuts_grades.csv pairwise_matrix.csv Fishing_Gear.csv no_take.tif bathymetry.tif coast_dist.tif legislation.tif trawl_fleet.tif seine_fleet.tif marine_traffic.tif chlorophyl.tif

#! /usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)
hh <- paste(unlist(args),collapse=' ')
listoptions <- unlist(strsplit(hh,'--'))[-1]
options.args <- sapply(listoptions,function(x){
  unlist(strsplit(x, ' '))[-1]
}, simplify=FALSE)
options.names <- sapply(listoptions,function(x){
  option <-  unlist(strsplit(x, ' '))[1]
})
names(options.args) <- unlist(options.names)

# Loading libraries
library(rgdal)        # load shapefiles
library(raster)       # handle raster objects
library(RColorBrewer) # define colorbars for raster
library(rasterVis)    # plot raster objects
library(maps)         # display of maps
library(mapdata)      # load map databases
library(maptools)     # mapping tool
library(latticeExtra) # graphical utilities
library(FuzzyAHP)     # Analytic Hierarchy Process
library(spatstat)     # spatial statistics tool
library(phylin)       # perform IDW interpolation
library(tmap)         # provide plots with tmap
library(tmaptools)    # auxiliary for tmap
library(fprmcda)      # package for applying MCDA

# Output dir
userpath <- args[1]
output_dir <- args[2]
app_domain <- args[3]

# ---- Load data and parameters ---- #  
# Specify the extension of components based on domain_boundary
ext <- c(as.numeric(args[4]), as.numeric(args[5]), as.numeric(args[6]), as.numeric(args[7]))
  
# Load coastline
coast_file <- args[8]
map_domain <- readOGR(userpath, coast_file)  
  
# Load input parameters related to grades of components
parameters_file <- args[9]
comp_cuts_grades <- read.csv(parameters_file, header = TRUE, sep = ",")
  
# Load pairwise matrix for Analytic Hierarchy Process
ahp_file <- args[10]
pairwise_matrix <- read.csv(ahp_file, header = TRUE, row.names = 1, sep = ",")
  
# Load fishing gear from port locations  
gt_file   <- args[11] 
port_gt <- read.csv(gt_file, sep = ",") 
  
# Load no_take zones
no_take_file <- args[12]
ssf_comp_no_take_zones = raster(no_take_file)
ssf_comp_no_take_zones <- crop(ssf_comp_no_take_zones, ext)
crs(ssf_comp_no_take_zones) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# Load components and create a composite raster
ncomp <- length(args)-12  # number of components
raster_list = c()
for (i in 1:ncomp){
  raster_file <- args[12+i]
  rst <- raster(raster_file)
  crs(rst) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  raster_list <- append(raster_list, rst)
}
ssf_comp = brick(x = raster_list) 
  
# Crop rasters on the domain boundary
ssf_comp <- crop(ssf_comp, ext)

# Initialize the graded raster and update its values following cuts and grades from "components_cuts_grades.csv"
graded_raster_list = c()
# Assign in a dynamic way the components as layer names in the graded composite raster
# and apply grades 
for (i in 1:ncomp){
  r_comp_graded =  eval(parse(text = noquote(paste0('ssf_comp$', names(ssf_comp)[i]))))
  r_comp = eval(parse(text = noquote(paste0('ssf_comp$', names(ssf_comp)[i]))))
  cuts <- eval(parse(text = noquote(paste0('comp_cuts_grades$', names(ssf_comp)[i], "_cuts"))))
  grades <- eval(parse(text = noquote(paste0('comp_cuts_grades$', names(ssf_comp)[i], "_grades"))))
  # remove potential NaNs
  k = which(is.na(cuts)); cuts <- cuts[-k]; grades <- grades[-k]
  values(r_comp_graded) <- fgrade(values(r_comp), cuts, grades)
  graded_raster_list <- append(graded_raster_list, r_comp_graded)
}
ssf_comp_graded = brick(x = graded_raster_list) 
names(ssf_comp_graded) <- names(ssf_comp)
  
# Build new pairwise matrix for ncomp components based on "pairwise_matrix.csv"
pairwise_matrix_comp <- diag(ncomp)
comp_index <- numeric(ncomp)
for (i in 1:ncomp){
  comp_index[i] = which(colnames(pairwise_matrix) == names(ssf_comp)[i])
}
  
for (j in seq(1:ncomp)){
  for (i in seq(1:ncomp)){
    if (i!=j){
      pairwise_matrix_comp[i,j] = pairwise_matrix[comp_index[i], comp_index[j]]
}}}
  
# --- Apply Multi-criteria Decision Analysis --- #
# Apply AHP to pairwise matrix defined to calculate weights, consistency ratio, e.t.c.
ahp_out = ahp_optim(pairwise_matrix_comp)

# Apply of Weighted Linear Combination to calculate Sc = Sum(weights * graded_data)
Sc = sum(ahp_out$weights * ssf_comp_graded)

# Normalise Sc
Sc <- FuzzyMember(Sc, "raster")

# Plot the Fish Suitability Index (Sc)
tmap_mode("plot")
m_fish_suit <- tm_shape(Sc) + tm_raster("layer", style = "cont", palette = "Blues", title = "", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fish Suitability Index (Sc)", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey75", frame = TRUE)
  tmap_save(m_fish_suit, filename = paste0(output_dir, paste0("/", "Fish_Suitability_Index","_", app_domain, ".png")), height=7)
  
# Apply IDW interpolation to fishing gear per port (port_gt) data; use graded_comp_ssf$Bathymetry as mask.raster
port_gt_intp <- idwfg(port_gt, ssf_comp)
  
# Spatialize fishing gear data points (Lon, Lat) and convert to SpatialPointsDataFrame
xy = port_gt[,1:2]
p <- SpatialPoints(xy)
proj4string(p) = CRS(projection(port_gt_intp$raster))
nam = c()

for(i in 1:nrow(xy)) { nam <- c(nam, paste("f", i, sep = ""))}
  df <- data.frame(attr1 = nam, gear = port_gt[,3])
  fgear <- SpatialPointsDataFrame(p, df)
  port_gt_intp$raster <- crop(port_gt_intp$raster, ext)
  crs(port_gt_intp$raster) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  
# Plot interpolated fishing gear
tmap_mode("plot")
m_gt <- tm_shape(port_gt_intp$raster) + tm_raster("layer", style = "cont", title = "Interpolation", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_shape(fgear) + tm_bubbles(size = "gear", col = "blue",  title.size = "Data") +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fishery Activity", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey95", frame = TRUE)
  tmap_save(m_gt, filename = paste0(output_dir, paste0("/", "GT_interpolated","_", app_domain, ".png")), height=7)
  
# Normalise interpolated fishing gear
port_gt_intp$Ac = FuzzyMember(port_gt_intp$raster, "raster")
  
# Calculate Fishing Pressure: FPc = Sc * port_gt_intp$raster * No_Take_Zones
FPc = Sc * port_gt_intp$raster * ssf_comp_no_take_zones
  
# Normalise FPc
FPc <- FuzzyMember(FPc, "raster")
  
# Plot Fishing Pressure (FPc)
tmap_mode("plot")
m_fish_pr <- tm_shape(FPc) + tm_raster("layer", palette = "Blues", title = "") +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fishing Pressure (FPc)", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color="grey75", frame = TRUE)
  tmap_save(m_fish_pr, filename = paste0(output_dir, paste0("/", "Fishing_Pressure","_", app_domain, ".png")), height=7)
  
# save fishing pressure output for Medium-Scale Fisheries Module
FPc <- ratify(FPc)
levels(FPc)[[1]]$NAME <- letters[1:nrow(levels(FPc)[[1]])]
writeRaster(FPc, paste0(output_dir,paste0("/","fpc_ssf.tif")),  overwrite=TRUE)
