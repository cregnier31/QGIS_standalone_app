# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cmems_diaologbox.ui'
#
# Created: Wed Jun  1 18:48:04 2016
#      by: PyQt4 UI code generator 4.10.1
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(579, 716)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(230, 660, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(60, 20, 491, 71))
        self.groupBox.setTitle(_fromUtf8(""))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(220, 20, 241, 31))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(0, 20, 101, 31))
        self.label.setObjectName(_fromUtf8("label"))
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(50, 90, 491, 71))
        self.groupBox_2.setTitle(_fromUtf8(""))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.comboBox_2 = QtGui.QComboBox(self.groupBox_2)
        self.comboBox_2.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(0, 20, 111, 31))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.groupBox_3 = QtGui.QGroupBox(Dialog)
        self.groupBox_3.setGeometry(QtCore.QRect(50, 160, 491, 71))
        self.groupBox_3.setTitle(_fromUtf8(""))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.comboBox_4 = QtGui.QComboBox(self.groupBox_3)
        self.comboBox_4.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_4.setObjectName(_fromUtf8("comboBox_4"))
        self.label_4 = QtGui.QLabel(self.groupBox_3)
        self.label_4.setGeometry(QtCore.QRect(0, 20, 111, 31))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.groupBox_4 = QtGui.QGroupBox(Dialog)
        self.groupBox_4.setGeometry(QtCore.QRect(50, 230, 491, 71))
        self.groupBox_4.setTitle(_fromUtf8(""))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.comboBox_5 = QtGui.QComboBox(self.groupBox_4)
        self.comboBox_5.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_5.setObjectName(_fromUtf8("comboBox_5"))
        self.label_5 = QtGui.QLabel(self.groupBox_4)
        self.label_5.setGeometry(QtCore.QRect(0, 20, 121, 31))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.groupBox_5 = QtGui.QGroupBox(Dialog)
        self.groupBox_5.setGeometry(QtCore.QRect(40, 300, 521, 161))
        self.groupBox_5.setTitle(_fromUtf8(""))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.label_3 = QtGui.QLabel(self.groupBox_5)
        self.label_3.setGeometry(QtCore.QRect(0, 60, 101, 31))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lineEdit = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit.setGeometry(QtCore.QRect(135, 59, 111, 41))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_2.setGeometry(QtCore.QRect(365, 55, 111, 41))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.lineEdit_3 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_3.setGeometry(QtCore.QRect(247, 19, 113, 41))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.lineEdit_4 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_4.setGeometry(QtCore.QRect(250, 100, 113, 41))
        self.lineEdit_4.setObjectName(_fromUtf8("lineEdit_4"))
        self.label_6 = QtGui.QLabel(self.groupBox_5)
        self.label_6.setGeometry(QtCore.QRect(165, 38, 71, 21))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_7 = QtGui.QLabel(self.groupBox_5)
        self.label_7.setGeometry(QtCore.QRect(395, 28, 66, 21))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.groupBox_5)
        self.label_8.setGeometry(QtCore.QRect(275, 78, 66, 21))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_9 = QtGui.QLabel(self.groupBox_5)
        self.label_9.setGeometry(QtCore.QRect(270, -1, 66, 21))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.groupBox_6 = QtGui.QGroupBox(Dialog)
        self.groupBox_6.setGeometry(QtCore.QRect(50, 450, 491, 71))
        self.groupBox_6.setTitle(_fromUtf8(""))
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.comboBox_6 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_6.setGeometry(QtCore.QRect(140, 20, 141, 31))
        self.comboBox_6.setObjectName(_fromUtf8("comboBox_6"))
        self.label_10 = QtGui.QLabel(self.groupBox_6)
        self.label_10.setGeometry(QtCore.QRect(-20, 20, 121, 31))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.comboBox_3 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_3.setGeometry(QtCore.QRect(320, 20, 151, 29))
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.groupBox_7 = QtGui.QGroupBox(Dialog)
        self.groupBox_7.setGeometry(QtCore.QRect(30, 580, 541, 71))
        self.groupBox_7.setTitle(_fromUtf8(""))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.comboBox_7 = QtGui.QComboBox(self.groupBox_7)
        self.comboBox_7.setGeometry(QtCore.QRect(110, 20, 151, 31))
        self.comboBox_7.setObjectName(_fromUtf8("comboBox_7"))
        self.label_11 = QtGui.QLabel(self.groupBox_7)
        self.label_11.setGeometry(QtCore.QRect(0, 20, 121, 31))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_13 = QtGui.QLabel(self.groupBox_7)
        self.label_13.setGeometry(QtCore.QRect(290, 20, 81, 31))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.comboBox_10 = QtGui.QComboBox(self.groupBox_7)
        self.comboBox_10.setGeometry(QtCore.QRect(380, 20, 151, 29))
        self.comboBox_10.setObjectName(_fromUtf8("comboBox_10"))
        self.groupBox_8 = QtGui.QGroupBox(Dialog)
        self.groupBox_8.setGeometry(QtCore.QRect(50, 510, 491, 71))
        self.groupBox_8.setTitle(_fromUtf8(""))
        self.groupBox_8.setObjectName(_fromUtf8("groupBox_8"))
        self.comboBox_8 = QtGui.QComboBox(self.groupBox_8)
        self.comboBox_8.setGeometry(QtCore.QRect(140, 20, 141, 31))
        self.comboBox_8.setObjectName(_fromUtf8("comboBox_8"))
        self.label_12 = QtGui.QLabel(self.groupBox_8)
        self.label_12.setGeometry(QtCore.QRect(-30, 20, 141, 31))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.comboBox_9 = QtGui.QComboBox(self.groupBox_8)
        self.comboBox_9.setGeometry(QtCore.QRect(320, 20, 151, 29))
        self.comboBox_9.setObjectName(_fromUtf8("comboBox_9"))

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Choose Area </span></p></body></html>", None))
        self.label_2.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Choose Product</span></p></body></html>", None))
        self.label_4.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Choose Dataset</span></p></body></html>", None))
        self.label_5.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Choose Variable</span></p></body></html>", None))
        self.label_3.setText(_translate("Dialog", "<html><head/><body><p><span style=\" font-weight:600;\">Defined Area</span></p></body></html>", None))
        self.label_6.setText(_translate("Dialog", "Lon min", None))
        self.label_7.setText(_translate("Dialog", "Lon max", None))
        self.label_8.setText(_translate("Dialog", "Lat min", None))
        self.label_9.setText(_translate("Dialog", "Lat max", None))
        self.label_10.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Time min</span></p></body></html>", None))
        self.label_11.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Depth min</span></p></body></html>", None))
        self.label_13.setText(_translate("Dialog", "Depth max", None))
        self.label_12.setText(_translate("Dialog", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Time max</span></p></body></html>", None))

