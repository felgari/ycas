# Copyright (c) 2015 Felipe Gallego. All rights reserved.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Description: This file process a csv file containing measurements for
# a set of astronomical objects in terms of magnitude, error and filter.
# The data is separated by filter and some curves are generated with
# the magnitudes of each column and also for some combinatios between the
# columns.
#

source("constants.R")

# Constants for the files names that store the data to process.
# These constants could be stored in the file constants.R.
#sDataFileName <- "magnitudes_file.csv"
#sCoordinatesFileName <- "coordinates_file.coo"

getColsNames <- function(data) {
  # Get the names of all the columns and only the columns that contains
  # magnitudes.
  #
  # Args:
  #   data: The data whose columns names are retrived.
  #
  # Returns:
  #   All the columns names and the columns names that contains magnitudes.
  #
  # Error handling
  #   
  
  # Get the names of the columns with data.
  cols <- list()
  cols_mag <- list()
  
  for ( n in names(data) ){
    if ( length(grep("MAG_", n)) > 0 ) {
      cols <- append(cols, list(n))
      cols_mag <- append(cols_mag, list(n))
    }    
    else if ( length(grep("ERR_", n)) > 0 ) {
      cols <- append(cols, list(n))
    }
  }
  
  return (list(cols, cols_mag))
}

calculateAverageData <- function(data, data.cols) {
  # Calculate average values for each day for all the data columns.
  #
  # Args:
  #   data: The data whose columns names are retrieved.
  #   data.cols: Columns names that contains data.
  #   mag.cols: Columns that contains magnitudes values.
  #
  # Returns:
  #   The data with the average values.
  #
  # Error handling
  #  

  # Add a new column to get MJD as integer value.
  data$MJD.int = as.integer(data$MJD)
  
  data.MJD.int = sort(unique(data$MJD.int))
  
  # Create the final data frame.
  data.avg = data.frame(MJD=data.MJD.int)
  
  for ( col in data.cols ) {
    data.avg[,col] = 0
  }
  
  # Calculate for each MJD, the mean values.
  for ( m in data.MJD.int ) {
    for ( co in cols ) {
      avg <- mean(data[data$MJD.int == m, c(co)], na.rm=TRUE)
      
      data.avg[data.avg$MJD == m, c(co)] <- avg
    }
  }
  
  return (data.avg)
}

calculatePlotLen <- function(mag.cols) {
  # Calculate the length for the plots.
  #
  # Args:
  #   mag.cols: Columns that contains magnitudes values.
  #
  # Returns:
  #   The length of the plot.  
  #
  # Error handling
  #  
  
  # Calculate the length necessary for the plot from the length of
  # the list of columns.
  num.mag <- length(mag.cols)
  
  len.plots <- num.mag / 2
  
  if (num.mag %% 2 > 0) {
    len.plots <- len.plots + 1
  }  
  
  return (len.plots)
}

plotMagnitudeData <- function(data, mag.cols) {
  # Plot all the magnitude values received.
  #
  # Args:
  #   data: The data whose columns are plotted.
  #   mag.cols: Columns that contains magnitudes values.
  #
  # Returns:
  #   Nothing  
  #
  # Error handling
  #  
  
  # Set plot features.
  par(pch = 22, col = "blue")
  
  # Calculate the length necessary for the plot.
  len.plots <- calculatePlotLen(mag.cols)
  
  # Set the number of plots in the frame.
  par(mfrow = c(2, len.plots))
  
  # Plot a curve for each magnitude column.
  for ( co in mag.cols ) {
    heading = paste("Star ", substr(co, 5, 10))
    
    plot(data$MJD, data[, co], 
         ylim = rev(range(na.omit(data[, co]))),
         main=heading, xlab="MJD", ylab="mag.")
    
    lines(data$MJD, data[, co])
  }    
}

plotDiffMagnitudeData <- function(data, mag.cols, filter) {
  # Plot a curve with the difference between the magnitude of the first
  # object (object of interest) and a mean of the rest of values.
  #
  # Args:
  #   data: The data whose columns are plotted.
  #   mag.cols: Columns that contains magnitudes values.
  #   filter: Name of the filter for these magnitudes.
  #
  # Returns:
  #   Nothing
  #
  # Error handling
  #  
  
  # Remove magnitude of the object of interest.
  diff.mag.cols <- mag.cols[! mag.cols %in% c("MAG_0")] 
  
  # Generate a data frame with the MJD, the magnitude for the object of 
  # interest and a mean of the rest of magnitudes.   
  data.dif <- data.frame(MJD=data$MJD, MAG_0=data$MAG_0, 
                         MEANS=rowMeans(data[,diff.mag.cols], na.rm = TRUE))
  
  # Add a column with the difference between the magnitude of the object of
  # interest and the mean of the rest of magnitudes.
  data.dif$dif <- data.dif$MAG_0 - data.dif$MEANS
  
  # Set the plt features.
  par(pch=22, col="blue")
  
  header = paste("Mag. diff. for filter ", filter)

  # Plot the difference calculated.  
  plot(data.dif$MJD, data.dif$dif, main=header, 
       ylim = rev(range(na.omit(data.dif$dif))),
       xlab="MJD", ylab="Mag. of object of interest - Mean")
  
  lines(data.dif$MJD, data.dif$dif)  
}

plotDiffOfMagnitudeCol <- function(data, mag.cols, filter) {
  # Plot curve with the difference between the magnitude of each
  # reference star and the mean of magnitudes of the rest of
  # reference stars.
  #
  # Args:
  #   data: The data whose columns are plotted.
  #   mag.cols: Columns that contains magnitudes values.
  #   filter: Name of the filter for these magnitudes.
  #
  # Returns:
  #   Nothing
  #
  # Error handling
  #  
  
  # Remove magnitude of the object of interest.
  ref.mag.cols <- mag.cols[! mag.cols %in% c("MAG_0")] 
  
  # Set the plt features.
  par(pch=22, col="blue")
  
  # Calculate the length necessary for the plot.
  len.plots <- calculatePlotLen(mag.cols)
  
  # Set the number of plots in the frame.
  par(mfrow = c(2, len.plots))
  
  # For each reference star plot the difference between its magnitude
  # and the mean of the magnitudes of the rest of reference stars.
  for ( i in 1:length(ref.mag.cols) ) {
    
    col <- ref.mag.cols[i]
    
    rest.mag.cols <- ref.mag.cols[! ref.mag.cols %in% c(col)]
    
    # Generate a data frame with the MJD, the magnitude for the object of 
    # interest and a mean of the rest of magnitudes.   
    data.dif <- data.frame(MJD=data$MJD, MAG=data[, c(col)], 
                           MEANS=rowMeans(data[,rest.mag.cols], na.rm = TRUE))
  
    # Add a column with the difference between the magnitude of the object of
    # interest and the mean of the rest of magnitudes.
    data.dif$dif <- data.dif$MEANS - data.dif$MAG   
    
    header = paste(col, paste(" - Mag. diff. for filter ", filter))
    
    # Plot the difference calculated.  
    plot(data.dif$MJD, data.dif$dif, main=header, xlab="MJD", 
         ylim = rev(range(na.omit(data.dif$dif))),
         ylab= paste("Mean - Mag. of reference star", col))
    
    lines(data.dif$MJD, data.dif$dif) 
  }
}

converFactorToNumeric <- function (df) {
  return (as.numeric(levels(df))[df])
}

readAndPrepareDataToPlot <- function() {
  # Read the data and prepare the data to plot.
  #
  # Args:
  #   None.
  #
  # Returns:
  #   The data just prepared.
  #
  # Error handling
  #  

  # Read the data.
  data <- read.csv(sDataFileName, sep = ",", header = FALSE,
                   numerals = "no.loss")
  
  coor <- read.csv(sCoordinatesFileName, sep = ",", header=FALSE)
  
  # Get the list of identifiers.
  identifiers <- coor[, 3]
  
  # Get the names of the columns to be used.
  mag.column.names <- paste("MAG_", identifiers, sep = "")
  err.column.names <- paste("ERR_", identifiers, sep = "")
  
  # Interleave the names of the columns for magnitudes and errors, 
  # as the data use this order for the columns.
  idx <- order(c(seq_along(mag.column.names), seq_along(err.column.names)))
  interl.col.names <- unlist(c(mag.column.names, err.column.names))[idx]
  
  column.names <- c("MJD", "FILTER", interl.col.names)
  
  # Set the names to the columns.
  names(data) <- column.names
  
  # Convert MJD to numeric.
  data$MJD <- converFactorToNumeric(data$MJD)
  
  # Sort by MJD.
  data <- data[with(data, order(MJD)), ]
  
  # Convert magnitude and error from factor to numeric.
  data[interl.col.names] <- lapply(data[interl.col.names], converFactorToNumeric)
  
  return (data)
}

data <- readAndPrepareDataToPlot()
  
# Separate data by filter.
data.B.filter <- data[data$FILTER=='B',]
data.V.filter <- data[data$FILTER=='V',]
data.R.filter <- data[data$FILTER=='R',]

# Get the names of the columns.
cols.names <- getColsNames(data.B.filter)

# Convert list to vectors
cols <- rapply(cols.names[1], c)
cols.mags <- rapply(cols.names[2], c)

# Plots without average.

# Plot data for each filter.
data.B.filter <- data.B.filter[with(data.B.filter, order(MJD)), ]
plotMagnitudeData(data.B.filter, cols.mags)

data.V.filter <- data.V.filter[with(data.V.filter, order(MJD)), ]
plotMagnitudeData(data.V.filter, cols.mags)

data.R.filter <- data.R.filter[with(data.R.filter, order(MJD)), ]
plotMagnitudeData(data.R.filter, cols.mags)

# Plot the curve for the difference between the magnitudes of the object of
# interest and the mean of the rest of objects.
par(mfrow = c(1, 3))

plotDiffMagnitudeData(data.B.filter, cols.mags, "B")
plotDiffMagnitudeData(data.V.filter, cols.mags, "V")
plotDiffMagnitudeData(data.R.filter, cols.mags, "R")

# Plots with average.

# Calculate average data for each filter.
data.avg.B <- calculateAverageData(data.B.filter, cols)
data.avg.V <- calculateAverageData(data.V.filter, cols)
data.avg.R <- calculateAverageData(data.R.filter, cols)

# Plot data for each filter.
plotMagnitudeData(data.avg.B, cols.mags)
plotMagnitudeData(data.avg.V, cols.mags)
plotMagnitudeData(data.avg.R, cols.mags)

# Plot the curve for the difference between the magnitudes of the object of
# interest and the mean of the rest of objects.
par(mfrow = c(1, 3))

plotDiffMagnitudeData(data.avg.B, cols.mags, "B")
plotDiffMagnitudeData(data.avg.V, cols.mags, "V")
plotDiffMagnitudeData(data.avg.R, cols.mags, "R")

# Remove columns with any NA value.
data.avg.B.noNA <- data.avg.B[ , colSums(is.na(data.avg.B)) == 0]
data.avg.V.noNA <- data.avg.V[ , colSums(is.na(data.avg.V)) == 0]
data.avg.R.noNA <- data.avg.R[ , colSums(is.na(data.avg.R)) == 0]

# Get the names of the columns.
cols.names.noNA <- getColsNames(data.avg.B.noNA)

# Convert list to vectors
cols.noNA <- rapply(cols.names.noNA[1], c)
cols.mags.noNA <- rapply(cols.names.noNA[2], c)

par(mfrow = c(1, 2))

plotDiffMagnitudeData(data.avg.B.noNA, cols.mags.noNA, "B")
plotDiffMagnitudeData(data.avg.V.noNA, cols.mags.noNA, "V")
plotDiffMagnitudeData(data.avg.R.noNA, cols.mags.noNA, "R")

# Plot the differences between reference stars in each filter.
plotDiffOfMagnitudeCol(data.B.filter, cols.mags, "B")
plotDiffOfMagnitudeCol(data.V.filter, cols.mags, "V")
plotDiffOfMagnitudeCol(data.R.filter, cols.mags, "R")
