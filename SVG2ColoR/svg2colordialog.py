# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SVG2ColoR
                                 A QGIS plugin
 Generates color-ramp styles from SVG files.  It also compatible with CPT-CITY styles.
 SVG2ColoR improves your color-ramp library, by the way your maps look better.
                              -------------------
        begin                : 2014-10-17
		version				 : 0.9
        copyright            : (C) 2014 by Mehmet Selim BILGIN
        email                : mselimbilgin@yahoo.com
		web					 : http://cbsuygulama.wordpress.com/svg2color
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

from PyQt4 import QtCore, QtGui, uic
import os

MainFormClass, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui_svg2color.ui'))


class SVG2ColoRDialog(QtGui.QDialog, MainFormClass):
    def __init__(self):
        print "inside init"
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
