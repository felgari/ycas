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
INDEX_FILE_PATTERN = '-indx.xyls'
DATA_FINAL_PATTERN = "_final.fit"
DATA_ALIGN_PATTERN = "_align.fit"
MAG_CSV_PATTERN = "_mag.csv"

# Special characters in file names.
BIAS_STRING = 'bias'
FLAT_STRING = 'flat'
DATANAME_CHAR_SEP = "-"
FIRST_DATA_IMG = "001"
FILTERS = [ 'V', 'B', 'R', 'CN', 'Cont4430', 'Cont6840' ]

MASTERBIAS_FILENAME = "bias_avg.fit"
MASTERFLAT_FILENAME = "flat_avg.fit"
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
ASTROMETRY_OPT_SEXTRACTOR_CONFIG = "--sextractor-config "

# Default number of objects to look at when doing astrometry.
ASTROMETRY_NUM_OBJS = 20
# Overwrite previous files and limit the number of objects to look at"
ASTROMETRY_PARAMS = "--overwrite -d "
# Radius of the field to solve.
SOLVE_FIELD_RADIUS = 1.0
# Identifier for object of interest in the coordinates list of a field.
OBJ_OF_INTEREST_ID = 0

# sextractor parameters.
SEXTACTOR_COMMENT = "#"
SEXTACTOR_FWHM_COL = 2
SEXTACTOR_FWHM_MIN_VALUE = 1.2
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
ERR_COL = 3
FILTER_COL = 4

# Parameters for the T150 CCD of the OSN.
# http://www.osn.iaa.es/content/CCDT150-Camera
OSN_CCD_T150_READNOISE = 8.23
OSN_CCD_T150_GAIN = 1.5
OSN_CCD_T150_DATAMAX = 60000

# Columns in catalog file.
CAT_X_COL = 0
CAT_Y_COL = 1
CAT_ID_COL = 2

# Coordinates file
COO_RA_COL = 0
COO_DEC_COL = 1
COO_ID_COL = 2

# Number of the columns that contains AR and DEC values in each type of file.
OBJECTS_RA_COL_NUMBER = 1
OBJECTS_DEC_COL_NUMBER = 2

MEASURES_RA_COL_NUMBER = 1
MEASURES_DEC_COL_NUMBER = 2
MEASURE_FIRST_COL_NUMBER = 3

RDLS_RA_IDX_NUMBER = 0
RDLS_RA_COL_NUMBER = 1
RDLS_DEC_COL_NUMBER = 2

# Columns in XY coordinates table.
XY_DATA_X_COL = 0
XY_DATA_Y_COL = 1

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

# Columns for magnitude tuples.
MAG_COL = 0
MAG_ERR_COL = 1
MAG_ID_COL = 2 

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
ERR_CEM_COL = 4
FILTER_CEM_COL = 5

# Minimum number of measures of standard objects to calculate extinction 
# coefficients.
MIN_NUM_STD_MEASURES = 4

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