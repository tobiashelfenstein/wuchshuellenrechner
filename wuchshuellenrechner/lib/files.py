"""
files.py - 

Copyright (C) 2016 Tobias Helfenstein <tobias.helfenstein@mailbox.org>
Copyright (C) 2016 Anton Hammer <hammer.anton@gmail.com>
Copyright (C) 2016 Sebastian Hein <hein@hs-rottenburg.de>
Copyright (C) 2016 Hochschule für Forstwirtschaft Rottenburg <hfr@hs-rottenburg.de>

This file is part of Wuchshüllenrechner.

Wuchshüllenrechner is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Wuchshüllenrechner is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""


import xml.etree.ElementTree as ElementTree
import logging
import os


def filename_is_valid(filename, filetype=""):
    """The constructor initializes the class XMLFileWriter."""
    status = True
    if not isinstance(filename, str):
        status = False
        # raise TypeError("file path not from type string")
    filename = filename.strip()
    if len(filename) < 5:
        status = False
        # raise ValueError("file name to short or empty")
    
    filetype = filetype.strip()
    if filetype:
        f_list = filename.rsplit(".", 1)
        if f_list.pop() != filetype:
            status = False
            # raise ValueError("file not from type " + filetype)
    
    return status