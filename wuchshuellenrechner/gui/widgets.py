"""
widgets.py -

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


from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QPixmap
import os.path

__version__ = "0.0.1"


class ToolTipLabel(QLabel):
    def __init__(self, toolTip=""):
        super().__init__()
        self.toolTip = toolTip.strip()

        self._OXYGEN_PATH_22 = os.path.join("resources", "icons", "oxygen", "22")
        self.setPixmap(QPixmap(os.path.join(self._OXYGEN_PATH_22, "system-help.png")))
        self.setMouseTracking(True)

    def setToolTip(self, toolTip):
        self.toolTip = toolTip.strip()

    def mouseMoveEvent(self, event):
        QToolTip.showText(event.globalPos(), self.toolTip, self)

        return super().mouseMoveEvent(event)
