# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
from qgis.core import *
from qgis.gui import *
import cPickle
import os,urllib2
import netCDF4
import time
import numpy as np
import xml.etree.ElementTree as ET
from owslib.wms import WebMapService
from Reader import read_netcdf_variable,array_to_raster
#from motuclient import *

class VectorDialog(QDialog):

    """ Vector Dialog interface"""

    def __init__(self): 
        QDialog.__init__(self)
        self.setWindowTitle("Enter Vector parameters") 
        layout = QFormLayout(self)
        self.zonalspeed = QLabel("Eastward velocity", self)
        self.zonalspeed_field = QLineEdit(self)
        self.meridianspeed = QLabel("Northward velocity", self)
        self.meridianspeed_field = QLineEdit(self)
        self.resol_label = QLabel("Resolution", self)
        self.resol_field = QLineEdit(self)
        self.scale_label = QLabel("Scale", self)
        self.scale_field = QLineEdit(self)
        self.color_rlabel = QLabel("Red Color", self)
        self.color_rfield = QLineEdit(self)
        self.color_rfield.setText("0")
        self.color_glabel = QLabel("Green Color", self)
        self.color_gfield = QLineEdit(self)
        self.color_gfield.setText("0")
        self.color_blabel = QLabel("Blue Color", self)
        self.color_bfield = QLineEdit(self)
        self.color_bfield.setText("0")
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.zonalspeed, self.zonalspeed_field)
        layout.addRow(self.meridianspeed, self.meridianspeed_field)
        layout.addRow(self.resol_label, self.resol_field)
        layout.addRow(self.scale_label, self.scale_field)
        layout.addRow(self.color_rlabel, self.color_rfield)
        layout.addRow(self.color_glabel, self.color_gfield)
        layout.addRow(self.color_blabel, self.color_bfield)
        layout.addRow(btn_layout)
        self.setLayout(layout)

class ContourDialogParams(QDialog):

    """ Contour Dialog interface """

    def __init__(self): 
        QDialog.__init__(self)
        self.setWindowTitle("Enter Contours parameters") 
        layout = QFormLayout(self)
        self.resol_clabel = QLabel("Resolution", self)
        self.resol_cfield = QLineEdit(self)
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.resol_clabel, self.resol_cfield)
        layout.addRow(btn_layout)
        self.setLayout(layout)

class GridDialogParams(QDialog):

    """ Grid Dialog interface """

    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("Enter Grid parameters") 
        layout = QFormLayout(self)
        self.resol_clabelgrid = QLabel("Resolution", self)
        self.resol_cfieldgrid = QLineEdit(self)
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.resol_clabelgrid, self.resol_cfieldgrid)
        layout.addRow(btn_layout)
        self.setLayout(layout)

class ComputeDiffDialog(QDialog):

    """Interface dialog for computing differences between 2 files """
    def __init__(self,parent): 
        QDialog.__init__(self)
        self.mainobj=parent
        layout = QFormLayout(self)
        self.setWindowTitle("Select input files to compare")
        self.resize(546, 479)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(110, 430, 231, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(50, 30, 411, 80))
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("File 1")
        self.File1Edit = QLineEdit(self.groupBox)
        self.File1Edit.setGeometry(QtCore.QRect(0, 30, 371, 33))
        self.File1Edit.setObjectName("File1Edit")
        self.toolButton = QToolButton(self.groupBox)
        self.toolButton.setGeometry(QtCore.QRect(380, 30, 31, 31))
        self.toolButton.setObjectName("toolButton")
        self.toolButton.setText("...")
        self.groupBox_2 = QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(50, 110, 411, 80))
        self.groupBox_2.setObjectName("groupBox_2")
        self.groupBox_2.setTitle("File 2")
        self.File2Edit = QLineEdit(self.groupBox_2)
        self.File2Edit.setGeometry(QtCore.QRect(0, 30, 371, 33))
        self.File2Edit.setObjectName("File2Edit")
        self.toolButton_2 = QToolButton(self.groupBox_2)
        self.toolButton_2.setGeometry(QtCore.QRect(380, 30, 31, 31))
        self.toolButton_2.setObjectName("toolButton_2")
        self.toolButton_2.setText("...")
        self.groupBox_3 = QGroupBox(self)
        self.groupBox_3.setGeometry(QtCore.QRect(50, 190, 171,71))
        self.groupBox_3.setObjectName("groupBox_variable")
        self.groupBox_3.setTitle("Choose variable")
        self.comboBox_var = QComboBox(self.groupBox_3)
        self.comboBox_var.setGeometry(QtCore.QRect(2, 30, 161, 29))
        self.comboBox_var.setObjectName("comboBox_variable")
        self.groupBox_4 = QtGui.QGroupBox(self)
        self.groupBox_4.setGeometry(QtCore.QRect(50, 260, 171, 80))
        self.groupBox_4.setObjectName("groupBox_depth")
        self.groupBox_4.setTitle("Choose depth")
        self.comboBox_2 = QComboBox(self.groupBox_4)
        self.comboBox_2.setGeometry(QtCore.QRect(0, 30, 151, 29))
        self.comboBox_2.setObjectName("comboBox_2_depth")
        self.groupBox_5 = QGroupBox(self)
        self.groupBox_5.setGeometry(QtCore.QRect(50, 330, 171, 71))
        self.groupBox_5.setObjectName("groupBox_time")
        self.groupBox_5.setTitle("Choose Time")
        self.comboBox_3 = QComboBox(self.groupBox_5)
        self.comboBox_3.setGeometry(QtCore.QRect(0, 30, 151, 29))
        self.comboBox_3.setObjectName("comboBox_3_time")
        self.tmp_path=self.mainobj.tmp_path
        self.setLayout(layout)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.toolButton, QtCore.SIGNAL("clicked()"), self.openRaster)
        QtCore.QObject.connect(self.toolButton_2, QtCore.SIGNAL("clicked()"),self.openRaster2)
        QtCore.QObject.connect(self.comboBox_var, QtCore.SIGNAL("currentIndexChanged(int)"), self.updateDim2)
        QtCore.QMetaObject.connectSlotsByName(self)

    def openRaster(self):
        """ Open raster dialog for file1 """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                     self.tr("netCDF Files (*.nc *.cdf *.nc2 *.nc4)"));
        if fileName is not None:
            print type(fileName)
            print "file OK %s " %(str(fileName))
            self.filename1=str(fileName)
            print os.path.basename(str(fileName))
            self.File1Edit.setText(os.path.basename(str(fileName)))
            print "Set file 1 OK"

    def openRaster2(self):
        """ Open raster dialog for file1 """
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                     self.tr("netCDF Files (*.nc *.cdf *.nc2 *.nc4)"));
        if fileName is not None:
            #LineEdit.setText(filename)
            self.groupBox_3.setEnabled(True)
            self.groupBox_4.setEnabled(True)
            self.File2Edit.setText(os.path.basename(str(fileName)))
            self.filename2=str(fileName)
            self.updateVar2(str(fileName))

    def updateVar2(self,filename):
        """ Populate combobox with variables """
        nc=netCDF4.Dataset(str(filename),'r')
        dict_var=nc.variables
        print 
        for var in dict_var :
            if str(var) != "longitude" and str(var) != "latitude" \
               and str(var) != "nav_lon" and str(var) != "nav_lat" \
               and str(var) != "depth" and str(var) != "deptht"  \
               and str(var) != "time_counter" and str(var) != "time" :
                self.comboBox_var.addItem(str(var))

    def updateDim2(self):
        """ Populate combobox with Dimensions """
        self.comboBox_2.clear()
        self.comboBox_3.clear()
        variable=self.comboBox_var.currentText()
        print "variable :: " 
        print variable
        nc=netCDF4.Dataset(str(self.filename2),'r')
        dim_var=nc.variables[str(variable)].dimensions
        dim_len=nc.variables[str(variable)].shape
        print "Open Filename OK %s " %(self.filename2)
        i=0
        dim_values = dict()
        dim_names = []
        dim_def = dict()
        for dim in dim_var :
            dim_values[ dim ] = []
            dim_def[ dim ] = []
            dim_values[ dim ].append(i)
            dim_def[ dim ].append(dim_len[i])
            dim_names.append(dim)
            i=i+1
        dim_names2=[]
        ll_depth=False
        for dim in dim_names:
            if dim == 'depth'  or dim == 'deptht': 
                dim_names2.append(dim)
                ll_depth=True
                def_var=dim_def[dim]
                for value in range(0,int(def_var[0])): 
                    self.comboBox_2.addItem(str(value+1))
            elif dim == 'time_counter' and dim_def[dim][0] >= 1 : 
                dim_names2.append(dim)
                def_var_time=dim_def[dim]
                for value in range(0,int(def_var_time[0])): 
                    self.comboBox_3.addItem(str(value+1))
            else:
                del dim_values[dim]
                del dim_def[dim]

        if not ll_depth:
            self.comboBox_2.addItem(str(1))

    def accept(self):
        if self.filename1 and self.filename2 :
            ## Read dataset and compute the diff 
            nc_file1=netCDF4.Dataset(self.filename1,'r')
            nc_file2=netCDF4.Dataset(self.filename2,'r')
            variable=str(self.comboBox_var.currentText())
            temps=int(self.comboBox_3.currentText())-1
            depth=int(self.comboBox_2.currentText())-1
            var_1=nc_file1.variables[variable][temps,depth,:,:]
            var_2=nc_file2.variables[variable][temps,depth,:,:]
            x,y=var_1.shape
            x2,y2=var_2.shape
            if  x == x2 and y == y2 : 
                lon = nc_file1.variables['longitude'][:]
                lat = nc_file1.variables['latitude'][:]
                var_1=np.ma.filled(var_1,np.nan)
                var_2=np.ma.filled(var_2,np.nan)
                var_diff=var_1-var_2
                x_min,y_min,x_max,y_max = [lon.min(),lat.min(),lon.max(),lat.max()]
                u_y_pixels, u_x_pixels = x,y
                dx = x_max - x_min
                dy = y_max - y_min
                cellsize_long = dx / u_x_pixels
                cellsize_lat = dy / u_y_pixels
                cell_sizes = (cellsize_long, cellsize_lat)
                print cell_sizes
                topleft_corner = (x_min, y_max)
                print topleft_corner
                ## Create outputfile 
                filepath=self.tmp_path
                print filepath
                new_filename='Diff_'+str(variable)+'_prof'+str(depth)+'.tif'
                print new_filename
                noDataValue=np.nan
                array_to_raster(np.flipud(var_diff), cell_sizes, topleft_corner,noDataValue,filepath+new_filename)      
                print 'array to raster ok'
                raster_lyr_diff=QgsRasterLayer(filepath+new_filename,'Diff_'+str(variable)+'_prof_'+str(depth)) 
                raster_lyr_diff.setCrs( QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
                print "Add to registry"
                QgsMapLayerRegistry.instance().addMapLayer(raster_lyr_diff)
                self.mainobj.addLayer(raster_lyr_diff,1)
                ## Enable some functionalities
                self.mainobj.actionGetValue.setEnabled(True)
                self.mainobj.actionTransparency.setEnabled(True)
                self.mainobj.actionContouring.setEnabled(True)
                self.mainobj.getvalue=PointTool(self.canvas,self.rlayer) # false = in
                self.mainobj.getvalue.setAction(self.actionGetValue)
                self.mainobj.compose=1
            else : 
                "No corresponding dimensions"

class OlaParams(QDialog):
    """ Dialog for min max depth profiles selection """
    def __init__(self,min_prof=None,max_prof=None): 
        QDialog.__init__(self)
        self.setWindowTitle("Select min and max depth") 
        layout = QFormLayout(self)
        self.minprof_clabelgrid = QLabel("Min Prof", self)
        self.minprof_fieldgrid = QLineEdit(self)
        self.minprof_fieldgrid.setText(min_prof)
        self.maxprof_clabelgrid = QLabel("Max Prof", self)
        self.maxprof_fieldgrid = QLineEdit(self)
        self.maxprof_fieldgrid.setText(max_prof)
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.minprof_clabelgrid, self.minprof_fieldgrid)
        layout.addRow(self.maxprof_clabelgrid, self.maxprof_fieldgrid)
        layout.addRow(btn_layout)
        self.setLayout(layout)
class DefWorkdir(QDialog):
    """ Dialog for working directory """
    def __init__(self): 
        QDialog.__init__(self)
        self.setWindowTitle("Enter working directory") 
        self.resize(546,100)
        layout = QFormLayout(self)
        self.work_clabel = QLabel("WORKDIR", self)
        self.work_field = QLineEdit(self)
        self.work_field.setText(str(os.getcwd())+'/tmp/')
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.work_clabel, self.work_field)
        layout.addRow(btn_layout)
        self.setLayout(layout)

class CmemsProductDialog(QDialog):
    """ Dialog for searching cmems product and launch a request to the selected product """
    def __init__(self,parent):
        print "Read pit"
        ## Open cmems pit
        filename=str(parent.homepath)+"/statics/cmems_dic_tot_pit.p"
        self.tmp=str(parent.homepath)+"/tmp/"
        self.mainobj=parent
        self.dict_var={}
        f = file(filename, 'r')
        self.dict_prod=cPickle.load(f)
        print "Read pit  ok"
        QDialog.__init__(self)
       # self.2htab=["1",]
        self.setWindowTitle("Access CMEMS viewer")
        self.resize(579, 716)
        layout=QFormLayout(self)
        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(230, 660, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(60, 20, 491, 71))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.comboBox = QtGui.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(220, 20, 241, 31))
        self.comboBox.setObjectName("comboBox Area")
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(0, 20, 101, 31))
        self.label.setObjectName("label")
        self.groupBox_2 = QtGui.QGroupBox(self)
        self.groupBox_2.setGeometry(QtCore.QRect(50, 90, 491, 71))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.comboBox_2 = QtGui.QComboBox(self.groupBox_2)
        self.comboBox_2.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_2.setObjectName("comboBox_2 Product")
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setGeometry(QtCore.QRect(0, 20, 111, 31))
        self.label_2.setObjectName("label_2")
        self.groupBox_3 = QtGui.QGroupBox(self)
        self.groupBox_3.setGeometry(QtCore.QRect(50, 160, 491, 71))
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.comboBox_3 = QtGui.QComboBox(self.groupBox_3)
        self.comboBox_3.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_3.setObjectName("comboBox_3 Dataset")
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setGeometry(QtCore.QRect(0, 20, 111, 31))
        self.label_3.setObjectName("label_3")
        self.groupBox_4 = QtGui.QGroupBox(self)
        self.groupBox_4.setGeometry(QtCore.QRect(50, 230, 491, 71))
        self.groupBox_4.setTitle("")
        self.groupBox_4.setObjectName("groupBox_4")
        self.comboBox_4 = QtGui.QComboBox(self.groupBox_4)
        self.comboBox_4.setGeometry(QtCore.QRect(140, 20, 331, 31))
        self.comboBox_4.setObjectName("comboBox_4 Variable")
        self.label_4 = QtGui.QLabel(self.groupBox_4)
        self.label_4.setGeometry(QtCore.QRect(0, 20, 121, 31))
        self.label_4.setObjectName("label_4")
        self.groupBox_5 = QtGui.QGroupBox(self)
        self.groupBox_5.setGeometry(QtCore.QRect(40, 300, 521, 161))
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.label_5 = QtGui.QLabel(self.groupBox_5)
        self.label_5.setGeometry(QtCore.QRect(0, 60, 101, 31))
        self.label_5.setObjectName("label_5")
        self.lineEdit = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit.setGeometry(QtCore.QRect(135, 59, 111, 41))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_2.setGeometry(QtCore.QRect(365, 55, 111, 41))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.lineEdit_3 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_3.setGeometry(QtCore.QRect(247, 19, 113, 41))
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.lineEdit_4 = QtGui.QLineEdit(self.groupBox_5)
        self.lineEdit_4.setGeometry(QtCore.QRect(250, 100, 113, 41))
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.label_6 = QtGui.QLabel(self.groupBox_5)
        self.label_6.setGeometry(QtCore.QRect(165, 38, 71, 21))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtGui.QLabel(self.groupBox_5)
        self.label_7.setGeometry(QtCore.QRect(395, 28, 66, 21))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtGui.QLabel(self.groupBox_5)
        self.label_8.setGeometry(QtCore.QRect(275, 78, 66, 21))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtGui.QLabel(self.groupBox_5)
        self.label_9.setGeometry(QtCore.QRect(270, -1, 66, 21))
        self.label_9.setObjectName("label_9")
        self.groupBox_6 = QtGui.QGroupBox(self)
        self.groupBox_6.setGeometry(QtCore.QRect(50, 460, 491, 71))
        self.groupBox_6.setTitle("")
        self.groupBox_6.setObjectName("groupBox_6")
        self.comboBox_5 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_5.setGeometry(QtCore.QRect(140, 20, 141, 31))
        self.comboBox_5.setObjectName("comboBox_5 Day1")
        self.label_10 = QtGui.QLabel(self.groupBox_6)
        self.label_10.setGeometry(QtCore.QRect(0, 20, 121, 31))
        self.label_10.setObjectName("label_10")
        self.comboBox_6 = QtGui.QComboBox(self.groupBox_6)
        self.comboBox_6.setGeometry(QtCore.QRect(320, 20, 151, 29))
        self.comboBox_6.setObjectName("comboBox_6 Hour1")
        self.groupBox_7 = QtGui.QGroupBox(self)
        self.groupBox_7.setGeometry(QtCore.QRect(30, 580, 541, 71))
        self.groupBox_7.setTitle("")
        self.groupBox_7.setObjectName("groupBox_7")
        self.comboBox_7 = QtGui.QComboBox(self.groupBox_7)
        self.comboBox_7.setGeometry(QtCore.QRect(110, 20, 151, 31))
        self.comboBox_7.setObjectName("comboBox_7 Depth min")
        self.label_11 = QtGui.QLabel(self.groupBox_7)
        self.label_11.setGeometry(QtCore.QRect(0, 20, 121, 31))
        self.label_11.setObjectName("label_11")
        self.label_13 = QtGui.QLabel(self.groupBox_7)
        self.label_13.setGeometry(QtCore.QRect(290, 20, 81, 31))
        self.label_13.setObjectName("label_13")
        self.comboBox_10 = QtGui.QComboBox(self.groupBox_7)
        self.comboBox_10.setGeometry(QtCore.QRect(380, 20, 151, 29))
        self.comboBox_10.setObjectName("comboBox_10 Depth max")
        self.groupBox_8 = QtGui.QGroupBox(self)
        self.groupBox_8.setGeometry(QtCore.QRect(50, 510, 491, 71))
        self.groupBox_8.setTitle("")
        self.groupBox_8.setObjectName("groupBox_8")
        self.comboBox_8 = QtGui.QComboBox(self.groupBox_8)
        self.comboBox_8.setGeometry(QtCore.QRect(140, 20, 141, 31))
        self.comboBox_8.setObjectName("comboBox_8 Day2")
        self.label_12 = QtGui.QLabel(self.groupBox_8)
        self.label_12.setGeometry(QtCore.QRect(0, 20, 141, 31))
        self.label_12.setObjectName("label_12")
        self.comboBox_9 = QtGui.QComboBox(self.groupBox_8)
        self.comboBox_9.setGeometry(QtCore.QRect(320, 20, 151, 29))
        self.comboBox_9.setObjectName("comboBox_9 hour2")

       ## self.label_11 = QtGui.QLabel(self)
       ## self.label_11.setGeometry(QtCore.QRect(320, 300, 66, 21))
       ## self.label_11.setObjectName("label_11")
        self.retranslateUi()
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"),self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.comboBox, QtCore.SIGNAL("currentIndexChanged(int)"), self.openproducts)
        QtCore.QObject.connect(self.comboBox_2, QtCore.SIGNAL("currentIndexChanged(int)"),self.opendatasets)
        QtCore.QObject.connect(self.comboBox_3, QtCore.SIGNAL("currentIndexChanged(int)"),self.openvariables)
        QtCore.QObject.connect(self.comboBox_4, QtCore.SIGNAL("currentIndexChanged(int)"),self.opentimeanddepth)
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        print "OK launch motuclient command"
        day1=str(self.comboBox_5.currentText())
        hour1=str(self.comboBox_6.currentText())
        day2=str(self.comboBox_8.currentText())
        hour2=str(self.comboBox_9.currentText())
        date_min=day1.split('T')[0]+' '+hour1.split('0Z')[0]
        date_max=day2.split('T')[0]+' '+hour2.split('0Z')[0]
        depth_min=str(self.comboBox_7.currentText())
        depth_max=str(self.comboBox_10.currentText())
        #print depth_min,depth_max
        proxy_server=str(self.mainobj.proxyserver)
        proxy_user=str(self.mainobj.proxyuser)
        proxy_pass=str(self.mainobj.proxypass)
        cmems_user=str(self.mainobj.cmemsuser)
        cmems_pass=str(self.mainobj.cmemspass)
        variable=str(self.comboBox_4.currentText())
        product=str(self.comboBox_2.currentText())
        dataset=str(self.comboBox_3.currentText())
        lon_min=float(self.lineEdit.text())
        lon_max=float(self.lineEdit_2.text())
        lat_min=float(self.lineEdit_4.text())
        lat_max=float(self.lineEdit_3.text())
        id_product=dataset
        id_service=str(self.dict_prod[product][dataset][9][0])
        dir_out=self.tmp
        motu=str(self.dict_prod[product][dataset][3][0])
        date1=date_min.replace('-','')
        date1=date1.replace(':','')
        date1=date1.replace(' ','_')
        date2=date_max.replace('-','')
        date2=date2.replace(':','')
        date2=date2.replace(' ','_')
        outputname='ext-'+dataset+'_'+variable+'_zmin'+str(depth_min)+'zmax_'+str(depth_max)+'_'+str(date1)+'_'+str(date2)+'.nc'
        default_values = {'date_min': str(date_min),'date_max': str(date_max),'depth_min': depth_min, 'depth_max': depth_max,\
                          'longitude_max': lon_max,'longitude_min': lon_min,'latitude_min': lat_min,'latitude_max': lat_max,\
                          'describe': None, 'auth_mode': 'cas', 'motu': motu,'block_size': 65536, 'log_level': 30, 'out_dir': dir_out,\
                          'socket_timeout': None,'sync': None,  'proxy_server': proxy_server,\
                          'proxy_user': proxy_user,'proxy_pwd': proxy_pass, 'user': cmems_user, 'pwd': cmems_pass,\
                          'variable':[variable],'product_id': id_product,'service_id': id_service,'user_agent': None,'out_name': outputname}
        print "======================================="
        print "Options"
        _opts = self.load_options(default_values)
        print "======================================="
        try :
            tic = time.time()
            print "Execute motu"
            motu_api.execute_request(_opts)
            toc = time.time()
            print '| %6d sec Elapsed for Motu request |' %(toc-tic)
            print "Motu OK"
        except Exception, e:
            print "error"
            print "Execution failed: %s", e
            if hasattr(e, 'reason'):
                print "reason: %s", e.reason
            if hasattr(e, 'code'):
                print ' . code  %s: ', e.code
            if hasattr(e, 'read'):
                print ' . detail:\n%s', e.read()
        print "Open File in Mercator interface"
        print "======================================="
        #self.mainobj.updateFileNC(dir_out+outputname) 
        self.mainobj.GroupBoxPal.setEnabled(True)
        print "Open OK launch ncview"
        os.system("/home/modules/versions/64/centos7/ncview/ncview-2.1.1_gnu4.8.2/bin/ncview "+dir_out+outputname)
    def retranslateUi(self):
        print "add text"
        self.setWindowTitle("Cmems selector")
        self.label.setText("Choose Area ")
        self.label_2.setText("Choose Product ")
        self.label_3.setText("Choose Dataset")
        self.label_4.setText("Choose Variable")
        self.label_5.setText("Defined area")
        self.label_6.setText("Lon min")
        self.label_7.setText("Lon max")
        self.label_8.setText("Lat min")
        self.label_9.setText("Lat max")
        self.label_10.setText("Time min")
        self.label_11.setText("Depth min")
        self.label_12.setText("Time max")
        self.label_13.setText("Depth max")
        print "add text ok"
      #  list_area=['GLOBAL','ARCTIC','BAL','MED','IBI','NWS']
        list_area=['ARCTIC','BAL','GLOBAL','IBI','MED','NWS']
        for area in list_area : 
            self.comboBox.addItem(str(area))
        self.comboBox.setEnabled(True)
        self.comboBox_2.setEnabled(False)
        self.comboBox_3.setEnabled(False)
        print "enable OK"

    def openproducts(self):
        """Populate combobox with products """
        print "Open products"
        self.comboBox_2.setEnabled(True)
        frame=self.comboBox.currentText()
        self.comboBox_3.clear()
        self.comboBox_2.clear()
        self.comboBox_4.clear()
        print str(frame)
        for key in self.dict_prod.keys():
            if str(frame) == "BAL":
                frame1="_BAL_"
                frame2="-BAL-"
                if frame1 in key or frame2 in key :
                    self.comboBox_2.addItem(str(key))
            elif str(frame) == "NWS":
                frame1="NORTHWESTSHELF_"
                frame2="NWS"
                if frame1 in key or frame2 in key :
                    self.comboBox_2.addItem(str(key))
            else : 
                if str(frame) in key :
                    self.comboBox_2.addItem(str(key))
        self.comboBox_3.setEnabled(True)

    def opendatasets(self): 
        """Populate combobox with datasets """
        print "Open datasets"
        self.comboBox_3.clear()
        self.comboBox_4.clear()
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.comboBox_7.clear()
        self.comboBox_8.clear()
        self.comboBox_9.clear()
        self.comboBox_10.clear()
        product=str(self.comboBox_2.currentText())
        for key in self.dict_prod[product].keys():
            print "Variable"
            self.comboBox_3.addItem(str(key))
        self.comboBox_4.setEnabled(True)

    def openvariables(self): 
        """Populate combobox with variables """
        print "Open Variable"
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.comboBox_8.clear()
        self.comboBox_9.clear()
        # 0 list_variables
        # 1 list_time
        # 2 list_server
        # 3 list_DGF
        # 4 list_MFTP
        # 5 list_WMS
        # 6 list_depth
        # 7 list_resol
        # print "Open variables"
        product=str(self.comboBox_2.currentText())
        dataset=str(self.comboBox_3.currentText())
        self.comboBox_4.clear()
        url_base=self.dict_prod[product][dataset][5]
        print 'url'
        print url_base
        self.dict_var=self.getXML(url_base)
        print 'Get XML'
        for key in self.dict_var.keys():
            print "Variable"
            print key
            if not str(key).startswith('Automatically'):
                print "populate var combobox"
                self.comboBox_4.addItem(str(key))
        variable=str(self.comboBox_4.currentText()) 
        list_area=self.dict_var[str(variable)][2]
        print list_area[0],list_area[1],list_area[2],list_area[3]
        #list_zone=self.dict_prod[product][dataset][1]
        self.lineEdit.setText(list_area[0]) 
        self.lineEdit_2.setText(list_area[1])
        self.lineEdit_3.setText(list_area[2])
        self.lineEdit_4.setText(list_area[3])
        self.comboBox_5.setEnabled(True)
        self.comboBox_6.setEnabled(True)
        self.comboBox_8.setEnabled(True)
        self.comboBox_9.setEnabled(True)
        ## Open wms server
        ## Find informations from WMS
        print "Get XML Ok"

    def getXML(self,url_base):
        """ Get XML from WMS adress """
        mercator_url1="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024"
        mercator_url2="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024-2hourly-t-u-v-ssh"
        mercator_url3="http://rancmems.mercator-ocean.fr/thredds/wms/dataset-global-reanalysis-phy-001-025-ran-fr-glorys2v4-daily"
        version="1.1.1"
        print "Adress %s " %(url_base[0])
        try :
            if url_base[0] == mercator_url1 or url_base[0] == mercator_url2 or url_base[0] == mercator_url3 :
                print "Mercator case"
                if 'http_proxy' in os.environ : 
                    del os.environ['http_proxy']
                if 'https_proxy' in os.environ : 
                    del os.environ['https_proxy']
            else :
                print "Not internal server"
                if not "http_proxy" in os.environ : 
                    print "Set the http_proxy variable to pass the proxy"
                    sys.exit(1)
            ## Read xml with urllib2
            url=url_base[0]+'?service=WMS&version='+version+'&request=GetCapabilities'
            request = urllib2.Request(url, headers={"Accept" : "application/xml"})
            u = urllib2.urlopen(request)
            u=urllib2.urlopen(url)
            value=u.read()
            tree= ET.fromstring( value )
            #print ET.dump(tree)
            dict_var={}
            cap = tree.findall('Capability')[0]
            layer1 = cap.findall('Layer')[0]
            layer2 = layer1.findall('Layer')[0]
            layers = layer2.findall('Layer')
            for l in layers:
                #variable_name=l.find('Title').text
                # variable_name=l.find('Abstract').text
                ## Find Variable name
                variable_name=l.find('Name').text
                print 'variable %s ' %(variable_name)
                ## Find are of product
                list_area=[]
                box=l.find('BoundingBox')
                lonmin=box.attrib['minx']
                list_area.append(lonmin)
                lonmax=box.attrib['maxx']
                list_area.append(lonmax)
                latmin=box.attrib['miny']
                list_area.append(latmin)
                latmax=box.attrib['maxy']
                list_area.append(latmax)
                ## Find time and prof
                dims=l.findall('Extent')
                list_prof=[]
                list_time=[]
                list_tot=[]
                for dim in dims : 
                    if dim.attrib['name'] == 'elevation' :
                        list_prof=str(dim.text).split(',')
                    if dim.attrib['name'] == 'time' :
                        list_time=str(dim.text).split(',')
                if  list_prof == [] : 
                    list_prof.append('0')
                list_tot.append(list_prof)
                list_tot.append(list_time)
                list_tot.append(list_area)
                dict_var[str(variable_name)]=list_tot
        except:
            raise
            print "Error in WMS procedure"
            sys.exit(1)
        return dict_var

    def opentimeanddepth(self) :
        """Populate combobox with time and depth variables """
        print "Open time and depth"
        self.comboBox_5.clear()
        self.comboBox_6.clear()
        self.comboBox_7.clear()
        self.comboBox_8.clear()
        self.comboBox_9.clear()
        self.comboBox_10.clear()
        # Current combobox values
        product=str(self.comboBox_2.currentText())
        dataset=str(self.comboBox_3.currentText())
        variable=str(self.comboBox_4.currentText())
        resol=self.dict_prod[product][dataset][7][0]
        list_time=self.dict_var[str(variable)][1]
        if "daily" in str(resol) :
            print "Daily variable"
            for value in list_time:
                day=str(value).split()[0][:-13]
                hour=str(value).split()[0][11:]
               # hour=str(value).split()[0][14:]
                self.comboBox_5.addItem(str(day))
                self.comboBox_8.addItem(str(day))
            self.comboBox_6.addItem(str(hour))  
            self.comboBox_9.addItem(str(hour))  
        self.comboBox_6.setEnabled(True)
        if "hourly" in str(resol) :
            print "Hourly variable"
            i=0
            day_tmp=''
            for value in list_time :
                day=str(value).split()[0][:-13]
                if day_tmp != day :
                    self.comboBox_5.addItem(str(day))
                    self.comboBox_8.addItem(str(day))
                    i=i+1
                day_tmp=day
                if i == 1:
                    hour=str(value).split()[0][11:]
                    self.comboBox_6.addItem(str(hour))
                    self.comboBox_9.addItem(str(hour))
                ##print "Hour %s " %(hour)
                ##print "day %s " %(day)
        list_prof=self.dict_var[variable][0]
        for value in list_prof : 
            prof=str(value).split()[0]
            if  float(prof) < 0 :
                prof=prof.split('-')[1]
            self.comboBox_7.addItem(str(prof))
            self.comboBox_10.addItem(str(prof))

    def load_options(self,default_values):
        class cmemsval(dict):
            pass
        values=cmemsval()
        for k,v in default_values.items():
            print k,v
            setattr(values, k, v)
        return values

class SectionParams(QDialog):

    """ Dialog for params Section selection """

    def __init__(self): 
        QDialog.__init__(self)
        self.setWindowTitle("Params for section") 
        layout = QFormLayout(self)
        self.minlon_clabelgrid = QLabel("Lon min", self)
        self.minlon_fieldgrid = QLineEdit(self)
        self.maxlon_clabelgrid = QLabel("Lon max", self)
        self.maxlon_fieldgrid = QLineEdit(self)
        self.minlat_clabelgrid = QLabel("Lat min", self)
        self.minlat_fieldgrid = QLineEdit(self)
        self.maxlat_clabelgrid = QLabel("Lat max", self)
        self.maxlat_fieldgrid = QLineEdit(self)
        self.cmin_clabelgrid = QLabel("Contour min", self)
        self.cmin_fieldgrid = QLineEdit(self)
        self.cmax_clabelgrid = QLabel("Contour max", self)
        self.cmax_fieldgrid = QLineEdit(self)
        self.step_clabelgrid = QLabel("Step", self)
        self.step_fieldgrid = QLineEdit(self)
        self.profmin_clabelgrid = QLabel("Prof min", self)
        self.profmin_fieldgrid = QLineEdit(self)
        self.profmax_clabelgrid = QLabel("Prof max", self)
        self.profmax_fieldgrid = QLineEdit(self)
        self.namesection_clabelgrid = QLabel("Section name", self)
        self.namesection_fieldgrid = QLineEdit(self)
        self.ok_btn = QPushButton("OK", self)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout = QHBoxLayout(self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(self.minlon_clabelgrid, self.minlon_fieldgrid)
        layout.addRow(self.maxlon_clabelgrid, self.maxlon_fieldgrid)
        layout.addRow(self.minlat_clabelgrid, self.minlat_fieldgrid)
        layout.addRow(self.maxlat_clabelgrid, self.maxlat_fieldgrid)
        layout.addRow(self.cmin_clabelgrid, self.cmin_fieldgrid)
        layout.addRow(self.cmax_clabelgrid, self.cmax_fieldgrid)
        layout.addRow(self.step_clabelgrid, self.step_fieldgrid)
        layout.addRow(self.profmin_clabelgrid, self.profmin_fieldgrid)
        layout.addRow(self.profmax_clabelgrid, self.profmax_fieldgrid)
        layout.addRow(self.namesection_clabelgrid, self.namesection_fieldgrid)
        layout.addRow(btn_layout)
        self.setLayout(layout)
