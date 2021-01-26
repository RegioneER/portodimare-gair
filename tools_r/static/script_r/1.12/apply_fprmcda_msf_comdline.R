# ---- Run an application of fprmcda for Medium-Scale Fisheries module passing arguments on the commandline
# Inputs arguments:
# Application Domain, Model boundaries, coastline, pairwise matrix, 
# Fishing Gear per port, no_take boolean, components
# Examples
# Rscript apply_fprmcda_msf_comdline.r Greece 20.26699 21.50498 37.9079 38.9125 coastLine components_cuts_grades_TR1224.csv components_cuts_grades_TR2440.csv components_cuts_grades_PS.csv pairwise_matrix_TR.csv pairwise_matrix_PS.csv Fishing_Gear_TR1224.csv Fishing_Gear_TR2440.csv Fishing_Gear_PS.csv no_take_TR.tif no_take_PS.tif bathymetry.tif coast_dist.tif 
# legislation_TR.tif legislation_PS.tif chlorophyl.tif fpc_ssf.tif

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
  
# Load input parameters for Trawlers (TR) and Purse seines (PS) related to the grades of components
parameters_file <- args[9]
comp_cuts_grades_TR1224 <- read.csv(parameters_file, header = TRUE, sep = ",")

parameters_file <- args[10]
comp_cuts_grades_TR2440 <- read.csv(parameters_file, header = TRUE, sep = ",")

parameters_file <- args[11]
comp_cuts_grades_PS <- read.csv(parameters_file, header = TRUE, sep = ",")
  
# Load pairwise matrix for Trawlers (TR) and Purse seines (PS) for Analytic Hierarchy Process
ahp_file_TR <- args[12]
pairwise_matrix_TR <- read.csv(ahp_file_TR, header = TRUE, row.names = 1, sep = ",")

ahp_file_PS <- args[13]
pairwise_matrix_PS <- read.csv(ahp_file_PS, header = TRUE, row.names = 1, sep = ",")
  
# Load fishing gear from port locations for Trawlers 12-24m and 24-40m (TR1224, TR2440) and Purse seines (PS) 
gt_file        <- args[14]
port_gt_TR1224 <- read.csv(gt_file, sep = ",")

gt_file        <- args[15]
port_gt_TR2440 <- read.csv(gt_file, sep = ",") 

gt_file        <- args[16]
port_gt_PS     <- read.csv(gt_file, sep = ",") 
  
# Load no_take zones for Trawlers (TR) and Purse seines (PS)
no_take_file <- args[17]
msf_comp_no_take_zones_TR = raster(no_take_file)
msf_comp_no_take_zones_TR <- crop(msf_comp_no_take_zones_TR, ext)
crs(msf_comp_no_take_zones_TR) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

no_take_file <- args[18]
msf_comp_no_take_zones_PS = raster(no_take_file)
msf_comp_no_take_zones_PS <- crop(msf_comp_no_take_zones_PS, ext)
crs(msf_comp_no_take_zones_PS) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# Load components and create a composite raster
ncomp <- length(args)-18  # number of components, skip first 16 input arguments
raster_list = c()
for (i in 1:(ncomp-1)){
  raster_file <- args[18+i]
  rst <- raster(raster_file)
  crs(rst) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  raster_list <- append(raster_list, rst)
}
msf_comp = brick(x = raster_list) 

# Crop rasters on the domain boundary
msf_comp <- crop(msf_comp, ext)

# Distinct components for Trawlers and Purse seines
msf_comp_TR = dropLayer(msf_comp, 4)
msf_comp_PS = dropLayer(msf_comp, 3)

# Load fishing pressure index extracted after running the Small-Scale Fisheries module (last argument)
FPc_SSF <- raster(args[length(args)])

# Initialize the graded raster and update its values following cuts and grades from components_cuts_grades csv files
graded_raster_list_TR1224 = c()
graded_raster_list_TR2440 = c()
graded_raster_list_PS     = c()

# Assign in a dynamic way the components as layer names in the graded composite raster and apply grades 
for (i in 1:(ncomp-2)){
   if (names(msf_comp_TR)[i] != "legislation_PS"){
      r_comp_TR            =  eval(parse(text = noquote(paste0('msf_comp_TR$', names(msf_comp_TR)[i]))))
      r_comp_graded_TR1224 =  eval(parse(text = noquote(paste0('msf_comp_TR$', names(msf_comp_TR)[i]))))
      r_comp_graded_TR2440 =  eval(parse(text = noquote(paste0('msf_comp_TR$', names(msf_comp_TR)[i]))))
      cuts_TR1224          <- eval(parse(text = noquote(paste0('comp_cuts_grades_TR1224$', names(msf_comp_TR)[i], "_cuts"))))
      grades_TR1224        <- eval(parse(text = noquote(paste0('comp_cuts_grades_TR1224$', names(msf_comp_TR)[i], "_grades"))))
      cuts_TR2440          <- eval(parse(text = noquote(paste0('comp_cuts_grades_TR2440$', names(msf_comp_TR)[i], "_cuts"))))
      grades_TR2440        <- eval(parse(text = noquote(paste0('comp_cuts_grades_TR2440$', names(msf_comp_TR)[i], "_grades"))))
      # remove NaNs
      k_tr1224 = which(is.na(cuts_TR1224)); if (length(k_tr1224)>0) {cuts_TR1224 <- cuts_TR1224[-k_tr1224]; grades_TR1224 <- grades_TR1224[-k_tr1224]}
      k_tr2440 = which(is.na(cuts_TR2440)); if (length(k_tr2440)>0) {cuts_TR2440 <- cuts_TR2440[-k_tr2440]; grades_TR2440 <- grades_TR2440[-k_tr2440]}
      # grade rasters
      values(r_comp_graded_TR1224) <- fgrade(values(r_comp_TR), cuts_TR1224, grades_TR1224)
      graded_raster_list_TR1224    <- append(graded_raster_list_TR1224, r_comp_graded_TR1224)
      values(r_comp_graded_TR2440) <- fgrade(values(r_comp_TR), cuts_TR2440, grades_TR2440)
      graded_raster_list_TR2440    <- append(graded_raster_list_TR2440, r_comp_graded_TR2440)
    }
  
  if (names(msf_comp_PS)[i] != "legislation_TR"){
     r_comp_PS        =  eval(parse(text = noquote(paste0('msf_comp_PS$', names(msf_comp_PS)[i]))))
     r_comp_graded_PS =  eval(parse(text = noquote(paste0('msf_comp_PS$', names(msf_comp_PS)[i]))))
     cuts_PS          <- eval(parse(text = noquote(paste0('comp_cuts_grades_PS$', names(msf_comp_PS)[i], "_cuts"))))
     grades_PS        <- eval(parse(text = noquote(paste0('comp_cuts_grades_PS$', names(msf_comp_PS)[i], "_grades"))))
     # remove NaNs
     k_ps     = which(is.na(cuts_PS));     if (length(k_ps)>0) {cuts_PS <- cuts_PS[-k_ps];  grades_PS <- grades_PS[-k_ps]}
     # grade rasters
     values(r_comp_graded_PS) <- fgrade(values(r_comp_PS), cuts_PS, grades_PS)
     graded_raster_list_PS    <- append(graded_raster_list_PS, r_comp_graded_PS)
  }
  
}
# Merge graded rasters
msf_comp_graded_TR1224 = brick(x = graded_raster_list_TR1224) 
msf_comp_graded_TR2440 = brick(x = graded_raster_list_TR2440) 
msf_comp_graded_PS = brick(x = graded_raster_list_PS) 

# --- Apply Multi-criteria Decision Analysis --- #
# Apply AHP to pairwise matrix defined to calculate weights, consistency ratio, e.t.c.
ahp_out_TR = ahp_optim(as.matrix(pairwise_matrix_TR))
ahp_out_PS = ahp_optim(as.matrix(pairwise_matrix_PS))

# Apply of Weighted Linear Combination to calculate Sc = Sum(weights * graded_data)
Sc_TR1224 = sum(ahp_out_TR$weights * msf_comp_graded_TR1224)
Sc_TR2440 = sum(ahp_out_TR$weights * msf_comp_graded_TR2440)
Sc_PS     = sum(ahp_out_PS$weights * msf_comp_graded_PS)

# Normalise Sc
Sc_TR1224 <- FuzzyMember(Sc_TR1224, "raster")
Sc_TR2440 <- FuzzyMember(Sc_TR2440, "raster")
Sc_PS     <- FuzzyMember(Sc_PS, "raster")

# Plot Fish Suitability Index (Sc)
tmap_mode("plot")
m_fish_suit_TR1224 <- tm_shape(Sc_TR1224) + tm_raster("layer", style = "cont", palette = "Blues", title = "", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fish Suitability Index (Sc) for Trawlers 12-24m", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey75", frame = TRUE)
tmap_save(m_fish_suit_TR1224, filename = paste0(output_dir,paste0("/", "Fish_Suitability_Index_TR1224","_", app_domain, ".png")), height=7)

tmap_mode("plot")
m_fish_suit_TR2440 <- tm_shape(Sc_TR2440) + tm_raster("layer", style = "cont", palette = "Blues", title = "", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fish Suitability Index (Sc) for Trawlers 24-40m", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey75", frame = TRUE)
tmap_save(m_fish_suit_TR2440, filename = paste0(output_dir,paste0("/", "Fish_Suitability_Index_TR2440","_", app_domain, ".png")), height=7)

tmap_mode("plot")
m_fish_suit_PS <- tm_shape(Sc_PS) + tm_raster("layer", style = "cont", palette = "Blues", title = "", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fish Suitability Index (Sc) for Purse seines", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey75", frame = TRUE)
tmap_save(m_fish_suit_PS, filename = paste0(output_dir,paste0("/", "Fish_Suitability_Index_PS","_", app_domain, ".png")), height=7)

# Apply IDW interpolation to fishing gear per port (port_gt) data; use graded_comp_msf$Bathymetry as mask.raster
port_gt_TR1224_intp <- idwfg(port_gt_TR1224, msf_comp)
port_gt_TR2440_intp <- idwfg(port_gt_TR2440, msf_comp)
port_gt_PS_intp     <- idwfg(port_gt_PS, msf_comp)

port_gt_TR1224_intp$raster <- crop(port_gt_TR1224_intp$raster, ext)
crs(port_gt_TR1224_intp$raster) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

port_gt_TR2440_intp$raster <- crop(port_gt_TR2440_intp$raster, ext)
crs(port_gt_TR2440_intp$raster) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

port_gt_PS_intp$raster <- crop(port_gt_PS_intp$raster, ext)
crs(port_gt_PS_intp$raster) <- "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

# Spatialize fishing port locations (Lon, Lat) and convert to SpatialPointsDataFrame
fports <- function(ploc, rloc){
  xy = ploc[,1:2]
  p <- SpatialPoints(xy)
  proj4string(p) = CRS(projection(rloc))
  nam = c()
  for(i in 1:nrow(xy)) { nam <- c(nam, paste("f", i, sep = "")) }
  df <- data.frame(attr1 = nam, gear = ploc[,3])
  fp <- SpatialPointsDataFrame(p, df)
  fp
}

fg_TR1224 = fports(port_gt_TR1224, port_gt_TR1224_intp$raster)
fg_TR2440 = fports(port_gt_TR2440, port_gt_TR2440_intp$raster)
fg_PS     = fports(port_gt_PS, port_gt_PS_intp$raster)

# Plot Vessel activity
tmap_mode("plot")
m_gt_TR1224 <- tm_shape(port_gt_TR1224_intp$raster) + tm_raster("layer", style = "cont", title = "Interpolation", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_shape(fg_TR1224) + tm_bubbles(size = "gear", col = "blue",  title.size = "Data") +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Interpolated Fishing Gear for Trawlers 12-24m", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey95", frame = TRUE)
tmap_save(m_gt_TR1224, filename = paste0(output_dir,paste0("/", "GT_interpolated_TR1224","_", app_domain, ".png")), height=7)

tmap_mode("plot")
m_gt_TR2440 <- tm_shape(port_gt_TR2440_intp$raster) + tm_raster("layer", style = "cont", title = "Interpolation", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_shape(fg_TR2440) + tm_bubbles(size = "gear", col = "blue",  title.size = "Data") +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Interpolated Fishing Gear for Trawlers 24-40m", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey95", frame = TRUE)
tmap_save(m_gt_TR2440, filename = paste0(output_dir,paste0("/", "GT_interpolated_TR2440","_", app_domain, ".png")), height=7)

tmap_mode("plot")
m_gt_PS <- tm_shape(port_gt_PS_intp$raster) + tm_raster("layer", style = "cont", title = "Interpolation", legend.reverse = TRUE) +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_shape(fg_PS) + tm_bubbles(size = "gear", col = "blue",  title.size = "Data") +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Interpolated Fishing Gear for Purse seines", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color = "grey95", frame = TRUE)
tmap_save(m_gt_PS, filename = paste0(output_dir,paste0("/", "GT_interpolated_PS","_", app_domain, ".png")), height=7)

# Normalise interpolated fishing gear
port_gt_TR1224_intp$Ac = FuzzyMember(port_gt_TR1224_intp$raster, "raster")
port_gt_TR2440_intp$Ac = FuzzyMember(port_gt_TR2440_intp$raster, "raster")
port_gt_PS_intp$Ac     = FuzzyMember(port_gt_PS_intp$raster, "raster")

# Calculate Fishing Pressure: FPc = Sc * port_gt_intp$raster * No_Take_Zones
FPc_TR1224 = Sc_TR1224 * port_gt_TR1224_intp$raster * msf_comp_no_take_zones_TR
FPc_TR2440 = Sc_TR2440 * port_gt_TR2440_intp$raster * msf_comp_no_take_zones_TR
FPc_PS     = Sc_PS * port_gt_PS_intp$raster * msf_comp_no_take_zones_PS

# Normalise different FPcs
FPc_TR1224 <- FuzzyMember(FPc_TR1224, "raster")
FPc_TR2440 <- FuzzyMember(FPc_TR2440, "raster")
FPc_PS     <- FuzzyMember(FPc_PS, "raster")

# Compute final FPc from small and medium-scale fisheries
FPc = FPc_TR1224 + FPc_TR2440 + FPc_PS + FPc_SSF
FPc <- FuzzyMember(FPc, "raster")

# Plot Fishing Pressure (FPc)
tmap_mode("plot")
m_fish_pr_TR1224 <- tm_shape(FPc_TR1224) + tm_raster("layer", palette = "Blues", title = "") +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fishing Pressure (FPc) for Trawlers 12-24m", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color="grey75", frame = TRUE)
tmap_save(m_fish_pr_TR1224, filename = paste0(output_dir,paste0("/", "Fishing_Pressure_TR1224","_", app_domain, ".png")), height=7)

tmap_mode("plot")
m_fish_pr_TR2440 <- tm_shape(FPc_TR2440) + tm_raster("layer", palette = "Blues", title = "") +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fishing Pressure (FPc) for Trawlers 24-40m", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color="grey75", frame = TRUE)
tmap_save(m_fish_pr_TR2440, filename = paste0(output_dir,paste0("/", "Fishing_Pressure_TR2440","_", app_domain, ".png")), height=7)

tmap_mode("plot")
m_fish_pr_PS <- tm_shape(FPc_PS) + tm_raster("layer", palette = "Blues", title = "") +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Fishing Pressure (FPc) for Purse seines", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color="grey75", frame = TRUE)
tmap_save(m_fish_pr_PS, filename = paste0(output_dir,paste0("/", "Fishing_Pressure_PS","_", app_domain, ".png")), height=7)
 
tmap_mode("plot")
m_fish_pr <- tm_shape(FPc) + tm_raster("layer", palette = "Blues", title = "") +
  tm_shape(map_domain) + tm_polygons(xlim = c(round(ext[1],1), round(ext[2],1)), ylim = c(round(ext[3],1), round(ext[4],1))) +
  tm_grid(labels.inside.frame = FALSE, n.x = 5, n.y = 4, col = "black", labels.size = 1)+
  tm_layout(panel.labels = "Composite Fishing Pressure (FPc)", outer.margins = c(.1,.1,.1,.1)) +
  tm_legend(position = c("right", "top"), bg.color="grey75", frame = TRUE)
tmap_save(m_fish_pr, filename = paste0(output_dir,paste0("/", "Fishing_Pressure","_", app_domain, ".png")), height=7)
