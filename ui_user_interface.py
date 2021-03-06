from PyQt4.QtGui import *
from PyQt4 import QtGui, QtCore
from qgis.core import *
from qgis.gui import *

import resources
## UI interface For Mercator Application
## C.REGNIER November 2015

class Ui_ExplorerWindow(object):

    def setupUi(self, window):
        window.setWindowTitle("Mercator Explorer")
        self.centralWidget = QtGui.QWidget(window)
        self.centralWidget.setMinimumSize(800, 400)
        window.setCentralWidget(self.centralWidget)
        self.menubar = window.menuBar()
        self.fileMenu = self.menubar.addMenu("File")
        self.viewMenu = self.menubar.addMenu("View")
        self.modeMenu = self.menubar.addMenu("Action")
        self.openMenu = self.menubar.addMenu("Open")
        ## Add toolbar to the menu
        self.toolbar = QtGui.QToolBar(window)
        window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        # Palette tool 
        self.GroupBoxPal = QtGui.QGroupBox(self.centralWidget)         
        self.vboxPalExplore=QtGui.QHBoxLayout(self.centralWidget)
        # Creation of a Colormap combobox
        self.combocolor=QgsColorRampComboBox()    
        # Populate the combobox with default style colors 
        self.combocolor.populate(QgsStyleV2().defaultStyle())  
        ## Add combocolor widget
        self.vboxPalExplore.addWidget(self.combocolor)
        ## Add Checkbox for palette
        self.invpal= QtGui.QCheckBox()
        self.invpal.setChecked(False)
        self.invpal.setObjectName("Invert_pal")
        self.invpal.setText("Invert")
        self.vboxPalExplore.addWidget(self.invpal)
        ## Create variables
        self.cboVars = QtGui.QComboBox()
        self.cboVars.setObjectName("cboVars")      
        self.cboVars.setEditable(True)
        self.cboVars.lineEdit().setText("Variables")
        self.cboVars.resize(60, 100)
        self.vboxPalExplore.addWidget(self.cboVars)
        # Create Dimensions combobox
        self.cboDim = QtGui.QComboBox()
        self.cboDim.setObjectName("cboDim")  
        self.cboDim.setEditable(True)
        self.cboDim.lineEdit().setText("Dims")
        self.vboxPalExplore.addWidget(self.cboDim)
        ## Create classes for colorbar
        self.counterclasse = QtGui.QLabel('Classes')
        self.vboxPalExplore.addWidget(self.counterclasse)
        ## Change number of colorramp values
        self.cboNbcolor = QtGui.QSpinBox()
        self.cboNbcolor.setMinimum(5)
        self.cboNbcolor.setMaximum(100)
        self.cboNbcolor.setObjectName("Nbcolor_classes")      
        self.cboNbcolor.resize(60, 100)
        self.vboxPalExplore.addWidget(self.cboNbcolor)
        ##Create Cmin Cmax 
        self.valmin = QtGui.QLabel('Min')
        self.vboxPalExplore.addWidget(self.valmin)
        self.Valminvalue = QtGui.QLineEdit()
        self.Valminvalue.resize(60, 50)
        self.vboxPalExplore.addWidget(self.Valminvalue)
        self.valmax = QtGui.QLabel('Max')
        self.vboxPalExplore.addWidget(self.valmax)
        self.Valmaxvalue = QtGui.QLineEdit()
        self.Valmaxvalue.resize(60, 50)
        self.vboxPalExplore.addWidget(self.Valmaxvalue)
        ## Create variables
        self.secVars = QtGui.QComboBox()
        self.secVars.setObjectName("secVars")      
        self.secVars.setEditable(True)
        self.vboxPalExplore.addWidget(self.secVars)
        # Create Basemap
        self.basemap=QtGui.QPushButton()
        self.basemap.setChecked(True)
        self.basemap.setObjectName("Basemap")
        self.basemap.setText("Basemap")
        self.comp= QtGui.QCheckBox()
        self.comp.setChecked(False)
        self.vboxPalExplore.addWidget(self.basemap)
        self.GroupBoxPal.setLayout(self.vboxPalExplore)
        # Define actions linked to the toolbar 
        self.actionQuit = QtGui.QAction("Quit", window)
        self.actionQuit.setShortcut(QtGui.QKeySequence.Quit)
        image_dir=":/images/icons/"
        self.actionZoomIn = QAction(QIcon(image_dir+"mActionZoomIn.png"),str("Zoom in"), window)
        self.actionZoomIn.setShortcut(QtGui.QKeySequence.ZoomIn)
        self.actionZoomOut = QAction(QIcon(image_dir+"mActionZoomOut.png"),str("Zoom out"), window)
        self.actionZoomOut.setShortcut(QtGui.QKeySequence.ZoomOut)
        self.actionPlotCurrent=QAction(QIcon(image_dir+"VectorFieldRendererIcon.png"),str("Plot_Current"),window)
        self.actionPan = QAction(QIcon(image_dir+"mActionPan.png"),str("Pan"), window)
        self.actionPan.setShortcut("Ctrl+1")
        self.actionExplore=QAction(QIcon(image_dir+"mActionIdentify.svg"),str("Explore"),window)
        self.actionSelect=QAction(QIcon(image_dir+"mActionCapturePolygon.png"),str("Selectool"),window)
        self.actionDistance=QAction(QIcon(image_dir+"mActionCapturePolygon.png"),str("Selectool"),window)
        self.actionCapture=QAction(QIcon(image_dir+"mActionCaptureLine.png"),str("Selectool"),window)
        self.actionReadhdf=QAction(QIcon(image_dir+"mActioncomputediff.png"),str("Read hdf"),window)
        #self.actionReadCmemsCatalog=QAction(QIcon(image_dir+"mActioncomputediff.png"),str("Cmems catalog"),window)
        self.actionThreddsViewer=QAction(QIcon(image_dir+"ThreddsViewer.png"),str("Thredds VIewer"),window)
        self.actionMakeoperation=QAction(QIcon(image_dir+"mActionAddGridLayer.png"),str("Make operations"),window)
        self.actionZoomFull=QAction(QIcon(image_dir+"mActionZoomFullExtent.png"),str("Zoom Full"),window)
        self.actionComputeDiff=QAction(QIcon(image_dir+"mActioncomputediff.png"),str("Compute Diff"),window) 
        self.actionSaveMap=QAction(QIcon(image_dir+"mActionSaveMapAsImage.png"),str("Save"),window)
        self.actionGetValue = QAction(QIcon(image_dir+"mActionCapturePoint.png"),str("Get Value"), window)
        self.actionPlotProfile = QAction(QIcon(image_dir+"mActionCapturePoint2.png"),str("Get Value"), window)
        self.actionAddGridd= QAction(QIcon(image_dir+"mActionAddGridLayer.png"),str("Grid"), window) 
        self.actionRescaling= QAction(QIcon(image_dir+"mActionDraw.png"),str("Rescaling"), window) 
        self.actionRescaling.setShortcut("Ctrl+r")
        self.actionAddWmsLayer=QAction(QIcon(image_dir+"mActionAddWmsLayer.png"),str("WMS/WCS"),window)
        self.actionAddRaster= QAction(QIcon(image_dir+"mActionAddRasterLayer.png"),str("Nectdf Raster"),window)
        self.actionAddVector= QAction(QIcon(image_dir+"mActionAddOgrLayer.png"),str("Vector"),window)
        self.actionAddGeojson= QAction(QIcon(image_dir+"mIconPointLayer.png"),str("Geojson"),window)
        self.actionPlotsection= QAction(QIcon(image_dir+"mIconPointLayer.png"),str("Plot section"),window)
        self.actionReadOla= QAction(QIcon(image_dir+"mIconPointLayer.png"),str("Read Ola File"),window)
        self.actionTransparency= QAction(QIcon(image_dir+"mIconTransparency.png"),str("Transparency"),window)
        self.actionContouring= QAction(QIcon(image_dir+"mIconContour.svg"),str("Contour"),window)
        self.actionLoadSvg=QAction(QIcon(image_dir+"icon_svg2color.png"),str("Colorbartool"), window)
        self.actionReadLightout=QAction(QIcon(image_dir+"mIconRasterLayer.svg"),str("Lightout"),window)
        self.actionZoomIn.setCheckable(False)
        self.actionZoomOut.setCheckable(False)
        self.actionPan.setCheckable(True)
        self.actionComputeDiff.setCheckable(True)
	self.actionMakeoperation.setCheckable(True)
	self.actionMakeoperation.setEnabled(False)

        self.actionZoomFull.setCheckable(False)
        self.actionSaveMap.setCheckable(True)
        self.actionAddGridd.setCheckable(True)
        self.actionAddRaster.setCheckable(True)
        self.actionAddVector.setCheckable(True)
        self.actionAddGeojson.setCheckable(True) 
        self.actionReadOla.setCheckable(False)
        self.actionTransparency.setCheckable(True) 
        self.actionLoadSvg.setCheckable(True)
        self.actionReadLightout.setCheckable(True)
	self.actionAddWmsLayer.setCheckable(True)
        #self.actionSelect.setEnabled(True) 
        self.actionDistance.setEnabled(True)
        self.actionCapture.setEnabled(False)
        self.actionPlotCurrent.setEnabled(False)
        self.actionGetValue.setEnabled(False)
        self.actionPlotProfile.setEnabled(False)
	self.actionReadhdf.setEnabled(True)
        self.actionPlotsection.setEnabled(False)
        #self.actionPlotsection.setEnabled(True)
	#self.actionReadCmemsCatalog.setEnabled(True)
        self.actionTransparency.setEnabled(False)
        self.actionContouring.setEnabled(False)
        self.actionExplore.setEnabled(False)
        self.actionThreddsViewer.setEnabled(True)
        ## Populate Map tools
        self.fileMenu.addAction(self.actionQuit)
        self.viewMenu.addAction(self.actionZoomIn)
        self.viewMenu.addAction(self.actionZoomOut)
        self.viewMenu.addAction(self.actionPan)
        self.viewMenu.addAction(self.actionZoomFull)
        self.viewMenu.addAction(self.actionSaveMap)
        self.openMenu.addAction(self.actionAddGridd)
        self.openMenu.addAction(self.actionAddRaster)
        self.openMenu.addAction(self.actionAddVector)
        self.openMenu.addAction(self.actionAddWmsLayer)
        self.openMenu.addAction(self.actionAddGeojson)
        self.openMenu.addAction(self.actionLoadSvg)
        self.openMenu.addAction(self.actionReadLightout)
        self.modeMenu.addAction(self.actionPlotCurrent)
        self.modeMenu.addAction(self.actionReadhdf)
        #self.modeMenu.addAction(self.actionReadCmemsCatalog)
        self.modeMenu.addAction(self.actionThreddsViewer)
        self.modeMenu.addAction(self.actionComputeDiff)
        self.modeMenu.addAction(self.actionContouring)
        self.modeMenu.addAction(self.actionMakeoperation)
        self.modeMenu.addAction(self.actionReadOla)
        self.modeMenu.addAction(self.actionPlotsection)
        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)
        self.toolbar.addAction(self.actionZoomFull)
        self.toolbar.addAction(self.actionGetValue)
        self.toolbar.addAction(self.actionAddGridd)
        self.toolbar.addAction(self.actionAddRaster)
        self.toolbar.addAction(self.actionAddVector)
        self.toolbar.addAction(self.actionAddGeojson)
        self.toolbar.addAction(self.actionReadLightout)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.actionRescaling)
        self.toolbar.addAction(self.actionTransparency)
        self.toolbar.addAction(self.actionContouring)
        self.toolbar.addAction(self.actionPlotCurrent)
        #self.toolbar.addAction(self.actionSelect)
        self.toolbar.addAction(self.actionDistance)
        self.toolbar.addAction(self.actionCapture)
        self.toolbar.addAction(self.actionPlotProfile)
        self.toolbar.addAction(self.actionExplore)
        #self.toolbar.addAction(self.actionAddWmsLayer)
       # self.toolbar.addAction(self.actionLoadSvg)
        self.toolbar.addWidget(self.GroupBoxPal)
        ## Create the status bar
        self.statusbar= QStatusBar()
        self.statusbar.setObjectName("StatusBar")
        self.setStatusBar(self.statusbar)
        ## Add Projection 
        self.proj=QtGui.QPushButton()
        self.proj.setChecked(True)
        self.proj.setObjectName("Proj")
        self.proj.setText("Projection")
        self.statusbar.addPermanentWidget(self.proj,0)
       # icon = QIcon("image.png")
        ## Add value status
        self.value=QLabel()
        self.value.setFrameStyle( QFrame.StyledPanel )
        self.value.setMinimumWidth( 40 )
        self.statusbar.addPermanentWidget(self.value,0)
        self.value.setText("Value")
        self.valueXY=QLabel()
        self.valueXY.setFrameStyle( QFrame.Box )
        self.valueXY.setMinimumWidth( 120 )
        self.statusbar.setSizeGripEnabled( False )
        self.statusbar.addPermanentWidget(self.valueXY,0)
        ## Add Coord value
        self.coordvalue=QLabel()
        self.coordvalue.setFrameStyle( QFrame.StyledPanel )
        self.coordvalue.setMinimumWidth( 20 )
        self.statusbar.addPermanentWidget(self.coordvalue,0)
        self.coordvalue.setText("Coords")
        self.lblXY = QLabel()
        self.lblXY.setFrameStyle( QFrame.Box )
        self.lblXY.setMinimumWidth( 180 )
        self.statusbar.setSizeGripEnabled( False )
        self.statusbar.addPermanentWidget( self.lblXY, 0 )
        #Self.lblScale = QLabel()
        #Self.lblScale.setFrameStyle( QFrame.StyledPanel )
        #Self.lblScale.setMinimumWidth( 50 )
        #Self.statusbar.addPermanentWidget( self.lblScale, 0 )
        self.GroupBoxPal.setEnabled(True) 
        window.resize(window.sizeHint())

