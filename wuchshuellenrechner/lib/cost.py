"""
cost.py - 

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


# define tree species key
TREESPECIES_DESCRIPTION = (
    "unbekannt (unb.)",
    "Weiß-Tanne (Ta)",
    "Große Küsten-Tanne (KüTa)",
    "Europäische Lärche (ELä)",
    "Japanische Lärche (JLä)",
    "Gemeine Fichte (Fi)",
    "Omorika-Fichte (OFi)",
    "Sitka-Fichte (SFi)",
    "Schwarz-Kiefer (SKi)",
    "Weymouths-Kiefer (Wey)",
    "Wald-Kiefer (Kie)",
    "Küsten-Douglasie (Dgl)",
    "Gewöhnliche Eibe (Eib)",
    "sonstige Nadelbaum-Arten (sNb)",
    "Feld-Ahorn (FAh)",
    "Spitz-Ahorn (SAh)",
    "Berg-Ahorn (BAh)",
    "Gewöhnliche Rosskastanie (RKa)",
    "Rot-Erle (REr)",
    "Grau-Erle (WEr)",
    "Birken-Arten (Bi)",
    "Hainbuche (HBu)",
    "Edelkastanie (EKa)",
    "Rot-Buche (Bu)",
    "Gemeine Esche (Es)",
    "Schwarznuss (SNu)",
    "Echte Walnuss (WNu)",
    "Wild-Apfel (WAp)",
    "Balsam-Pappeln (BPa)",
    "Schwarz-Pappel (SPa)",
    "Zitter-Pappel (As)",
    "sonstige Pappel-Arten (sPa)",
    "Vogel-Kirsche (Kir)",
    "Traubenkirsche (TKir)",
    "Wild-Birne (WBi)",
    "Trauben-Eiche (TEi)",
    "Stiel-Eiche (SEi)",
    "Rot-Eiche (REi)",
    "Robinie (Rob)",
    "Weiden-Arten (Wei)",
    "Mehlbeere (Meb)",
    "Vogelbeere (Vb)",
    "Speierling (Spei)",
    "Elsbeere (Els)",
    "Winter-Linde (WLi)",
    "Sommer-Linde (SLi)",
    "Berg-Ulme (BUl)",
    "Flatter-Ulme (FlU)",
    "Feld-Ulme (FUl)",
    "sonstige Laubbaum-Arten (sLb)"
)

TREESPECIES_NAME = (
    "unbekannt",
    "Weiß-Tanne",
    "Große Küsten-Tanne",
    "Europäische Lärche",
    "Japanische Lärche",
    "Gemeine Fichte",
    "Omorika-Fichte",
    "Sitka-Fichte",
    "Schwarz-Kiefer",
    "Weymouths-Kiefer",
    "Wald-Kiefer",
    "Küsten-Douglasie",
    "Gewöhnliche Eibe",
    "sonstige Nadelbaum-Arten",
    "Feld-Ahorn",
    "Spitz-Ahorn",
    "Berg-Ahorn",
    "Gewöhnliche Rosskastanie",
    "Rot-Erle",
    "Grau-Erle",
    "Birken-Arten",
    "Hainbuche",
    "Edelkastanie",
    "Rot-Buche",
    "Gemeine Esche",
    "Schwarznuss",
    "Echte Walnuss",
    "Wild-Apfel",
    "Balsam-Pappeln",
    "Schwarz-Pappel",
    "Zitter-Pappel",
    "sonstige Pappel-Arten",
    "Vogel-Kirsche",
    "Traubenkirsche",
    "Wild-Birne",
    "Trauben-Eiche",
    "Stiel-Eiche",
    "Rot-Eiche",
    "Robinie",
    "Weiden-Arten",
    "Mehlbeere",
    "Vogelbeere",
    "Speierling",
    "Elsbeere",
    "Winter-Linde",
    "Sommer-Linde",
    "Berg-Ulme",
    "Flatter-Ulme",
    "Feld-Ulme",
    "sonstige Laubbaum-Arten"
)

TREESPECIES_ABBREVIATION = (
    "unb.",
    "Ta",
    "KüTa",
    "ELä",
    "JLä",
    "Fi",
    "OFi",
    "SFi",
    "SKi",
    "Wey",
    "Kie",
    "Dgl",
    "Eib",
    "sNb",
    "FAh",
    "SAh",
    "BAh",
    "RKa",
    "REr",
    "WEr",
    "Bi",
    "HBu",
    "EKa",
    "Bu",
    "Es",
    "SNu",
    "WNu",
    "WAp",
    "BPa",
    "SPa",
    "As",
    "sPa",
    "Kir",
    "TKir",
    "WBi",
    "TEi",
    "SEi",
    "REi",
    "Rob",
    "Wei",
    "Meb",
    "Vb",
    "Spei",
    "Els",
    "WLi",
    "SLi",
    "BUl",
    "FUl",
    "FlU",
    "sLb"
)

# define tree shelters
TREESHELTERS_DESCRIPTION = (
    "Anderer Wuchshüllentyp",
    "PlantaGard Gitterhülle (20|120 cm)",
    "PlantaGard Gitterhülle (30|120 cm)",
    "PlantaGard Microvent (90 cm)",
    "PlantaGard Microvent (120 cm)",
    "PlantaGard Microvent (150 cm)",
    "PlantaGard Microvent (180 cm)",
    "PlantaGard Netzhülle (120 cm)",
    "Tubex Layflat SG (20|120 cm)",
    "Tubex Shelterguard (120 cm)",
    "Tubex Shelterguard (150 cm)",
    "Tubex Shelterguard (180 cm)",
    "Tubex Ventex (90 cm)",
    "Tubex Ventex (120 cm)",
    "Tubex Ventex (150 cm)",
    "Tubex Ventex (180 cm)",
    "Tubex Ventex 12D (120 cm)",
    "Tubex Ventex 12D (150 cm)",
    "Tubex Ventex 12D (180 cm)"
)

TREESHELTERS_HEIGHT = (
    0,
    120,
    120,
    90,
    120,
    150,
    180,
    120,
    120,
    120,
    150,
    180,
    90,
    120,
    150,
    180,
    120,
    150,
    180
)

TREESHELTERS_COST = (
    0.00,
    1.76,
    2.56,
    0.97,
    1.22,
    1.89,
    1.93,
    1.22,
    2.44,
    2.31,
    2.77,
    3.32,
    2.02,
    2.18,
    2.82,
    3.45,
    2.82,
    3.57,
    4.45
)

# HAMMER: AFZ-DerWald 23/2012 bei 35€/Stunde und ca. 22 Wuchshüllen
# Alternativwert aus KOPP
TREESHELTERS_INSTALLATION = 1.36

# KOPP: AFZ-DerWald 16/2012 bei 35€/Stunde und ca. 28 Wuchshüllen
# inklusive Entsorgungskosten
TREESHELTERS_REMOVAL = 1.50

TREESHELTERS_NO_REMOVAL = (
    0,
    16,
    17,
    18)

STAKES_HEIGHT = (
    150,
    180,
    220
)

STAKES_COST = (
    0.59,
    1.01,
    1.22
)

FENCE_DESCRIPTION = (
    "Anderer Zauntyp",
    "Hordengatter (4,00 m x 2,50 m)",
    "Wanderzaun (1,50 m)",
    "Scherenzaun (1,60 m)",
    "Pfostenzaun (1,60 m)",
    "Modifizierter Stützenzaun (1,60 m)"
)

FENCE_COST = (
    0.00,
    15.25,
    9.45,
    11.22,
    10.03,
    12.32
)

# 19% sales tax
SALES_TAX = 0.19
