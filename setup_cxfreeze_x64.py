"""
setup_cxfreeze_x64.py -

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


import sys
import os
from cx_Freeze import setup, Executable

# modify sys.path
#sys.path.append(os.path.abspath('pflanzenschutzkalkulationshilfe'))

# delete old build folder
os.system("rd /s /q build")


base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

# setup project dependencies
#build_exe_options = {"packages": ["os", "sys", "PyQt5.QtWidgets"],
#                     "excludes": ["tkinter", "tests"],
#                     "includes": ["subprocess"]}


options = {
    'build_exe': {
        "excludes": ["PyQt5.QtSensors", "PyQt5.QtWebChannel", "PyQt5.QtMultimedia"],
        "packages": ["os", "sys"],
        "includes": ["atexit"],
        "include_files" : ["language",
                ("C://Program Files//Python//Python34//Lib//site-packages//PyQt5//translations//qtbase_de.qm", "language//qtbase_de.qm"),
                "articles",
                "doc",
                "examples",
                "resources"],
        "include_msvcr": True
    }
}

executables = [
    Executable('main.py',
               base=base,
               targetName = 'wuchshuellenrechner.exe')
]

setup(name='Wuchshüllenrechner',
      version = '1.0.0-rc.1',
      description = 'Wuchshüllenrechner der Hochschule für Forstwirtschaft Rottenburg',
      options = options,
      executables = executables)
