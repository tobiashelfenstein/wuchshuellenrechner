"""
dialog_about.py - simple about dialog

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


from PyQt5.QtCore import QMargins
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QListWidget
from PyQt5.QtWidgets import QListWidgetItem
from lib import articles as library
import os.path
import sys
import subprocess

__version__ = "1.0.0-rc.2"


class AboutDialog(QDialog):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self):
        """The constructor initializes the class AboutDialog."""
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        # initialize class constants
        self._BUTTON_MIN_WIDTH = 110
        self._OXYGEN_PATH_48 = os.path.join("resources", "icons", "oxygen", "48")
        self._LOGOS_PATH = os.path.join("resources", "logos")

        # create basic elements
        self.setupUi()

    def setupUi(self):
        """Creates all basic elements of the about dialog."""
        self.setWindowTitle(QApplication.translate("AboutDialog", "About Wuchshüllenrechner"))  # Über Wuchshüllenrechner
        mainLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()

        # fonts and margins settings
        hlFont = QFont()
        hlFont.setBold(True)
        hlFont.setPointSize(14)

        shFont = QFont()
        shFont.setBold(True)

        maBottom = QMargins(0, 0, 0, 10)

        # create only the logo label on the left side of the dialog
        appLogo = QLabel(pixmap=QPixmap(os.path.join(self._OXYGEN_PATH_48, "dialog-information.png")))
        leftLayout.addWidget(appLogo)
        leftLayout.addStretch()

        # create all other text labels on the right side of the dialog
        # application specific labels
        appName = QLabel(QApplication.translate("AboutDialog", "Wuchshüllenrechner"))   # Wuchshüllenrechner
        appName.setFont(hlFont)
        rightLayout.addWidget(appName)

        appVersion = QLabel(QApplication.translate("AboutDialog", "Version " + __version__))    # Version
        appVersion.setContentsMargins(maBottom)
        rightLayout.addWidget(appVersion)

        # authors specific labels
        shAuthors = QLabel(QApplication.translate("AboutDialog", "Authors"))    # Autoren
        shAuthors.setFont(shFont)
        rightLayout.addWidget(shAuthors)

        appAuthors = QLabel("Tobias Helfenstein | <a href='mailto:tobias.helfenstein@mailbox.org'>tobias.helfenstein@mailbox.org</a><br />"
                "Anton Hammer | <a href='mailto:hammer.anton@gmail.com'>hammer.anton@gmail.com</a><br />"
                "Sebastian Hein | <a href='mailto:hein@hs-rottenburg.de'>hein@hs-rottenburg.de</a>")
        appAuthors.setOpenExternalLinks(True)
        appAuthors.setContentsMargins(maBottom)
        rightLayout.addWidget(appAuthors)

        # copyright specific labels
        shCopyright = QLabel(QApplication.translate("AboutDialog", "Copyright notice"))    # Urheberrechtshinweis
        shCopyright.setFont(shFont)
        rightLayout.addWidget(shCopyright)

        universityLogo = QLabel(pixmap=QPixmap(os.path.join(self._LOGOS_PATH, "university_rottenburg.png")))
        rightLayout.addWidget(universityLogo)

        appCopyright = QLabel("Copyright \N{COPYRIGHT SIGN} 2015-2016 " +
                QApplication.translate("AboutDialog",
                "University of Applied Forest Sciences Rottenburg"))     # Hochschule für Forstwirtschaft Rottenburg (HFR)
        appCopyright.setContentsMargins(maBottom)
        rightLayout.addWidget(appCopyright)

        # citatation specific labels
        shCitation = QLabel(QApplication.translate("AboutDialog", "Recommended citation"))    # Zitierempfehlung
        shCitation.setFont(shFont)
        rightLayout.addWidget(shCitation)

        appCitation = QLabel("HELFENSTEIN, T.; HAMMER, A.; HEIN, S. (2016): Wuchshüllenrechner<br />"
                "Version " + __version__ + ". Hochschule für Forstwirtschaft, Fachbereich Waldbau")
        rightLayout.addWidget(appCitation)

        # vertical spacer between copyright and supporters
        spacerCopyright = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        rightLayout.addItem(spacerCopyright)

        # supporters
        supportersLayout = QGridLayout(spacing=20)
        shSupporters = QLabel(QApplication.translate("AboutDialog", "Supporters"))    # Unterstützer
        shSupporters.setFont(shFont)
        supportersLayout.addWidget(shSupporters, 0, 0, 1, 2)

        # TUBEX
        tubexLogo = QLabel(pixmap=QPixmap(os.path.join(self._LOGOS_PATH, "tubex.png")))
        supportersLayout.addWidget(tubexLogo, 1, 0)

        # JOHANNES SCHMIDT FORSTSCHUTZ
        jsfLogo = QLabel(pixmap=QPixmap(os.path.join(self._LOGOS_PATH, "johannes_schmidt.png")))
        supportersLayout.addWidget(jsfLogo, 1, 1)

        rightLayout.addLayout(supportersLayout)

        # vertical spacer between the labels and the close button
        spacerSupporters = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        rightLayout.addItem(spacerSupporters)

        # close button at the bottom
        closeButton = QPushButton(QApplication.translate("AboutDialog", "Close"))   # Schließen
        closeButton.setFixedWidth(self._BUTTON_MIN_WIDTH)
        closeButton.clicked.connect(self.close)
        rightLayout.addWidget(closeButton, 0, Qt.AlignRight)

        # add the layouts to the dialog
        spacerHorizontal = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)
        mainLayout.addLayout(leftLayout)
        mainLayout.addItem(spacerHorizontal)
        mainLayout.addLayout(rightLayout)
        self.setLayout(mainLayout)


class ScientificBasisDialog(QDialog):
    """Creates a simple about dialog.

    The about dialog contains general information about the application and
    shows the copyright notice.
    That's why the class has no attributes or return values.

    """

    def __init__(self):
        """The constructor initializes the class AboutDialog."""
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        # initialize class constants
        self._BUTTON_MIN_WIDTH = 110

        # fonts and margins settings
        hlFont = QFont()
        hlFont.setBold(True)
        hlFont.setPointSize(14)

        # scientific logo
        logo = QLabel(pixmap=QPixmap(os.path.join(self._OXYGEN_PATH_48, "applications-science.png")))

        logoLayout = QVBoxLayout()
        logoLayout.addWidget(logo)
        logoLayout.addStretch()

        # begin the content
        # headline and description text
        self.headline = QLabel()
        self.headline.setFont(hlFont)
        self.description = QLabel(wordWrap=True)

        # the list with the open button
        self.listWidget = QListWidget()
        self.listWidget.setMinimumWidth(420)
        self.createArticles()

        self.openButton = QPushButton()
        self.openButton.clicked.connect(self.openAction)

        listLayout = QHBoxLayout()
        listLayout.addWidget(self.listWidget)
        listLayout.addWidget(self.openButton, alignment=Qt.AlignTop)

        # create a close button
        line = QFrame(frameShadow=QFrame.Sunken, frameShape=QFrame.HLine)
        self.closeButton = QPushButton()
        self.closeButton.setFixedWidth(self._BUTTON_MIN_WIDTH)
        self.closeButton.clicked.connect(self.close)

        # content layout
        contentLayout = QVBoxLayout()
        contentLayout.addWidget(self.headline)
        contentLayout.addWidget(self.description)
        contentLayout.addLayout(listLayout)
        contentLayout.addWidget(line)
        contentLayout.addWidget(self.closeButton, alignment=Qt.AlignRight)

        # main layout
        layout = QHBoxLayout(self)
        layout.addLayout(logoLayout)
        layout.addLayout(contentLayout)

        # translate the graphical user interface
        self.retranslateUi()

    def createArticles(self):
        # load articles from library
        # and add them to the list
        for article in library.SCIENTIFIC_ARTICLES:
            # list widget item with it's data
            item = QListWidgetItem()
            item.setText(article[0].strip())
            item.setData(Qt.UserRole, article[1].strip())

            # add the item to the list widget
            self.listWidget.addItem(item)

    def openAction(self):
        # get the current item from list
        item = self.listWidget.currentItem()

        # create the documentation path with
        # the current locale settings
        articleFile = os.path.join("articles", item.data(Qt.UserRole))

        # on every platfrom a different
        # start operation is needed
        if sys.platform == "win32":
            os.startfile(articleFile)
        elif sys.platform == "darwin":
            subprocess.call(("open", articleFile))
        elif sys.platform.startswith("linux"):
            subprocess.call(("xdg-open", articleFile))

    def retranslateUi(self):
        # dialog titel
        self.setWindowTitle(QApplication.translate("ScientificBasisDialog", "Specialist articles"))        # Wissenschaftliche Grundlage

        # headline and description
        self.headline.setText(QApplication.translate("ScientificBasisDialog", "Specialist articles"))   # Wissenschaftliche Beiträge
        self.description.setText(QApplication.translate("ScientificBasisDialog",
                "Hier finden Sie grundlegende Fachbeiträge zur Thematik") + ":")

        # buttons
        self.openButton.setText(QApplication.translate("ScientificBasisDialog", "Open article"))        # Beitrag öffnen
        self.closeButton.setText(QApplication.translate("ScientificBasisDialog", "Close"))              # Schließen
