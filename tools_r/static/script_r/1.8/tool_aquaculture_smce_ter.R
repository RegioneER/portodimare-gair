shhh <- suppressPackageStartupMessages
shhh(library(raster))
shhh(library(rgdal))
shhh(library(maptools))
shhh(library(rgeos))
shhh(library(RColorBrewer))
shhh(library(ggplot2))
shhh(library(scales))
shhh(library(rasterVis))
shhh(library(gridExtra))


args = commandArgs(trailingOnly = TRUE)
weights <- read.csv(args[1],sep=";",row.names=1)
userpath <- args[2]
dir_output <- args[3]


read_criteria <- function(userpath){
  
  ras_files <- list.files(userpath,  pattern = ".tif")
  
  batch_ras<- function(ras_files){
    layer_name <- as.character(gsub(".tif","",ras_files))
    outfiles <- paste0(userpath, ras_files)
    ras_spdf <-raster(outfiles)
  }
  
  #########################################
  # Pass batch function to raster list #
  #########################################
  
batch_ras_list <- lapply(ras_files, batch_ras)
  
  #--Extract each element in list into its own object
  
  for (i in seq(batch_ras_list)){
    
    batch_ras_list[[i]] <-  setMinMax(batch_ras_list[[i]])
    batch_ras_list[[i]] <-  (batch_ras_list[[i]]-maxValue(batch_ras_list[[i]]))/(minValue(batch_ras_list[[i]])-maxValue(batch_ras_list[[i]]))
    batch_ras_list[[i]] <-  resample(batch_ras_list[[i]],batch_ras_list[[1]],method="bilinear") ## resample raster files
  }
 
  input=batch_ras_list
  return(input)
}

####################################
# Batch shapefile loading function #
####################################
read_constraints <- function(userpath){
  
  shp_files <- list.files(userpath,  pattern = "\\.shp$")
  
  batch_shp<- function(shp_files){
    layer_name <- as.character(gsub(".shp","",shp_files))
    shp_spdf <- readOGR(dsn = userpath, stringsAsFactors = FALSE, verbose = FALSE, 
                     useC = TRUE, dropNULLGeometries = TRUE, addCommentsToPolygons = TRUE,
                     layer = layer_name, require_geomType = NULL, 
                     p4s = NULL, encoding = 'ESRI Shapefile')

    shp_spdf <- readOGR(dsn = userpath, stringsAsFactors = FALSE, verbose = FALSE, useC = TRUE, dropNULLGeometries = TRUE, addCommentsToPolygons = TRUE, layer = layer_name, require_geomType = NULL, p4s = NULL, encoding = 'ESRI Shapefile')
    shp_spdf_trans <- spTransform(shp_spdf,
                                 CRS("+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"))
    shp_spdf_buff <- gBuffer(shp_spdf_trans,width = 500)
    shp_spdf_trans2 <- spTransform(shp_spdf_buff,CRS("+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"))
}

#########################################
# Pass batch function to shapefile list #
#########################################

batch_shp_list <- lapply(shp_files, batch_shp)

#--Extract each element in list into its own object

for (i in seq(batch_shp_list)){
  batch_shp_list[[i]] <- spTransform(batch_shp_list[[i]],
                                    CRS("+proj=utm +zone=33 +datum=WGS84 +units=m +no_defs +ellps=WGS84 +towgs84=0,0,0"))
  batch_shp_list[[i]] <- gBuffer(batch_shp_list[[i]],width = 500)
  batch_shp_list[[i]] <- spTransform(batch_shp_list[[i]],CRS("+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"))
}

constraints <- batch_shp_list
m <- do.call(bind, constraints) 
input_constraints=list(constraints,m)
return(input_constraints)
}

suitability_f <- function(userpath,input,input_constraints) {
  suitability_weights <- weights

  constraints=input_constraints[[1]]
  m=input_constraints[[2]]
  
  for (i in seq(input)){
    input[[i]] <-  (input[[i]] * suitability_weights[i,])
    criteria <- stack(input)
  }
  
  suitability <- sum(criteria)
  crs(suitability) <-  "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"
  
  suitability_constraints <- mask(suitability,m,inverse=T)
  
  writeRaster(suitability,file.path(dir_output,"aquaculture_suitability.tif"),overwrite=TRUE)
  writeRaster(suitability_constraints,file.path(dir_output,"aquaculture_suitability_constraints.tif"),overwrite=TRUE)
  
  cuts=as.data.frame(c(0.25,0.35,0.5,0.75,1.0))
  cuts=cuts$`c(0.25, 0.35, 0.5, 0.75, 1)` #set breaks
  colours =c("#D7191C","#FDAE61","#FFFFC0","#A6D96A","#1A9641")
  p1 <- print(gplot(suitability) + geom_tile(aes(fill = value)) +
                scale_fill_gradientn(colours=colours,na.value = "white", guide = "colourbar",
                                     aesthetics = "fill", breaks=cuts,colors=colours, 
                                     limits = c(0, 1),"Suitability" ,
                                     labels=as.character(cuts)) +
                labs(title = "Aquaculture Suitability", x = "Longitude", y = "Latitude")+
                theme(legend.position = 'right', 
                      legend.spacing.x = unit(0.5, 'cm'),
                      legend.key.size = unit(0.8, 'cm'))+
                coord_equal())
  
  
  p2 <- print(gplot(suitability_constraints) + geom_tile(aes(fill = value)) +
                scale_fill_gradientn(colours=colours,na.value = "white", guide = "colourbar",
                                     aesthetics = "fill", breaks=cuts,colors=colours, 
                                     limits = c(0, 1),"Suitability" ,
                                     labels=as.character(cuts)) +
                labs(title = "Aquaculture Suitability considering the constraints", x = "Longitude", y = "Latitude")+
                theme(legend.position = 'right', 
                      legend.spacing.x = unit(0.5, 'cm'),
                      legend.key.size = unit(0.8, 'cm'))+
                coord_equal())
  
  
  intervals=c(0,cuts)
  # Km2 frequency per suitability class
  ncells_S <- sum(!is.na(suitability[]))
  # Count frequencies and calculate percentage
  t_S <- table(cut(as.vector(suitability), intervals, include.lowest=TRUE)) / ncells_S * 100
  df_S <- data.frame(round(t_S, digits=2))
  df_S$Var1 <-as.character(cuts)
  
  # Reorder following a precise order
  df_S$Var1 <- factor(df_S$Var1, levels=unique(df_S$Var1))
  
  p_S <- print(ggplot(df_S, aes(x = Var1,y=Freq)) +  
                 geom_bar(stat="identity",fill=colours)+
                 labs(title="Aquaculture Suitability Percentage", 
                      x="Suitability clusterization", y = "Percentage")+
                 theme_minimal())
  
  # Km2 frequency per suitability class considering the constraints
  ncells_SC <- sum(!is.na(suitability_constraints[]))
  # Count frequencies and calculate percentage
  t_SC <- table(cut(as.vector(suitability_constraints), intervals, include.lowest=TRUE)) / ncells_SC * 100
  df_SC <- data.frame(round(t_SC, digits=2))
  df_SC$Var1 <- as.character(cuts)
  
  # Reorder following a precise order
  df_SC$Var1 <- factor(df_SC$Var1, levels=unique(df_SC$Var1))
  
  p_SC <- print(ggplot(df_SC, aes(x = Var1,y=Freq)) +  
                  geom_bar(stat="identity",fill=colours)+
                  labs(title="Aquaculture Suitability Percentage considering the constraints", 
                       x="Suitability clusterization", y = "Percentage")+
                  theme_minimal())
  
  
  ggsave(file.path(dir_output,"aquaculture_suitability.pdf"), arrangeGrob(p1,p2))
  ggsave(file.path(dir_output,"aquaculture_suitability_histogram.pdf"), arrangeGrob(p_S, p_SC))

  
  output=list(suitability_weights,suitability,suitability_constraints)
  
  return(output)
  }


################################################
###             MAIN PROCESS              ######
################################################

input_data <- read_criteria(userpath)
constraints_shp <- read_constraints(userpath)
suitability <- suitability_f(userpath,input_data,constraints_shp)


