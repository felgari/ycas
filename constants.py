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

# File name parts delimited.
FILE_NAME_PARTS_DELIM = "_"

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

# Columns in catalog file.
CAT_X_COL = 0
CAT_Y_COL = 1
CAT_ID_COL = 2

# Columns in XY coordinates table.
XY_DATA_X_COL = 0
XY_DATA_Y_COL = 1

# Columns of the file that contains the objects of interest.
OBJ_NAME_COL = 0
OBJ_RA_COL = 1
OBJ_DEC_COL = 2
OBJ_STANDARD_COL = 3

B_FILTER_NAME = "B"
V_FILTER_NAME = "V"
R_FILTER_NAME = "R"

# Columns for magnitude tuples.
MAG_COL = 0
MAG_ERR_COL = 1
MAG_ID_COL = 2 

INDEF_VALUE = "INDEF"