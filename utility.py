# -*- coding: utf-8 -*-

# Copyright (c) 2015 Felipe Gallego. All rights reserved.
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

""" This module performs some utility functions. """

def get_day_from_mjd(mjd_time):
    """Returns the julian day related to the Julian time received.
    
    The day is assigned to that which the night begins.
    So a JD between .0 (0:00:00) and .4 (+8:00:00) belongs to the day before.
    
    Args:
        mjd_time: A Julian time value.
    
    Returns:        
        The Julian day related to the Julian day, without decimals. 
    
    """
    
    day = None
    
    dot_pos = mjd_time.find('.')
    
    first_decimal = mjd_time[dot_pos + 1]
    
    int_first_decimal = int(first_decimal) 
    
    if int_first_decimal >= 0 and int_first_decimal <= 4:
        day = str(int(mjd_time[:dot_pos]) - 1)
    else:
        day = mjd_time[:dot_pos]
    
    return day