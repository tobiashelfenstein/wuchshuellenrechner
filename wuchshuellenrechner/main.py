"""
main.py - 

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
from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from gui.window_main import MainWindow


def main():
    app = QApplication(sys.argv)
    
    # load Qt translation for default dialogs
    #qtTl = QTranslator()
    #if qtTl.load(QLocale(), "qtbase", "_", QLibraryInfo.location(QLibraryInfo.TranslationsPath)):
    #if qtTl.load(QLocale(), "qtbase", "_", "language"):
    #    app.installTranslator(qtTl)

    # load own application translation
    #appTl = QTranslator()
    #if appTl.load(QLocale(), "wuchshuellenrechner", "_", "language"):
    #    app.installTranslator(appTl)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
