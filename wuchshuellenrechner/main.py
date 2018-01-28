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


import os.path
import sys
from argparse import ArgumentParser
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QSplashScreen
from gui.window_main import MainWindow

__version__ = "1.0.0"


def main():
    # define command line parameters
    parser = ArgumentParser()
    parser.add_argument("-s", "--splash", dest="splash", action="store_false")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    # create splash screen with sponsors
    # default splash=True, use "-s" or "--splash" to set splash=False
    window = MainWindow()
    if args.splash:
        pixmap = QPixmap(os.path.join("resources","splash", "splash.jpg"))
        splash = QSplashScreen(pixmap)
        splash.showMessage("  Version: " + __version__, Qt.AlignBottom)

        # show the splash screen for 3 seconds
        splash.show()
        app.processEvents()
        QThread.sleep(3)
        window.show()
        splash.finish(window)
    else:
        window.show()

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
