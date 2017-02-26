# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_rasparenza.ui'
#
# Created: Wed Nov 06 15:48:34 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_rasparenza(object):
    def setupUi(self, rasparenza):
        rasparenza.setObjectName(_fromUtf8("rasparenza"))
        rasparenza.resize(400, 87)
        self.buttonBox = QtGui.QDialogButtonBox(rasparenza)
        self.buttonBox.setGeometry(QtCore.QRect(30, 50, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalSlider = QtGui.QSlider(rasparenza)
        self.horizontalSlider.setGeometry(QtCore.QRect(50,10,280,19))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName(_fromUtf8("horizontalSlider"))

        self.retranslateUi(rasparenza)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), rasparenza.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), rasparenza.reject)
        QtCore.QMetaObject.connectSlotsByName(rasparenza)

    def retranslateUi(self, rasparenza):
        rasparenza.setWindowTitle(_translate("Transparency", "Transparency", None))
