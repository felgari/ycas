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

"""This module performs some utility functions. """

def get_day_from_mjd(mjd_time):
    """Returns the Modified Julian day related to the Modified Julian time
    received without decimals.
    
    The day is assigned to that which the night begins.
    So a MJD between .0 (0:00:00) and .5 (+12:00:00) belongs to the day before,
    this is, when the night begins.
    
    Args:
        mjd_time: A Julian time value.
    
    Returns:        
        The Modified Julian day calculated. 
    
    """
    
    day = None
    
    dot_pos = mjd_time.find('.')
    
    first_decimal = mjd_time[dot_pos + 1]
    
    int_first_decimal = int(first_decimal) 
        
    if int_first_decimal >= 0 and int_first_decimal <= 5:
        # The day before, as the time corresponds to early morning.
        day = str(int(mjd_time[:dot_pos]) - 1)
    else:
        day = mjd_time[:dot_pos]
    
    return int(day)