# -*- coding: utf-8 -*-
"""
/***************************************************************************
 rasparenzaDialog
                                 A QGIS plugin
 rasparenza
                             -------------------
        begin                : 2013-11-06
        copyright            : (C) 2013 by geodrinx
        email                : geodrinx@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from ui_rasparenza import Ui_rasparenza
# create the dialog for zoom to point


class rasparenzaDialog(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_rasparenza()
        self.ui.setupUi(self)
