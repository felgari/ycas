#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2014 Felipe Gallego. All rights reserved.
#
# This file is part of ycas: https://github.com/felgari/ycas
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

import os
import logging

# Log levels, taken from logging.
LOG_LEVELS = { "CRITICAL" : logging.CRITICAL,
              "ERROR": logging.ERROR,
              "WARNING": logging.WARNING,
              "INFO": logging.INFO,
              "DEBUG": logging.DEBUG }

DEFAULT_LOG_LEVEL_NAME = "WARNING"

DEFAULT_LOG_FILE_NAME = "ycas_log.txt"

DEFAULT_DIFF_PHOT_FILE_NAME_PREFIX = "diff_mag"

# Directories.
BIAS_DIRECTORY = 'bias'
FLAT_DIRECTORY = 'flat'
DATA_DIRECTORY = 'data'

# File extensions.
FIT_FILE_EXT = "fit"
CATALOG_FILE_EXT = 'cat'
MAGNITUDE_FILE_EXT = "mag"
CSV_FILE_EXT = "csv"
TSV_FILE_EXT = "tsv"
RDLS_FILE_EXT = "rdls"
COORD_FILE_EXT = "coo"
INDEX_FILE_PATTERN = '-indx.xyls'
DATA_FINAL_PATTERN = "_final.fit"
DATA_ALIGN_PATTERN = "_align.fit"

# Directory paths.
PATH_FROM_FLAT_TO_BIAS = os.path.join("..", "..", BIAS_DIRECTORY)
PATH_FROM_DATA_TO_BIAS = os.path.join("..", "..", BIAS_DIRECTORY)
PATH_FROM_DATA_TO_FLAT = os.path.join("..", "..", FLAT_DIRECTORY)

# Special characters in file names.
BIAS_STRING = 'bias'
FLAT_STRING = 'flat'
DATANAME_CHAR_SEP = "-"
FIRST_DATA_IMG = "001"
FILTERS = [ 'V', 'B', 'R', 'CN', 'Cont4430', 'Cont6840' ]

MASTERBIAS_FILENAME = "bias_avg.fit"
MASTERFLAT_FILENAME = "flat_avg.fit"
WORK_FILE_SUFFIX = "_work"
NORM_FILE_SUFFIX = "_norm"
DATA_FINAL_SUFFIX = "_final"
INST_MAG_SUFFIX = "_inst_mag"
ALL_INST_MAG_SUFFIX = "_all_inst_mag"
CORR_MAG_SUFFIX = "_ec_mag"
CAL_MAG_SUFFIX = "_cal_mag"

IMSTAT_FIRST_VALUE = 1

# External commands
ASTROMETRY_COMMAND = "solve-field"

# Astrometry option to use sextractor.
ASTROMETRY_OPT_USE_SEXTRACTOR = " --use-sextractor "

# Default number of objects to look at when doing astrometry.
ASTROMETRY_NUM_OBJS = 20
# Overwrite previous files and limit the number of objects to look at"
ASTROMETRY_PARAMS = "--overwrite -d "
# Radius of the field to solve.
SOLVE_FIELD_RADIUS = 0.1
# Identifier for object of interest in the coordinates list of a field.
OBJ_OF_INTEREST_ID = 0
# Error margin when assigning astrometry coordinates.
ASTROMETRY_COORD_RANGE = 0.005

# First index for a FIT table.
FIT_FIRST_TABLE_INDEX = 1

# sextractor parameters.
SEXTACTOR_COMMENT = "#"
SEXTACTOR_FWHM_COL = 2
SEXTACTOR_FWHM_MIN_VALUE = 1.2
SEXTRACTOR_CFG_DEFAULT_PATH = os.getcwd()
SEXTRACTOR_CFG_FILENAME = "sextractor.sex"

# Photometry parameters

# Multipliers to calculate some photometry parameters as multipliers 
# of the seeing value.
APERTURE_MULT = 3
ANNULUS_MULT = 4

DANNULUS_VALUE = 8
DATAMIN_MULT = 8
DATAMIN_VALUE = -0.001
DATAMAX_VALUE = 65536
CBOX_VALUE = 5

SKY_VALUE = 0

TXDUMP_FIELDS = "id,xc,yc,otime,mag,xairmass,merr"

# Columns from txdump that are used to calculate magnitudes.
COLS_MAG = [0,3,4,6]

# Columns of the data that contains the instrumental measures.
JD_TIME_COL = 0
INST_MAG_COL = 1
AIRMASS_COL = 2
FILTER_COL = 3

# Parameters for the T150 CCD of the OSN.
# http://www.osn.iaa.es/content/CCDT150-Camera
OSN_CCD_T150_READNOISE = 8.23
OSN_CCD_T150_GAIN = 1.5
OSN_CCD_T150_DATAMAX = 65536

# Columns in catalog file.
CAT_X_COL = 0
CAT_Y_COL = 1
CAT_ID_COL = 2

# Coordinates file
COO_RA_COL = 0
COO_DEC_COL = 1
COO_ID_COL = 2

# Number of the column that contains the magnitude value.
CSV_ID_COOR_COL = 0
CSV_X_COOR_COL = 1
CSV_Y_COOR_COL = 2
CSV_TIME_COL = 3 
CSV_MAG_COL = 4
CSV_AIRMASS_COL = 5
CSV_ERROR_COL = 6

# Number of the columns that contains AR and DEC values in each type of file.
OBJECTS_RA_COL_NUMBER = 1
OBJECTS_DEC_COL_NUMBER = 2

MEASURES_RA_COL_NUMBER = 1
MEASURES_DEC_COL_NUMBER = 2
MEASURE_FIRST_COL_NUMBER = 3

RDLS_RA_IDX_NUMBER = 0
RDLS_RA_COL_NUMBER = 1
RDLS_DEC_COL_NUMBER = 2

# Columns in celestial coordinates table.
RD_DATA_RA_COL = 0
RD_DATA_DEC_COL = 1

# Columns in XY coordinates table.
XY_DATA_X_COL = 0
XY_DATA_Y_COL = 1

# Name of the file that contains information about the objects of interest.
INT_OBJECTS_FILE_NAME = "objects.tsv"

# Columns of the file that contains the objects of interest.
OBJ_NAME_COL = 0
OBJ_RA_COL = 1
OBJ_DEC_COL = 2
OBJ_STANDARD_COL = 3
OBJ_B_MAG_COL = 4
OBJ_V_MAG_COL = 5
OBJ_R_MAG_COL = 6
OBJ_FINAL_NAME_COL = 7

STANDARD_VALUE = "YES"
NO_STANDARD_VALUE = "NO"

B_FILTER_NAME = "B"
V_FILTER_NAME = "V"
R_FILTER_NAME = "R"

# Columns for the data used to calculate extinction coefficients.
DAY_CE_CALC_DATA = 0
JD_TIME_CE_CALC_DATA = 1
INST_MAG_CE_CALC_DATA = 2
STD_MAG_CE_CALC_DATA = 3
AIRMASS_CE_CALC_DATA = 4
FILTER_CE_CALC_DATA = 5
OBJ_NAME_CALC_DATA = 6

# Columns for extinction coefficient data.
DAY_CE_DATA = 0
FILTER_CE_DATA = 1
SLOPE_CE_DATA = 2
INTERCEPT_CE_DATA = 3

INDEF_VALUE = "INDEF"

# Columns for extinction coefficients magnitudes.
JD_TIME_CEM_COL = 0
DAY_CEM_COL = 1
CE_MAG_CEM_COL = 2
INST_MAG_CEM_COL = 3
FILTER_CEM_COL = 4

# Columns of the transforming coefficients.
DAY_TRANS_COEF_COL = 0
C1_TRANS_COEF_COL = 1
C2_TRANS_COEF_COL = 2
C3_TRANS_COEF_COL = 3
C4_TRANS_COEF_COL = 4

# Columns of data in differential magnitude.
OBJ_NAME_COL_DF = 0
FILTER_COL_DF = 1
INDEX_COL_DF = 2
JD_COL_DF = 3
MAG_COL_DF = 4
ERR_COL_DF = 5
INDEF_COL_DF = 6

# File name parts delimited.
FILE_NAME_PARTS_DELIM = "_"