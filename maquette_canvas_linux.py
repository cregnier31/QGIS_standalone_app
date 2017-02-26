# -*-  coding: utf-8 -*-
## Exemple de projection de shapefile avec pyqgis
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import qgis.utils
import numpy as np
import os, sys,re,math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import netCDF4
from osgeo import gdal
from osgeo import osr
from math import ceil
#import processing
sys.path.append('/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0')
from VectorFieldRenderer import VectorFieldRenderer
from GDALParameters import GDALParameters
from Reader import read_netcdf_variable,array_to_raster
from Grid import Grid
from contour import ContourDialog
from contour import  ContourError

QgsApplication.setPrefixPath("/usr", True)
QgsApplication.initQgis()
#import SVG2ColoR.SVG2ColoRDialog
#from SVG2ColoR.SVG2ColoRDialog import SVG2ColoRDialog
class GridLayerType(QgsPluginLayerType):
    def __init__(self):
        QgsPluginLayerType.__init__(self, "GridLayer")
    def createLayer(self):
        return GridLayer()

class GridLayer(QgsPluginLayer):    
    def __init__(self):        
        QgsPluginLayer.__init__(self, "GridLayer", "Grid Layer")        
        self.setValid(True)
        self.setCrs(QgsCoordinateReferenceSystem(4326)) 

    def createLayer(self):
        return GridLayer()

    def draw(self, renderContext):       
        painter = renderContext.painter()       
        self.setExtent(QgsRectangle(-180, 90, 180, 90))
        extent = renderContext.extent()
        xMin = int(math.floor(extent.xMinimum()))        
        xMax = int(math.ceil(extent.xMaximum()))        
        yMin = int(math.floor(extent.yMinimum()))        
        yMax = int(math.ceil(extent.yMaximum())) 
        pen = QPen()        
        pen.setColor(QColor("light gray"))
        pen.setWidth(1.0)
        painter.setPen(pen)
        mapToPixel = renderContext.mapToPixel() 
#     drawing longitude 
        for x in range(xMin, xMax+1):            
            coord1 = mapToPixel.transform(x, yMin)
            coord2 = mapToPixel.transform(x, yMax)
            painter.drawLine(coord1.x(), coord1.y(),
            coord2.x(), coord2.y())
#     drawing latitude
        for y in range(yMin, yMax+1):
            coord1 = mapToPixel.transform(xMin, y)
            coord2 = mapToPixel.transform(xMax, y)
            painter.drawLine(coord1.x(), coord1.y(),
            coord2.x(), coord2.y())
        return True
        
class Crea_layer(object):
    def __init__(self,name,type):
        self.type=type
        self.name = name
        self.layer =  QgsVectorLayer(self.type, self.name , "memory")
        self.pr =self.layer.dataProvider()
        #self.layer.setLayerTransparency(0)
        props = { 'color' : 'transparent', 'style' : 'no', 'style' : 'solid' }
        s = QgsFillSymbolV2.createSimple(props)
        self.layer.setRendererV2( QgsSingleSymbolRendererV2( s ) ) 
    def create_poly(self,points):
        self.seg = QgsFeature()
        #props = { 'color' : '0,0, 255', 'style' : 'no', 'style' : 'solid' }
#        s = QgsFillSymbolV2.createSimple(props)
      #  self.seg.setRendererV2( QgsSingleSymbolRendererV2( s ) ) 
        self.seg.setGeometry(QgsGeometry.fromPolygon([points]))
        self.pr.addFeatures( [self.seg] )
        self.layer.updateExtents()
    @property
    def disp_layer(self):
        
        self.layer.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayers([self.layer])

### Extension of a maptool object
class PointTool(QgsMapTool):   
    def __init__(self, canvas,layer):
        QgsMapTool.__init__(self, canvas)
        cursor = QCursor()
        cursor.setShape(Qt.WhatsThisCursor)
        #QApplication.instance().setOverrideCursor(cursor)
	    #self.cursor = QCursor(QPixmap(identify_cursor), 1, 1)
        #self.cursor = QCursor(Qt.WaitCursor)
        self.canvas = canvas    
 	#self.button = button
	#self.button.setCheckable(True)
	self.layer=layer
    def canvasPressEvent(self, event):
	print 'canvasPresEvent OK'
        print self.canvas.getCoordinateTransform()
	print 'canvasPresEvent'
        pass

    def canvasMoveEvent(self,event):
        #print 'canvasMoveEvent'
        x = event.pos().x()
        y = event.pos().y()
	#QgsMapTool.activate(self)
        #self.canvas.setCursor(self.cursor)
	self.emit( SIGNAL("moved"), QPoint(event.pos().x(), event.pos().y()) )
       # QMessageBox.information(None, "Coords values", " x: " + str(point.x()) + " Y: " + str(point.y()) )

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
	print 'canvasReleaseEvent'
        print x,y
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        extent = self.canvas.extent()
        width = round(extent.width() / self.canvas.mapUnitsPerPixel());
        height = round(extent.height() / self.canvas.mapUnitsPerPixel());
	print "---width height ---"
        print width,height
	layer=self.layer
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
	print self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
	position=self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
	if position is not None:
	    ident = layer.dataProvider().identify(position, QgsRaster.IdentifyFormatValue,self.canvas.extent(), width, height ).results()
	    iband=1
	    if not ident or not ident.has_key( iband ): # should not happen
                  bandvalue = "?"
            else:
              bandvalue = ident[iband]
              if bandvalue is None:
                 bandvalue = "no data"
        ## Add message box to see coordinates
        QMessageBox.information(None, "Clicked coords", " Lon: " + str(point.x()) + " Lat: " + str(point.y()) + "\n Value: " + str(bandvalue))

    def activate(self):
        pass

    def deactivate(self):
        pass

    def isZoomTool(self):
        return False

    def isTransient(self):
        return False

    def isEditTool(self):
        return True

### Class to create gridLayer
class Create_gridlayer(object):
    def __init__(self,name,type,canvas,layer):
        self.type=type
        self.name = name
	self.canvas=canvas
        self.layer1=  layer
        self.layer =  QgsVectorLayer(self.type, self.name , "memory")
        self.pr =self.layer.dataProvider() 
    def create_poly(self,points):
        self.seg = QgsFeature()  
        self.seg.setGeometry(QgsGeometry.fromPolygon([points]))
        self.pr.addFeatures( [self.seg] )
        self.layer.updateExtents()
    @property
    def disp_layer(self):
        # Add Layer set to registry
        QgsMapLayerRegistry.instance().addMapLayers([self.layer])
        ## Create list of layers
        # QList <QgsMapCanvasLayer> 
        myLayerSet=[]
        #Change properties for layer2 
	# Change the color of the layer to gray
	self.layer.setLayerTransparency(80)
       # symbol_layer = self.layer.rendererV2().symbols()[0].symbolLayer(0)
       # symbol_layer.setColor(QColor(Qt.white))
       # self.layer.rendererV2().symbols()[0].changeSymbolLayer(0, symbol_layer)
        cl2=QgsMapCanvasLayer(self.layer)
	myLayerSet.append(cl2)
        cl1=QgsMapCanvasLayer(self.layer1)
	myLayerSet.append(cl1)
	# set extent to the extent of our layer
        self.canvas.setExtent(self.layer.extent())
        self.canvas.enableAntiAliasing(True)    
        self.canvas.freeze(False)
        # set the map canvas layer set
        self.canvas.setLayerSet(myLayerSet)
        ## Refreshing canvas
        self.canvas.refresh()
        self.canvas.update()
        
class MyMenu(QMenu):                                                                                                                    

    def __init__(self):
        QMenu.__init__(self)
        self.ignoreHide = False

    def setVisible(self,visible):
        if self.ignoreHide:
            self.ignoreHide = False
            return
        QWidget.setVisible(self,visible)

    def mouseReleaseEvent(self,event):
        action = self.actionAt(event.pos())
        if action is not None:
            #if (actions_with_showed_menu.contains (action))
            self.ignoreHide = True
        QMenu.mouseReleaseEvent(self,event)


# Some helpful functions
def formatNumber( number, precision=0, group_sep='.', decimal_sep=',' ):
   """
   number: Number to be formatted
   precision: Number of decimals
   group_sep: Miles separator
   decimal_sep: Decimal separator
   """
   number = ( '%.*f' % ( max( 0, precision ), number ) ).split( '.' )
   integer_part = number[ 0 ]
   if integer_part[ 0 ] == '-':
     sign = integer_part[ 0 ]
     integer_part = integer_part[ 1: ]
   else:
     sign = ''
   if len( number ) == 2:
     decimal_part = decimal_sep + number[ 1 ]
   else:
     decimal_part = ''
     integer_part = list( integer_part )
     c = len( integer_part )
   while c > 3:
     c -= 3
     integer_part.insert( c, group_sep )
     return sign + ''.join( integer_part ) + decimal_part
def formatToDegrees( number ):
   """ Returns the degrees-minutes-seconds form of number """
   sign = ''
   if number < 0:
      number = math.fabs( number )
      sign = '-'
      deg = math.floor( number )
      minu = math.floor( ( number - deg ) * 60 )
      sec = ( ( ( number - deg ) * 60 ) - minu ) * 60
      return sign + "%.0f"%deg + 'ÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂÃÂº ' + "%.0f"%minu + "' " \
       + "%.2f"%sec + "\""
def show_error(title, text):
   QMessageBox.critical(None, title, text,
   QMessageBox.Ok | QMessageBox.Default,
   QMessageBox.NoButton)
   print >> sys.stderr, 'E: Error. Exiting ...'
   print __doc__
   sys.exit(1)

 

## Class MyCanvas => custom canvas for Mercator application
class MyCanvas(QMainWindow):
  #def __init__(self, layer,band,filename):
  def __init__(self):
    QMainWindow.__init__(self)
   # self.layer=layer
   # self.band=band
    #self.filename=filename
    # set widgets layouts
    self.layers = []
    self.mainLayout = QtGui.QHBoxLayout()
    self.setLayout(self.mainLayout)
    # Create canevas
    self.canvas = QgsMapCanvas()
    self.canvas.setCanvasColor(Qt.white)
    self.canvas.useImageToRender(True)
    self.canvas.enableAntiAliasing(True)
    #self.canvas.setExtent(layer.extent())
    self.setCentralWidget(self.canvas)
    ## Create Legend widget
    self.addLegendtoLayer()

    ## Define CRS projection
    #if iface.mapCanvas().mapRenderer().hasCrsTransformEnabled():    
    crs=QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)  
    self.canvas.setDestinationCrs(crs)
    self.iface=iface
    # Creation of a Colormap combobox
    self.combocolor=QgsColorRampComboBox()    
    # Populate the combobox with default style colors 
    self.combocolor.populate(QgsStyleV2().defaultStyle())     
    #self.combocolor.setEnabled(False)
    self.cboNbcolor = QtGui.QSpinBox()
    self.cboNbcolor.setMinimum(5)
    self.cboNbcolor.setMaximum(100)
    self.cboNbcolor.setObjectName("Nbcolor_classes")      
    self.cboNbcolor.resize(60, 100)
    ## Add Checkbox for grid
    self.checkbox= QtGui.QCheckBox()
    self.checkbox.setChecked(False)
    self.checkbox.setObjectName("AddGridOverlay")
    self.checkbox.setText("Grid on")
    ## Add Checkbox for palette
    self.invpal= QtGui.QCheckBox()
    self.invpal.setChecked(False)
    self.invpal.setObjectName("Invert_pal")
    self.invpal.setText("Invert")
    ## Create variables
    self.cboVars = QtGui.QComboBox()
    self.cboVars.setObjectName("cboVars")      
    self.cboVars.resize(60, 100)
    ## Create dimension 
    self.cboDim = QtGui.QComboBox()
    self.cboDim.setObjectName("cboDim")      
    # Create Basemap
    self.gridGroupBox = QtGui.QGroupBox("Basemap")
    self.basemap=QtGui.QComboBox(self.gridGroupBox)
    self.basemap2=QtGui.QPushButton(self.gridGroupBox)
    self.basemap2.setText("Basemap")
    #self.basemap = QtGui.QComboBox()
    #self.basemap = QtGui.QCheckBox()
    self.basemap.setObjectName("Basemap")
    self.updatebasemap()
    ## Test composer
    self.comp= QtGui.QCheckBox()
    self.comp.setChecked(False)
    self.comp.setObjectName("Componer")
    self.comp.setText("Componer")
    ## Add grid Layer to canvas
    ## Construction of buttons
    image_dir="/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/icons/"
#image_dir="C:/Users/Charly/Documents/DEV/pyqgis/images/"
    
    self.actioncontour=QAction(QIcon(image_dir+"contour.png"),str("Contour"),self)
    self.actionLoadSvg=QAction(QIcon(image_dir+"icon_svg2color.png"),str("Colorbartool"), self)
    actionZoomIn = QAction(QIcon(image_dir+"mActionZoomIn.png"),str("Zoom in"), self)
    actionZoomOut = QAction(QIcon(image_dir+"mActionZoomOut.png"),str("Zoom out"), self)
    actionPan = QAction(QIcon(image_dir+"mActionPan.png"),str("Pan"), self)
    actionZoomFull=QAction(QIcon(image_dir+"mActionZoomFullExtent.png"),str("Zoom Full"),self)
    actionSaveMap=QAction(QIcon(image_dir+"mActionSaveMapAsImage.png"),str("Save"),self)
    self.actionGetValue = QAction(QIcon(image_dir+"mActionCapturePoint.png"),str("Get Value"), self)
    actionAddGridd= QAction(QIcon(image_dir+"mActionAddOgrLayer.png"),str("Plot Grid"), self) 
    self.actionRescaling= QAction(QIcon(image_dir+"mActionDraw.png"),str("Rescaling"), self) 
    actionAddRaster= QAction(QIcon(image_dir+"mActionAddRasterLayer.png"),str("Plot Raster"),self)
    self.actionPlotCurrent= QAction(QIcon(image_dir+"mIconPolygonLayer.png"),str("Plot Current"),self)
    actionAddVector= QAction(QIcon(image_dir+"mActionAddLayer.png"),str("PlotVector"),self)
    actionAddGeojson= QAction(QIcon(image_dir+"mIconPointLayer.png"),str("PlotGeojson"),self)

    actionZoomIn.setCheckable(False)
    actionZoomOut.setCheckable(False)
    actionPan.setCheckable(True)
    actionZoomFull.setCheckable(False)
    actionSaveMap.setCheckable(True)
    actionAddGridd.setCheckable(True)
    self.actionPlotCurrent.setEnabled(False)
    self.actionLoadSvg.setCheckable(True)
    actionAddRaster.setCheckable(True)
    actionAddVector.setCheckable(True)
    actionAddGeojson.setCheckable(True)
    self.actioncontour.setCheckable(True)
    self.actionRescaling.setCheckable(False)
    self.actionRescaling.setEnabled(False)
    self.compose=1
    ##-----------------------------------
    ## Create menus
    ## create the action behaviours
    self.connect(actionZoomIn, SIGNAL("triggered()"), self.zoomIn)
    self.connect(actionZoomOut, SIGNAL("triggered()"), self.zoomOut)
    self.connect(actionPan, SIGNAL("triggered()"), self.pan)
    self.connect(actionZoomFull, SIGNAL("triggered()"), self.zoomFull)
    self.connect(actionSaveMap, SIGNAL("triggered()"), self.saveMap)
    self.connect(self.actionGetValue, SIGNAL("triggered()"), self.getValue)
    self.connect(actionAddGridd, SIGNAL("triggered()"), self.plot_grid2)
    self.connect(actionAddRaster, SIGNAL("triggered()"), self.addRaster)
    self.connect(actionAddVector, SIGNAL("triggered()"), self.addVector)
    self.connect(self.actionPlotCurrent,SIGNAL("triggered()"), self.plotcurrent)
    self.connect(actionAddGeojson, SIGNAL("triggered()"), self.addGeojson)
    self.connect(self.actionLoadSvg,SIGNAL("triggered()"),self.launchSvg2color)
    self.connect(self.cboNbcolor, SIGNAL("valueChanged(int)"),self.actionMenu2)
    self.connect(self.actioncontour,SIGNAL("triggered()"), self.plotContour)
    #self.connect(self.actionRescaling, SIGNAL("triggered()"),self.redrawLayer)
    self.connect(self.actionRescaling, SIGNAL("triggered()"),self.actionMenu2)
    self.connect(self.invpal, SIGNAL("stateChanged(int)"),self.actionMenu2)
    self.connect(self.comp, SIGNAL("stateChanged(int)"),self.actionComp)
 #   self.connect(self.canvas, SIGNAL( "scaleChanged(double)" ),self.changeScale )
 #   self.connect(self.basemap2, SIGNAL("triggered(QAction *)"), self.on_basemap_triggered)
    self.connect(self.canvas, SIGNAL( "xyCoordinates(const QgsPoint&)" ),self.updateXY )
    #self.connect(self.canvas, SIGNAL( "xyCoordinates(const QgsPoint&)" ),self.move_xy )
#    self.connect(self.canvas, SIGNAL("moved"),self.move_xy)
    self.connect(self.cboVars, SIGNAL("currentIndexChanged(QString)"), self.updateVariable)
    self.connect(self.cboDim, SIGNAL("currentIndexChanged(QString)"), self.updateDims)
    #self.connect(self.basemap, SIGNAL("currentIndexChanged(QString)"), self.on_basemap_triggered)
    #self.connect( app, SIGNAL( "loadPgLayer" ), self.loadLayer ) 
    self.layerSRID = ''
    ##self.loadLayer( dictOpts )
    ## Connect the combobox to action 
    #self.connect(self.combocolor,SIGNAL("currentIndexChanged(int)"), self.redrawLayer)
    self.connect(self.combocolor,SIGNAL("currentIndexChanged(int)"), self.actionMenu2)
    ## Create Map tools
    self.toolbar = self.addToolBar("Canvas actions")
    self.toolbar.addAction(actionZoomIn)
    self.toolbar.addAction(actionZoomOut)
    self.toolbar.addAction(actionPan)
    self.toolbar.addAction(actionZoomFull)
    self.toolbar.addAction(actionSaveMap)
    self.toolbar.addAction(self.actionGetValue)
    self.toolbar.addAction(actionAddGridd)
    self.toolbar.addAction(actionAddRaster)
    self.toolbar.addAction(actionAddVector)
    self.toolbar.addAction(actionAddGeojson)
    self.toolbar.addAction(self.actionRescaling)
    self.toolbar.addAction(self.actionPlotCurrent)
    #self.toolbar.addAction(self.actionLoadSvg)
    self.toolbar.addAction(self.actioncontour)
    ## Create the status bar
    self.statusbar= QStatusBar(self)
    self.statusbar.setObjectName("StatusBar")
    self.setStatusBar(self.statusbar)
    self.value=QLabel()
    self.value.setFrameStyle( QFrame.StyledPanel )
    self.value.setMinimumWidth( 40 )
    self.statusbar.addPermanentWidget(self.value,0)
    self.value.setText("Value")

    self.valueXY=QLabel()
    self.valueXY.setFrameStyle( QFrame.StyledPanel )
    self.valueXY.setMinimumWidth( 170 )
    self.statusbar.addPermanentWidget(self.valueXY,0)

    self.coordvalue=QLabel()
    self.coordvalue.setFrameStyle( QFrame.StyledPanel )
    self.coordvalue.setMinimumWidth( 20 )
    self.statusbar.addPermanentWidget(self.coordvalue,0)
    self.coordvalue.setText("Coords")
    self.lblXY = QLabel()
    self.lblXY.setFrameStyle( QFrame.Box )
    self.lblXY.setMinimumWidth( 170 )
    self.lblXY.setAlignment( Qt.AlignCenter )
    self.statusbar.setSizeGripEnabled( False )
    self.statusbar.addPermanentWidget( self.lblXY, 0 )
    self.lblScale = QLabel()
    self.lblScale.setFrameStyle( QFrame.StyledPanel )
    self.lblScale.setMinimumWidth( 140 )
    self.statusbar.addPermanentWidget( self.lblScale, 0 )

    # create layer explorer pane
    self.explorer = QDockWidget("Layers")
    self.explorer.resize(60, 100)
    self.explorerListWidget = QtGui.QListWidget(self.canvas)#~
    self.explorerListWidget.setObjectName("listWidget")#~
    self.explorer.setWidget(self.explorerListWidget)#~

#    self.legendock= QDockWidget("Legend")
#    #self.legendock.resize(100,20)
#    self.legendock.setWidget(LegendView(QgsProject.instance().layerTreeRoot()))
#    print "add legenddock"
    #iface.addDockWidget(Qt.LeftDockWidgetArea, self.legendock)
    # create the map tools
    self.toolPan = QgsMapToolPan(self.canvas)
    self.toolPan.setAction(actionPan)

    self.toolZoomIn = QgsMapToolZoom(self.canvas,False) # false = in
    self.toolZoomIn.setAction(actionZoomIn)
     

    self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
    self.toolZoomOut.setAction(actionZoomOut)

    if iface.activeLayer() :
        self.layer=iface.activeLayer()
        self.getvalue=PointTool(self.canvas,self.layer) # false = in
        self.getvalue.setAction(self.actionGetValue)           
  
    
    # Palette tool 
    self.GroupBoxPal = QtGui.QGroupBox(self.canvas)         
    self.vboxPalExplore=QtGui.QHBoxLayout(self.canvas)
    self.vboxPalExplore.addWidget(self.combocolor)
    self.vboxPalExplore.addWidget(self.cboNbcolor)
    self.vboxPalExplore.addWidget(self.checkbox)
    self.vboxPalExplore.addWidget(self.invpal)
    self.vboxPalExplore.addWidget(self.comp)
    self.vboxPalExplore.addWidget(self.cboVars)
    self.vboxPalExplore.addWidget(self.cboDim)
    self.vboxPalExplore.addWidget(self.basemap2)
    self.GroupBoxPal.setLayout(self.vboxPalExplore)
    self.mainLayout.addWidget(self.GroupBoxPal)
    self.GroupBoxPal.setEnabled(False) 
    print "Creation canevas OK"
  def plotContour(self):
     spacing = 5.
     inset = .1
     self.rasterlayer=self.view.currentLayer()
     self.rldp = self.rasterlayer.dataProvider()
     crs = QgsCoordinateReferenceSystem()
     self.extentLayer = self.rasterlayer.extent()
     self.vector_lyr = QgsVectorLayer ('Point?crs:%s' %crs, 'grid', "memory")
     self.vpr = self.vector_lyr.dataProvider()
     self.qd = QVariant.Double
     self.vpr.addAttributes([QgsField ("id", QVariant.UInt), QgsField ("field values", self.qd)])
     self.vector_lyr.updateFields()
     self.xmin = self.extentLayer.xMinimum() + inset
     self.xmax = self.extentLayer.xMaximum()
     self.ymin = self.extentLayer.yMinimum() + inset
     self.ymax = self.extentLayer.yMaximum() - inset
     self.pts = [(x,y) for x in (i for i in np.arange (self.xmin, self.xmax, spacing)) for y in (j for j in np.arange (self.ymin, self.ymax, spacing))]
     self.feats= []
     print "Compute Features"
     for x, y in self.pts:
         self.f = QgsFeature(self.vector_lyr.pendingFields())
         self.p = QgsPoint (x,y)
         self.qry = self.rasterlayer.dataProvider().identify (self.p, QgsRaster.IdentifyFormatValue)
         self.r = self.qry.results()
         self.f.setAttribute (0, self.r[1])
         self.f.setGeometry (QgsGeometry.fromPoint(self.p))
         self.feats.append(self.f)
     self.vpr.addFeatures(self.feats)
     self.vector_lyr.updateExtents()
     QgsMapLayerRegistry.instance().addMapLayer(self.vector_lyr)
    # QgsVectorFileWriter.writeAsVectorFormat(self.vector_lyr, "C:\Users\dpeyrot\grid.shp", "grid", None, "ESRI Shapefile")
     #try :
     print "print ContourDialog"
     dlg = ContourDialog(self.vector_lyr,self.canvas)
     print "print ContourDialog ok"
#     dlg.show()
     dlg.exec_()
	 
  def  launchSvg2color(self):
    print "launch svg plugin"
    SVG2ColoRDialog()
  def plotcurrent(self):
      netcdf_datafile=str(self.filename)
      print 'Read filename %s  ' %(netcdf_datafile)
      # Read variable from netcdf 
      dim_val=self.cboDim.currentText()
      band=int(dim_val)
      u_varname='u'
      v_varname='v'
      ds_in = gdal.Open(netcdf_datafile)  
      metadata = ds_in.GetMetadata()  
      x_min = float(metadata['NC_GLOBAL#longitude_min'])
      x_max = float(metadata['NC_GLOBAL#longitude_max'])
      y_min = float(metadata['NC_GLOBAL#latitude_min'])
      y_max = float(metadata['NC_GLOBAL#latitude_max'])
      print x_min,x_max,y_min,y_max
      topleft_corner = (x_min, y_max)    
      u_raster_params, u_array = read_netcdf_variable(netcdf_datafile, str(u_varname),band)
      v_raster_params, v_array = read_netcdf_variable(netcdf_datafile, str(v_varname),band)
      u_y_pixels, u_x_pixels = u_array.shape # num of rows and columns, u array
      v_y_pixels, v_x_pixels = v_array.shape # num of rows and columns, v array
      assert u_y_pixels == v_y_pixels and u_x_pixels == v_x_pixels
      dx = x_max - x_min
      dy = y_max - y_min
      cellsize_long = dx / u_x_pixels
      cellsize_lat = dy / u_y_pixels
      cell_sizes = (cellsize_long, cellsize_lat)
      # create velocity vector field
      nc=netCDF4.Dataset(self.filename,'r')
      u_array_2=nc.variables['u'][0,band,:,:]
      v_array_2=nc.variables['v'][0,band,:,:]
      vector_array = np.ma.zeros((u_raster_params.get_rows(), u_raster_params.get_cols(), 2))
      vector_array[:,:,:]=np.nan
      print vector_array.shape
      print u_array_2.shape
      print v_array_2.shape
     # vector_array[:,:,0], vector_array[:,:,1] = u_array, v_array
      vector_array[:,:,0], vector_array[:,:,1] = np.flipud(u_array_2), np.flipud(v_array_2)
      #vector_array[:,:,0]=u_array[:,:],
      #vector_array[:,:,1]= v_array[:,:]
      vector_field = Grid(u_raster_params, vector_array)  
      magnitude_field_array = vector_field.magnitude().get_grid_data()
      orientation_field_array = vector_field.orientations().get_grid_data()
      #filepath="C:/Users/Charly/Documents/DEV/pyqgis/"
      filepath="/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/tmp/"
      magnitude_filename='magnitude_'+str(band)+'.tiff'
      filename=filepath+magnitude_filename
      print "Write array to raster %s" %(filename)
      array_to_raster(magnitude_field_array, cell_sizes, topleft_corner,filepath+magnitude_filename)
      orientation_filename='orientation_'+str(band)+'.tiff'
      filename=filepath+orientation_filename
      print "Write array to raster %s" %(filename)
      array_to_raster(orientation_field_array, cell_sizes, topleft_corner,filepath+orientation_filename)
      
      ## Create raster layer for magnitude and orientation 
      spacing = .1
      spacing = .25
      spacing = 1
      inset = .05
  #    raster_lyr_magn=QgsRasterLayer(filepath+magnitude_filename,"magnitude_band_"+str(band))
      raster_lyr_magn=QgsRasterLayer(filepath+magnitude_filename,"magnitude")
      raster_lyr_magn.isValid()
      #raster_lyr_orient=QgsRasterLayer(filepath+orientation_filename,"orientation_"+str(band))
      raster_lyr_orient=QgsRasterLayer(filepath+orientation_filename,"orientation")
      raster_lyr_orient.isValid()
      rprm = raster_lyr_magn.dataProvider()
      crs = QgsCoordinateReferenceSystem()
      ext_magn = raster_lyr_magn.extent()
      rpro = raster_lyr_orient.dataProvider()
      crs = QgsCoordinateReferenceSystem()
      ext_orient = raster_lyr_orient.extent()
      print "Defining raster layer ok %s" %(crs)
      ## Add Grid layer 
      vector_lyr = QgsVectorLayer ('Point?crs:%s' % crs, 'Grid', "memory")
      vpr = vector_lyr.dataProvider()
      qd = QVariant.Double
      # Create Attributes fields
      vpr.addAttributes([QgsField ("id", QVariant.UInt), QgsField ("orientation", qd), QgsField("magnitude", qd)])
      vector_lyr.updateFields()
      xmin_orient = ext_orient.xMinimum() + inset
      xmax_orient = ext_orient.xMaximum()
      ymin_orient = ext_orient.yMinimum() + inset
      ymax_orient = ext_orient.yMaximum() - inset
      feats= []
      QgsMapLayerRegistry.instance().addMapLayer(raster_lyr_magn)
      self.addLayer(raster_lyr_magn,band)
      print "Add layer 1"
      #QgsMapLayerRegistry.instance().addMapLayer(raster_lyr_orient)
      print "Add layer 2"
      #self.addLayer(raster_lyr_orient,band)
      pts = [(x,y) for x in (i for i in np.arange (xmin_orient, xmax_orient, spacing)) for y in (j for j in np.arange (ymin_orient, ymax_orient, spacing))]
      ## Creation of vectorfieldRenderer
      for x, y in pts:
          f = QgsFeature(vector_lyr.pendingFields())
          p = QgsPoint (x,y)
          qry_o = rpro.identify (p, QgsRaster.IdentifyFormatValue)
          qry_m = rprm.identify (p, QgsRaster.IdentifyFormatValue)
          r_o = qry_o.results()
          r_m = qry_m.results()
          f.setAttribute (0, r_o [1])
          f.setAttribute (1, r_m [1])
          f.setGeometry (QgsGeometry.fromPoint(p))
          feats.append(f)
      ## pass the point values to the data provider of points layer
      vpr.addFeatures(feats)
      ## Update layer extend 
      vector_lyr.updateExtents()
      ## Creation of vectorfieldRenderer
      r = VectorFieldRenderer.VectorFieldRenderer()
      # Set the mode for the renderer - possible values are
      # Cartesian (0), Polar (1), Height (2), or NoArrow (3).
      # And set the attributes defining the vector field
      r.setMode(r.Polar)
      r.setFields('magnitude','orientation')
      r.setDegrees(True)
      r.setAngleFromNorth(True)
      # Get the arrow symbol and assign its colors
      # Units can be QgsSymbolV2.MapUnit or QgsSymbolV2.MM

      r.setOutputUnit(QgsSymbolV2.MapUnit)

      arrow = r.arrow()

      # Configure the base of the arrow
      arrow.setBaseSize(0)
      arrow.setBaseBorderWidth(0)
      arrow.setBaseFillColor(QColor.fromRgb(255,0,0))
      arrow.setBaseBorderColor(QColor.fromRgb(0,0,0))
      arrow.setFillBase(True)

      # Configure the arrow - setColor applies to the shaft and outline of the arrow head.
      arrow.setColor(QColor.fromRgb(255,0,0))
      arrow.setShaftWidth(0.7)
      arrow.setRelativeHeadSize(0.3)
      arrow.setMaxHeadSize(3.0)
      arrow.setHeadShape(0.0,-1.0,-0.7)
      arrow.setHeadWidth(0.0)
      arrow.setHeadFillColor(QColor.fromRgb(0,0,0))
      arrow.setFillHead(True)
      # Set other symbology properties

      r.setScale(2)
      r.setUseMapUnit(False)

      r.setScaleGroup('def')
      r.setScaleGroupFactor(0.1)

      r.setScaleGroup('deformation')
      r.setLegendText(' horizontal')
      r.setScaleBoxText(' hor (95% conf lim)')
      r.setShowInScaleBox(True)
     # r.legendSymbologyItems(1.0)
      # Assign the renderer to the layer and refresh the symbology
      # Not sure whether clearing the image cache is necessary, should be 
      # done by QGis on setting the renderer
  
      vector_lyr.setRendererV2(r)
  
      # If the scale is to be automatically set based on the visible
      # vectors, then the following rather obscure code will do it.
      QgsMapLayerRegistry.instance().addMapLayer(vector_lyr)
      self.addLayer(vector_lyr,band)
      
  def read_netcdf_variable(netcdf_file, var_name):

    netcdf_file_var = gdal.Open('NETCDF:"' + netcdf_file + '":%s' % (var_name), GA_ReadOnly)
    if netcdf_file_var is None:
        raise IOError, 'Unable to open raster %s' %  (netcdf_file)

    # initialize DEM parameters
    raster_params = GDALParameters()

    # get driver type for current raster
    raster_params.set_driverShortName(netcdf_file_var.GetDriver().ShortName)

    # get current raster projection
    raster_params.set_projection(netcdf_file_var.GetProjection())

    # get row and column numbers
    raster_params.set_rows(netcdf_file_var.RasterYSize)
    raster_params.set_cols(netcdf_file_var.RasterXSize)

    # get and check number of raster bands - it must be one
    raster_bands = netcdf_file_var.RasterCount
    if raster_bands > 1:
        raise TypeError, 'More than one raster band in raster'
    # set critical grid values from geotransform array
    raster_params.set_topLeftX(netcdf_file_var.GetGeoTransform()[0])
    raster_params.set_pixSizeEW(netcdf_file_var.GetGeoTransform()[1])
    raster_params.set_rotationA(netcdf_file_var.GetGeoTransform()[2])
    raster_params.set_topLeftY(netcdf_file_var.GetGeoTransform()[3])
    raster_params.set_rotationB(netcdf_file_var.GetGeoTransform()[4])
    raster_params.set_pixSizeNS(netcdf_file_var.GetGeoTransform()[5])

    # get single band
    band = netcdf_file_var.GetRasterBand(1)
    print 'band %s' %str(band)

    # get no data value for current band
    raster_params.set_noDataValue(band.GetNoDataValue())
    if raster_params.get_noDataValue() is None:
        raise IOError, 'Unable to get no data value from input raster. Try change input format\n(e.g., ESRI ascii grids generally work)'

    # read data from band
    grid_values = band.ReadAsArray(0,0,raster_params.get_cols(),raster_params.get_rows())
    if grid_values is None:
        raise IOError, 'Unable to read data from raster'

    # transform data into numpy array
    data = np.asarray(grid_values)

    # if nodatavalue exists, set null values to NaN in numpy array
    if raster_params.get_noDataValue() is not None:
        data = np.where(abs(data-raster_params.get_noDataValue())> 1e-05, data, np.NaN)

    return raster_params, data

          
       
       
  def addGeojson(self):
      fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                   self.tr("Geojson (*geojson)"));
      if fileName is not None:
         self.updateFileVector(fileName)
         self.GroupBoxPal.setEnabled(True)

  def addVector(self):
     fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                   self.tr("Shapes Files (*)"));
     if fileName is not None:
            ## Find dimensions and variables
            #self.ui.leFileName.setText( fileName )
            self.updateFileVector(fileName)
            #self.combocolor.setEnable(True)
            self.GroupBoxPal.setEnabled(True) 

  def addRaster(self):
     fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                   self.tr("netCDF Files (*.nc *.cdf *.nc2 *.nc4)"));
     if fileName is not None:
            ## Find dimensions and variables
            #self.ui.leFileName.setText( fileName )
            self.updateFile(fileName)
            #self.combocolor.setEnable(True)
            self.GroupBoxPal.setEnabled(True) 
  def updateFileVector(self,name):
    #  if self.canvas.activeLayer() :
    #    layer1=self.canvas.activeLayer()
      self.layer2=QgsVectorLayer(name,os.path.basename(str(name)),"ogr")
      self.layer2.setLayerTransparency(50)
      QgsMapLayerRegistry.instance().addMapLayers([self.layer2])
      ## Set active layer to previous layer to use redrawing function
      # Set up the map canvas layer set
      self.layers.append( QgsMapCanvasLayer(self.layer2) )
    # # self.canvas.setLayerSet(self.layers)
      self.canvas.setExtent(self.layer2.extent())


#  def updateFileVector(self,name):
#        self.type=type
#        self.name = name
#        self.layer1 =  QgsVectorLayer(self.type, self.name , "memory")
#        self.pr =self.layer.dataProvider() 
#        QgsMapLayerRegistry.instance().addMapLayers([self.layer1])
#        ## Create list of layers
#        # QList <QgsMapCanvasLayer> 
#        myLayerSet=[]
#        self.layer1.setLayerTransparency(80)
#        cl1=QgsMapCanvasLayer(self.layer1)
#        myLayerSet.append(cl1)
#        # set extent to the extent of our layer
#        #self.canvas.setExtent(self.layer.extent())
#        self.canvas.enableAntiAliasing(True)    
#        self.canvas.freeze(False)
#        # set the map canvas layer set
#        self.canvas.setLayerSet(myLayerSet)
#        ## Refreshing canvas
#        self.canvas.refresh()
#        self.canvas.update()
#
  def updateFile(self,fileName):
        if fileName == '':
            return
        ll_speedu=False
        ll_speedv=False
        self.filename=fileName
        self.prefix = ''
        self.variables = []
        self.dim_values = dict()
	#self.variables = None
        self.dim_names = []
        self.dim_def = dict()                                                                                                                
        self.dim_band = dict()
        gdal.PushErrorHandler('CPLQuietErrorHandler')
        ds = gdal.Open(fileName)
        gdal.PopErrorHandler()
        if ds is None:
            return
        md = ds.GetMetadata("SUBDATASETS")
        for key in sorted(md.iterkeys()):
            if re.match('^SUBDATASET_[0-9]+_NAME$', key) is None:
                continue
            m = re.search('^(NETCDF:".+"):(.+)', md[key])
            if m is None:
                continue
            self.prefix = m.group(1)
            self.variables.append(m.group(2))
            if (str(m.group(2))) == 'u' :
                ll_speedu=True
            if (str(m.group(2))) == 'v' :
                ll_speedv=True
            
        if debug>0:
            print('prefix: '+str(self.prefix))
            print('variables: '+str(self.variables))
        self.cboVars.blockSignals(True)
        self.cboVars.clear()
        for var in self.variables:
            print('variables: %s'%(var))
            self.cboVars.addItem( var )
       # self.updateVariable()
        self.cboVars.blockSignals(False)

        if debug>0:
            print('done updateFile '+fileName)
	## Update dimension
        variable=self.cboVars.currentText()
        nc=netCDF4.Dataset(fileName,'r')
        if debug>0: 
          print 'OK1 var %s ' %(variable) 
        dim_var=nc.variables[variable].dimensions
        dim_len=nc.variables[variable].shape
        i=0
        if debug>0: 
          print 'OK2' 
          print dim_var
        for dim in dim_var :
            print 'dim %s' %(dim) 
            self.dim_values[ dim ] = []
            self.dim_def[ dim ] = []
            self.dim_values[ dim ].append(i)
            self.dim_def[ dim ].append(dim_len[i])
            self.dim_names.append(dim)
            i=i+1
        dim_names = self.dim_names
        dim_def=self.dim_def
        self.dim_names=[]
        for dim in dim_names:
            print 'dim %s ' %(dim)
            print dim_def[dim][0]
            #if dim_def[dim][0] <= 1 or dim /= 'depth' or dim /= 'deptht' :
            if dim == 'depth'  or dim == 'deptht': 
               self.dim_names.append(dim)
               print 'dim ok %s ' %(dim)
            elif dim == 'time_counter' and dim_def[dim][0] > 1 : 
               self.dim_names.append(dim)
            else:
        #       .or. dim .ne. 'z' :
               del self.dim_values[dim]
               del self.dim_def[dim]
        if debug>0:
            print(str(self.dim_names))

        if len(self.dim_names) > 1:
	    self.cboDim.setEnabled(True)
	    def_var=self.dim_def[dim]
            dim = self.dim_names[1]
            #self.cboDim.addItem("Dim")
            ## Update dimension values
            self.compose=0
            for value in range(0,def_var[1]): 
               self.cboDim.addItem(str(value))
        else :
            self.cboDim.setEnabled(False)
        if ll_speedu and ll_speedv : 
            self.actionPlotCurrent.setEnabled(True)
          

  def updateVariable(self):
        self.dim_names = []
        self.dim_values = dict()
        self.dim_def = dict()
        self.dim_band = dict()
        #self.clear()

	## Update dimension
        variable=self.cboVars.currentText()
        nc=netCDF4.Dataset(self.filename,'r')
        if debug>0: 
          print 'Update variable var %s ' %(variable) 
        if variable : 
            dim_var=nc.variables[str(variable)].dimensions
            dim_len=nc.variables[str(variable)].shape
        else :
            dim_var=""
            dim_len=""
        i=0
        if debug>0: 
          print 'OK2' 
        if dim_var :
          for dim in dim_var :
            self.dim_values[ dim ] = []
            self.dim_def[ dim ] = []
            self.dim_values[ dim ].append(i)
            self.dim_def[ dim ].append(dim_len[i])
            self.dim_names.append(dim)
            i=i+1
        dim_names = self.dim_names
        dim_def=self.dim_def
        self.dim_names=[]
        for dim in dim_names:
            #print 'dim %s ' %(dim)
            #if dim_def[dim][0] <= 1 or dim /= 'depth' or dim /= 'deptht' :
            if dim == 'depth'  or dim == 'deptht': 
               self.dim_names.append(dim)
               def_var=self.dim_def[dim]
            elif dim == 'time_counter' and dim_def[dim][0] > 1 : 
               self.dim_names.append(dim)
            else:
               del self.dim_values[dim]
               del self.dim_def[dim]

	if len(self.dim_names) > 0:
            dim = self.dim_names[0]
            def_var=self.dim_def[dim]
            self.cboDim.setEnabled(True)
            ## Update dimension values
            for value in range(0,def_var[0]): 
               self.compose=0
               self.cboDim.addItem(str(value+1))
            dim_val=self.cboDim.currentText()
	    self.compose_layer(self.filename,variable,dim_val)
	elif len(self.dim_names) == 2:
	   print 'passe la 2 dimensions'
	   self.addLayerMulti(self.filename,variable,dim_val)
	else: 
            print 'passe la'
            self.compose=0
            self.cboDim.addItem(str(1))
            self.cboDim.setEnabled(False)
	    self.compose_layer(self.filename,variable,1)
        
        
  def updatebasemap(self):
        print "inside basemap"
        menu = MyMenu()
        item1="map 50m"
        self.basemap.addItem(item1)
        action = QAction(str(item1),menu)
        action.setCheckable(True)
        #action.setEnable(False)
        action.setChecked(False)
        menu.addAction(action)                
        item2="map 110m"
        self.basemap.addItem(item2)
        action = QAction(str(item2),menu)
        action.setCheckable(True)
        #action.setChecked(False)
        menu.addAction(action)                
        self.basemap2.setMenu(menu)
        #if len(menu.actions()) > 1:
        #        menu.actions()[1].setChecked(True)
        self.basemap2.setEnabled(True)
        QObject.connect(self.basemap2.menu(), SIGNAL("triggered(QAction *)"), self.on_basemap_triggered)

  def redrawLayer(self):
        band=self.cboDim.currentText()
       # band=self.band
        if band : 
          layer=iface.activeLayer()
          self.addLayer(layer,band)
	else: 
	  print ("Band not defined")

  def on_basemap_triggered(self):
      # index = self.basemap.findText("Basemap", QtCore.Qt.MatchFixedString)
      # print index
      # if index >= 0:
      #     self.basemap.setCurrentIndex(index)
       print self.basemap.currentText()
       QtGui.QMessageBox.information(self,
            "INFORMATION:", "Functionality not implemented",
            QtGui.QMessageBox.Ok)
  
  def updateDims(self): 
        band=self.cboDim.currentText()
        var=self.cboVars.currentText()
        if self.compose == 1 : 
             self.compose_layer(str(self.filename),str(var),band)	

  def addLayerMulti(self,fileName,var,band):
        print('Multi dimensions')


  def compose_layer(self,fileName,var,band):
        if debug>0:
            print('addLayer(%s,%s,%s)' % (fileName,var,band))
        uri = 'NETCDF:"%s":%s' % (fileName, var)
        name = '%s_var=%s' % (fileName,var)
        namelayer=os.path.basename(name)
        print 'band %s'  %(band)
        if int(band) == 1 :
            name = '%s_band=%s' % (name, str(band))
        else:
            name = "%s_%s=%s" % (name,self.dim_names[0],str(band))
           # name = '%s_band=%s' % (name, str(band))
        print 'uri %s' %(uri)
        print 'Name raster %s' %(name)
	s = QSettings()
        self.rlayer = QgsRasterLayer( uri, namelayer )
        self.rlayer.setCrs( QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        QgsMapLayerRegistry.instance().addMapLayers([self.rlayer])
##        self.legend.addLayerToLegend(self.rlayer)
        self.addLayer(self.rlayer,band)	
        self.getvalue=PointTool(self.canvas,self.rlayer) # false = in
        self.getvalue.setAction(self.actionGetValue)           

	
  #def addLayer(self,fileName,var,band):
  def addLayer(self,layer,band):
        self.layer=layer
        if self.layer is None or not self.layer.isValid():
            print('Netcdf raster %s failed to load')
            return
        colorRamp=self.combocolor.currentColorRamp()	
        if colorRamp is None :
            print('Colorramp is none')
            pass
        if self.layer.type() == 1  :
            nb_classes=self.cboNbcolor.value()
            self.updatelayerwithpal(layer,colorRamp,int(nb_classes),band)
        else :
            print "Vector layer"
        #self.canvas.setExtent(self.layer.extent())
        self.canvas.enableAntiAliasing(True)    

        myLayerSet=[]
        cl1=QgsMapCanvasLayer(layer)
        myLayerSet.append(cl1)
        self.layers.append( QgsMapCanvasLayer(layer) )
        # set extent to the extent of our layer
        self.canvas.freeze(False)
        ##self.canvas.setLayerSet(self.layers)
        self.canvas.refresh()
        self.canvas.update()
        self.compose=1
        

  def updatelayerwithpal (self,layer,colorRamp,nb_values,band) :
    if layer.isValid() :
        myRasterShader = QgsRasterShader()
        myColorRamp = QgsColorRampShader()
        renderer = layer.renderer()
        provider = layer.dataProvider()
        band=int(band)
        if self.actionRescaling.isEnabled() : 
            ## Rescaling depending on zoom
            xmin = self.canvas.extent().xMinimum()
            xmax = self.canvas.extent().xMaximum()
            ymin = self.canvas.extent().yMinimum()
            ymax = self.canvas.extent().yMaximum()
            ## Get Statistics for min and max values
            myRasterBandStats=layer.dataProvider().bandStatistics(int(band),
                                             QgsRasterBandStats.Min | QgsRasterBandStats.Max,
                                             QgsRectangle(xmin,ymin,xmax,ymax))
            rastermin=myRasterBandStats.minimumValue
            rastermax=myRasterBandStats.maximumValue
        else :
            print "passe la actionRescaling no enable"
            myRasterBandStats=layer.dataProvider().bandStatistics(int(band),
                                          QgsRasterBandStats.Min | QgsRasterBandStats.Max)
            rastermin=myRasterBandStats.minimumValue
            rastermax=myRasterBandStats.maximumValue
        intervalDiff = ( rastermax - rastermin )/(nb_values-1);
        value=rastermin
        items=[]
        for class_val in range(0, nb_values):
            val=float(class_val)/float(nb_values)
            if self.invpal.isChecked():
                colour=colorRamp.color(1-val)
            else :
                colour=colorRamp.color(val)
            label = '%s' % (str(value))
            ramp_item = QgsColorRampShader.ColorRampItem(value, colour, label)
            items.append(ramp_item)
            value=value+intervalDiff
        print 'ok'
    
     # Create Raster Shader
        raster_shader = QgsRasterShader()
        color_ramp_shader = QgsColorRampShader() 
        color_ramp_shader.setColorRampType(QgsColorRampShader.INTERPOLATED)
        color_ramp_shader.setColorRampItemList(items)
        raster_shader.setRasterShaderFunction(color_ramp_shader)
        layer.setDefaultContrastEnhancement()
        myPseudoRenderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(),int(band),raster_shader)                                                                 
        layer.setRenderer(myPseudoRenderer)
        layer.setCacheImage(None)
        layer.triggerRepaint()
        self.canvas.refresh()
        self.canvas.update()
    else :  
       print "layer is not valid"
       

  #def addLayer(self,fileName,var,band):
  def addLayer(self,layer,band):
        self.layer=layer
        if self.layer is None or not self.layer.isValid():
            print('Netcdf raster %s failed to load')
            return
        colorRamp=self.combocolor.currentColorRamp()	
        if colorRamp is None :
            print('Colorramp is none')
            pass
        if self.layer.type() == 1 :
           nb_classes=self.cboNbcolor.value()
           self.updatelayerwithpal(layer,colorRamp,int(nb_classes),band)
        self.canvas.setExtent(self.layer.extent())
        self.canvas.enableAntiAliasing(True)    

        myLayerSet=[]
        #Change properties for layer2
        # Change the color of the layer to gray
        #self.layer.setLayerTransparency(80)
        cl1=QgsMapCanvasLayer(layer)
        myLayerSet.append(cl1)
        self.layers.append( QgsMapCanvasLayer(layer) )
        # set extent to the extent of our layer
        self.canvas.setExtent(self.layer.extent())
        self.canvas.freeze(False)
#        self.canvas.setLayerSet(self.layers)
        self.canvas.refresh()
        self.canvas.update()
        self.compose=1
        

  def changeScale( self, scale ):
      #self.lblScale.setText( "Scale 1:" + formatNumber( scale ) )
      print ('scale ' %(scale))
      if scale is not None  :
         self.lblScale.setText( "Scale 1:" + formatNumber( scale ) )
#  def move_xy(self,event):
  def move_xy(self,p):
      x = p.x()
      y = p.y()
      #x = event.pos().x()
      #y = event.pos().y()
      extent = self.canvas.extent()
      width = round(extent.width() / self.canvas.mapUnitsPerPixel());
      height = round(extent.height() / self.canvas.mapUnitsPerPixel());
      position=self.canvas.getCoordinateTransform().toMapCoordinates(x,y)
      print position
      if position is not None:
          ident = self.layer.dataProvider().identify(position, QgsRaster.IdentifyFormatValue,self.canvas.extent(), width, height ).results()
          iband=1
          if not ident or not ident.has_key( iband ): # should not happen
             bandvalue = "?"
          else:
             bandvalue = ident[iband]
             if bandvalue is None:
                bandvalue = "no data"
      self.valueXY.setText(str(bandvalue))
     #if p.x() is None and p.y()  is None :
  
  def updateXY( self, p ):
      x = p.x()
      y = p.y()
      self.lblXY.setText(" x: " + str(x) + " y: " + str(y) )
##      extent = self.canvas.extent()
##      width = round(extent.width() / self.canvas.mapUnitsPerPixel());
##      height = round(extent.height() / self.canvas.mapUnitsPerPixel());
##      position=self.canvas.getCoordinateTransform().toMapCoordinates(x,y)
##      print "---width height ---"
##      print position
##
##      if position is not None:
##          ident = self.layer.dataProvider().identify(position, QgsRaster.IdentifyFormatValue,self.canvas.extent(), width, height ).results()
##          iband=1
##          if not ident or not ident.has_key( iband ): # should not happen
##             bandvalue = "?"
##          else:
##             bandvalue = ident[iband]
##             if bandvalue is None:
##                bandvalue = "no data"
##      self.valueXY.setText(str(bandvalue))
     #if p.x() is None and p.y()  is None :
     #   return
     #else :
     #   if self.canvas.mapUnits() == 2: # Degrees
     #       self.lblXY.setText( formatToDegrees( p.x() ) + " | " \
     #        + formatToDegrees( p.y() ) )
     #   else: # Unidad lineal
     #       self.lblXY.setText( formatNumber( p.x() ) + " | " \
     #        + formatNumber( p.y() ) + "" )
    # else :
    #    str_x="0"
    #    str_y="0"
    #    self.lblXY.setText( str_x+ " | " \
    #                      + str_y + "" )

  def loadLayer( self, dictOpts ):
  	print 'I: Loading the layer...'
  	self.layerSRID = dictOpts[ 'srid' ] # To access the SRID when querying layer properties
  
  	if not self.isActiveWindow():
  		self.activateWindow()			 
  		self.raise_() 
  
  	if dictOpts['type'] == 'vector':
  		# QGIS connection
  		uri = QgsDataSourceURI()
  		uri.setConnection( dictOpts['-h'], dictOpts['-p'], dictOpts['-d'], dictOpts['-U'], dictOpts['-W'] )
  		uri.setDataSource( dictOpts['-s'], dictOpts['-t'], dictOpts['-g'] )
  		layer = QgsVectorLayer( uri.uri(), dictOpts['-s'] + '.' + dictOpts['-t'], "postgres" )		  
  	elif dictOpts['type'] == 'raster':
  		connString = "PG: dbname=%s host=%s user=%s password=%s port=%s schema=%s table=%s" % ( dictOpts['-d'], dictOpts['-h'], dictOpts['-U'], dictOpts['-W'], dictOpts['-p'], dictOpts['-s'], dictOpts['-t'] )
  		layer = QgsRasterLayer( connString, dictOpts['-s'] + '.' + dictOpts['-t'] )
  		layer.setNoDataValue( -32768 )
  		layer.rasterTransparency().initializeTransparentPixelList( -32768 )
  
  	if layer.isValid():
  		if self.canvas.layerCount() == 0:
  			self.canvas.setExtent( layer.extent() )
  
  			if dictOpts[ 'srid' ] != '-1':
  				print 'I: Map SRS (EPSG): %s' % dictOpts[ 'srid' ]
  				self.canvas.setMapUnits( layer.srs().mapUnits() )
  			else:
  				print 'I: Unknown Reference System'
  				self.canvas.setMapUnits( 0 ) # 0: QGis.Meters

		QgsMapLayerRegistry.instance().addMapLayer( layer )					   

  def getLayerProperties( self, l ):
		self.layerSRID = ''
		""" Create a layer-properties string (l:layer)"""
		print 'I: Generating layer properties...'
		if l.type() == 0: # Vector
			wkbType = ["WKBUnknown","WKBPoint","WKBLineString","WKBPolygon",
					   "WKBMultiPoint","WKBMultiLineString","WKBMultiPolygon",
					   "WKBNoGeometry","WKBPoint25D","WKBLineString25D","WKBPolygon25D",
					   "WKBMultiPoint25D","WKBMultiLineString25D","WKBMultiPolygon25D"]
			properties = "Source: %s\n" \
						 "Geometry type: %s\n" \
						 "Number of features: %s\n" \
						 "Number of fields: %s\n" \
						 "SRS (EPSG): %s\n" \
						 "Extent: %s " \
						  % ( l.source(), wkbType[l.wkbType()], l.featureCount(), 
							  l.dataProvider().fieldCount(), self.layerSRID, 
							  l.extent().toString() )
		elif l.type() == 1: # Raster
			rType = [ "GrayOrUndefined (single band)", "Palette (single band)", "Multiband" ]
			properties = "Source: %s\n" \
						 "Raster type: %s\n" \
						 "Width-Height (pixels): %sx%s\n" \
						 "Bands: %s\n" \
						 "Extent: %s" \
						 % ( l.source(), rType[l.rasterType()], l.width(), l.height(),
							 l.bandCount(), l.extent().toString() )
							# l.bandCount(), self.layerSRID, l.extent().toString() )
						 #"SRS (EPSG): %s\n" \
		return properties

  def createLegendWidget( self ):
     """ Create the map legend widget and associate to the canvas """
     print "createLegendWidget"
     self.legend = Legend( self )
     self.legend.setCanvas( self.canvas )
     self.legend.setObjectName( "theMapLegend" )
     self.LegendDock = QDockWidget( "Layers", self )
     self.LegendDock.setObjectName( "legend" )
     self.LegendDock.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
     self.LegendDock.setWidget( self.legend )
     self.LegendDock.setContentsMargins ( 0, 0, 0, 0 )
     #self.addDockWidget( Qt.BottomDockWidgetArea, self.LegendDock ) 
     self.addDockWidget( Qt.LeftDockWidgetArea, self.LegendDock ) 
     if iface.activeLayer() :
       self.layer=iface.activeLayer()
       self.legend.addLayerToLegend(self.layer)

  ##  Colorbar Legend widget
  def addLegendtoLayer(self):
       self.root = QgsProject.instance().layerTreeRoot()
       self.bridge = QgsLayerTreeMapCanvasBridge(self.root, self.canvas)
       self.model = QgsLayerTreeModel(self.root)
       self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
       self.model.setFlag(QgsLayerTreeModel.AllowNodeRename)
       self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
       self.model.setFlag(QgsLayerTreeModel.ShowLegend)
       self.view = QgsLayerTreeView()
       self.view.setModel(self.model)
       self.LegendDock = QDockWidget( "Layers", self )
       self.LegendDock.setObjectName( "layers" )
       self.LegendDock.setAllowedAreas( Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea )
       self.LegendDock.setWidget( self.view )
       self.LegendDock.setContentsMargins ( 9, 9, 9, 9 )
       self.addDockWidget( Qt.LeftDockWidgetArea, self.LegendDock )
       provider=MyMenuProvider(self.view,self.layers,self.canvas)
       self.view.setMenuProvider(provider)
##
	   
  def actionComp(self):
	xmin,ymin,xmax,ymax = self.layer.extent().toRectF().getCoords()
	# create composition with composer map
	mapRenderer = iface.mapCanvas().mapRenderer()
	c = QgsComposition(mapRenderer)
	c.setPlotStyle(QgsComposition.Print)
	x, y = 0, 0
	w, h = c.paperWidth(), c.paperHeight()
	composerMap = QgsComposerMap(c, x ,y, w, h)
	c.addItem(composerMap)
        # Label
        composerLabel = QgsComposerLabel(c)
	composerLabel.setText("Hello world")
	composerLabel.adjustSizeToText()
	c.addItem(composerLabel)
        # Legend
	legend = QgsComposerLegend(c)
	legend.model().setLayerSet(mapRenderer.layerSet())
	c.addItem(legend)
        # Scale bar 
	item = QgsComposerScaleBar(c)
	item.setStyle('Numeric') # optionally modify the style
	item.setComposerMap(composerMap)
	item.applyDefaultSize()
	c.addItem(item)
	# set label 1cm from the top and 2cm from the left of the page
	composerLabel.setItemPosition(20, 10)
	# set both label's position and size (width 10cm, height 3cm)
	composerLabel.setItemPosition(20, 10, 100, 30)
	#composerLabel.setFrame(False)
	dpi = c.printResolution()
	dpmm = dpi / 25.4
	width = int(dpmm * c.paperWidth())
	height = int(dpmm * c.paperHeight())
	c.setPaperSize(width, height)
	c.setPrintResolution(dpi)
	# create output image and initialize it
	image = QImage(QSize(width, height), QImage.Format_ARGB32)
	image.setDotsPerMeterX(dpmm * 1000)
	image.setDotsPerMeterY(dpmm * 1000)
	image.fill(0)
	#render the composition
	imagePainter = QPainter(image)
	sourceArea = QRectF(0, 0, c.paperWidth(), c.paperHeight())
	targetArea = QRectF(0, 0, width, height)
	c.render(imagePainter, targetArea, sourceArea)
	imagePainter.end()
	image.save("C:\Users\Charly\Documents\DEV\pyqgis\images\test.png", "png")
    
  def plot_grid2(self): 
    print "plot grid2"
    print "processing"
    xmin = self.canvas.extent().xMinimum()
    xmax = self.canvas.extent().xMaximum()
    ymin = self.canvas.extent().yMinimum()
    ymax = self.canvas.extent().yMaximum()

    #xmin,ymin,xmax,ymax = self.view.currentLayer().extent().toRectF().getCoords()
    #xmin=-180
    #ymin=-90
    #xmax=180
    #ymax =90 
    gridWidth = 10
    gridHeight = 10
    rows = ceil((ymax-ymin)/gridHeight)
    cols = ceil((xmax-xmin)/gridWidth)
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight
    pol = Crea_layer("grid", "Polygon")
    for i in range(int(cols)):
        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        for j in range(int(rows)):
            poly = [QgsPoint(ringXleftOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYtop)] 
            pol.create_poly(poly) 
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth

    pol.disp_layer    
##    input = processing.getobject(layer.name())
##    centerx = (input.extent().xMinimum() + input.extent().xMaximum()) / 2
##    centery = (input.extent().yMinimum() + input.extent().yMaximum()) / 2
##    width = (input.extent().xMaximum() - input.extent().xMinimum())
##    height = (input.extent().yMaximum() - input.extent().yMinimum())
#    cellsize = 10
#    centerx = 0
#    centery = 0
#    width = 360
#    height = 180
#    path_res = "C:/Users/Charly/Documents/DEV/pyqgis/Shapefiles/"
#    grid=path_res+"grid.shp"
#
#    result=processing.runandload("qgis:creategrid", cellsize, cellsize, width, height, centerx, centery, 1, "epsg:4326", grid)
#    #result = processing.runalg("qgis:creategrid", 1, 360, 180, 10, 10, 0, 0, "epsg:4326", None)
#    print "processing"
##    path_res = "C:/Users/Charly/Documents/DEV/pyqgis/"
##    os.chdir(path_dir + "Shapefiles"+"/")
##    for fname in glob.glob("*.shp"):        
##        outputs_2=general.runalg("qgis:clip", outputs_1['SAVENAME'], fname, path_res  + "/"+ fname)
##        
#
##print "result ok"
##    print type(result)
#    gridLayer = iface.addVectorLayer(result.get("OUTPUT"),"grid","ogr")
#
#Add it to the canvas
##    gridLayer = self.canvas.addVectorLayer(result.get("OUTPUT"),"grid","ogr")
# create composition with composer map
#    self.mMapSettings= QgsMapSettings()
#    crs=QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)  
#    self.mMapSettings.setDestinationCrs( crs )
#    self.mMapSettings.setCrsTransformEnabled(False)
#    self.mComposition = QgsComposition(self.mMapSettings)
#    self.mComposition.setPaperSize(297, 210)
#    self.mComposerMap = QgsComposerMap(self.mComposition, 20, 20, 200, 100)
#    self.mComposerMap.setFrameEnabled(True)
#    self.mComposerMap.setBackgroundColor( QColor(Qt.white) )
#    self.mComposerMap.storeCurrentLayerSet()
#    self.mComposerMap.setKeepLayerSet(True)
#    self.mComposition.addComposerMap(self.mComposerMap)
#    print "OK1"
  
#    myRectangle = QgsRectangle(781662.375, 3339523.125,793062.375, 3345223.125)
#    #myRectangle = QgsRectangle(xmin,xmax,ymin,ymax)
#    self.mComposerMap.setNewExtent(myRectangle)
#    self.mComposerMap.grid().setEnabled( True )
#    self.mComposerMap.grid().setIntervalX( 2 )
#    self.mComposerMap.grid().setIntervalY( 2 )
#    self.mComposerMap.grid().setAnnotationEnabled( True )
#    self.mComposerMap.grid().setGridLineColor( QColor( 0, 255, 0 ) )
#    self.mComposerMap.grid().setGridLineWidth( 0.5 )
#    self.mComposerMap.grid().setAnnotationFont( QgsFontUtils.getStandardTestFont() )
#    self.mComposerMap.grid().setAnnotationPrecision( 0 )
#    self.mComposerMap.grid().setAnnotationPosition( QgsComposerMapGrid.Disabled, QgsComposerMapGrid.Left )
#    self.mComposerMap.grid().setAnnotationPosition( QgsComposerMapGrid.OutsideMapFrame, QgsComposerMapGrid.Right )
#    self.mComposerMap.grid().setAnnotationPosition( QgsComposerMapGrid.Disabled, QgsComposerMapGrid.Top )
#    self.mComposerMap.grid().setAnnotationPosition( QgsComposerMapGrid.OutsideMapFrame, QgsComposerMapGrid.Bottom )
#    self.mComposerMap.grid().setAnnotationDirection( QgsComposerMapGrid.Horizontal, QgsComposerMapGrid.Right )
#    self.mComposerMap.grid().setAnnotationDirection( QgsComposerMapGrid.Horizontal, QgsComposerMapGrid.Bottom )
#    self.mComposerMap.grid().setAnnotationFontColor( QColor( 255, 0, 0, 150 ) )
#    self.mComposerMap.grid().setBlendMode( QPainter.CompositionMode_Overlay )
#    checker = QgsCompositionChecker('composermap_grid', self.mComposition)
#    myTestResult, myMessage = checker.testComposition()
#    self.mComposerMap.setGridEnabled(False)
#    self.mComposerMap.setShowGridAnnotation(False)
#    print "OK2"
#    assert myTestResult == True, myMessage
  def plot_grid(self): 
    # first layer
    xmin,ymin,xmax,ymax = self.view.layer.extent().toRectF().getCoords()
    print xmin,ymin,xmax,ymax
    gridWidth = 5
    gridHeight = 5
    rows = ceil((ymax-ymin)/gridHeight)
    cols = ceil((xmax-xmin)/gridWidth)
    print 'row, col :'
    print rows,cols
    ringXleftOrigin = xmin
    ringXrightOrigin = xmin + gridWidth
    ringYtopOrigin = ymax
    ringYbottomOrigin = ymax-gridHeight
    pol = Create_gridlayer("grid", "Polygon",self.canvas,self.layer)
    for i in range(int(cols)):
        # reset envelope for rows
        ringYtop = ringYtopOrigin
        ringYbottom =ringYbottomOrigin
        for j in range(int(rows)):
            poly = [QgsPoint(ringXleftOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYtop),QgsPoint(ringXrightOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYbottom),QgsPoint(ringXleftOrigin, ringYtop)] 
            pol.create_poly(poly) 
            ringYtop = ringYtop - gridHeight
            ringYbottom = ringYbottom - gridHeight
        ringXleftOrigin = ringXleftOrigin + gridWidth
        ringXrightOrigin = ringXrightOrigin + gridWidth
    pol.disp_layer

  def getValue(self):                                                                                                                                 
      print 'Do getvalue'
      self.canvas.setMapTool(self.getvalue)
      result=1

  def actionMenu2(self): 
      ## Get current colormap
      #colorRamp=self.combocolor.currentColorRamp().invertedColorRamp() 	
      print "do actionMenu2"
      print "band "
      self.layer=self.view.currentLayer()
      typelayer = self.layer.type()
      print "layer type : %i " %(typelayer) 
      if typelayer == 1 : # Raster
#      self.layer=iface.activeLayer()
         colorRamp=self.combocolor.currentColorRamp()      
         nb_classes=self.cboNbcolor.value()
         dim_val=self.cboDim.currentText()
         self.updatelayerwithpal(self.layer,colorRamp,int(nb_classes),dim_val)

  def zoomIn(self):
    print 'Do zoomIn'
#    self.actionZoomIn.setCheckable(True)
#.select(layer.dataProvider().attributeIndexes(), QgsRectangle(), False)
    self.canvas.setMapTool(self.toolZoomIn)
    self.actionRescaling.setEnabled(True)
  def zoomOut(self):
    self.canvas.setMapTool(self.toolZoomOut)
  def zoomFull(self):
    self.canvas.zoomToFullExtent()
    self.actionRescaling.setEnabled(False)
    self.actionMenu2()
  def pan(self):
    self.canvas.setMapTool(self.toolPan)
  def saveMap(self):
     # create image
     self.canvas.saveAsImage("/home/cregnier/DEV/Python/pyqgis/render.png", QPixmap(800, 600), "PNG")
     #img = QImage(QSize(800, 600), QImage.Format_ARGB32_Premultiplied)
     ## set image's background color
     #color = QColor(255, 255, 255)
     #img.fill(color.rgb())
     ## create painter
     #p = QPainter()
     #p.begin(img)
     #p.setRenderHint(QPainter.Antialiasing)
     #render = QgsMapRenderer()
     ## set layer set
     #lst = [self.layer.id()]  # add ID of every layer
     #render.setLayerSet(lst)
     ## set extent
     #rect = QgsRect(render.fullExtent())
     #rect.scale(1.1)
     #render.setExtent(rect)
     ## set output size
     #render.setOutputSize(img.size(), img.logicalDpiX())
     ## do the rendering
     #render.render(p)
     #p.end()
     ## save image
     #img.save("/home/cregnier/DEV/Python/pyqgis/render.png","png")
     #QtGui.QMessageBox.information(
     #   self,
     #   "INFORMATION:", "Functionality not implemented",
     #   QtGui.QMessageBox.Ok)


## Classes Netcdf to browse data
# this menu don't hide when items are clicked
# http://stackoverflow.com/questions/2050462/prevent-a-qmenu-from-closing-when-one-of-its-qaction-is-triggered
class MyMenu(QMenu):

    def __init__(self):
        QMenu.__init__(self)
        self.ignoreHide = False

    def setVisible(self,visible):
        if self.ignoreHide:
            self.ignoreHide = False
            return
        QWidget.setVisible(self,visible)

    def mouseReleaseEvent(self,event):
        action = self.actionAt(event.pos())
        if action is not None:
            #if (actions_with_showed_menu.contains (action))
            self.ignoreHide = True
        QMenu.mouseReleaseEvent(self,event)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

debug=1

class MyMenuProvider(QgsLayerTreeViewMenuProvider):
  def __init__(self, view,list_layers,canvas):
    QgsLayerTreeViewMenuProvider.__init__(self)
    print "Init MyMenuProvider"
    self.view = view
    self.canvas=canvas
    self.root = QgsProject.instance().layerTreeRoot()
    self.layers=list_layers
  def createContextMenu(self):
    imgs_dir=":/images/icons/"
    if not self.view.currentLayer():
      return None
    m = QMenu()
    #m.addSeparator()
    self.spinbox = QtGui.QSpinBox()
    self.spinbox.setMinimum(5)
    self.spinbox.setMaximum(100)
    imgs_dir="C:/Users/Charly/Documents/DEV/pyqgis/Charly_V0/icons/"
    m.addAction(QIcon(imgs_dir+"mIconAtlas.png"), "&Show Extent", self.showExtent) 
    m.addAction(QIcon(imgs_dir+"mActionZoomFullExtent.png"),"&Zoom to layer extent", self.zoomToLayer )
    m.addAction(QIcon(imgs_dir+"removeLayer.png"), "&Remove layer",self.removeCurrentLayer )
    m.addAction(QIcon(imgs_dir+"mActionRemoveAllFromOverview.png"),"&Remove all layers",self.removeAll )
    m.addAction(QIcon(imgs_dir+"mIconInfo.png"),"&Get properties",self.getLayerProperties )
    m.addAction(QIcon(imgs_dir+"mIconInfo.png"),"&Set Visibility",self.setLayerVisibility )
    return m

  def showExtent(self):
    r = self.view.currentLayer().extent()
    QMessageBox.information(None, "Extent", r.toString())
  def setLayerVisibility(self):
    qtw=QTabWidget()
    qtw.setWindowTitle("Test")
    print "OK1"
    wd=QWidget()
    print "OK2"
    lcd=QLCDNumber(wd)
    sld=QSlider(QtCore.Qt.Horizontal, wd)
    vbox = QVBoxLayout()
    print "OK3"
    vbox.addWidget(lcd)
    vbox.addWidget(sld)
    print "OK4"
    wd.setLayout(vbox)
    sld.valueChanged.connect(lcd.display)
    print "OK4"
    wd.setGeometry(50,50,30,30)
    print "OK5"
    qtw.addTab(wd,"First tab")
    qtw.show() 
    #self.view.currentLayer().renderer().setOpacity(0.5)
    # Trigger a repaint
    #if hasattr(self.view.currentLayer(), "setCacheImage"):
    #    self.view.currentLayer().setCacheImage(None)
    #self.view.currentLayer().triggerRepaint()
   # node = self.root.findLayer(self.view.currentLayer().id())
   # new_state = Qt.Checked if node.isVisible() == Qt.Unchecked else Qt.Unchecked
   # node.setVisible(new_state)
  def zoomToLayer(self):
    root = QgsProject.instance().layerTreeRoot()
    bridge = QgsLayerTreeMapCanvasBridge(root, self.canvas)
    self.canvas.zoomToFullExtent()
    self.canvas.show()
  def removeCurrentLayer(self):
    QgsMapLayerRegistry.instance().removeMapLayer( self.view.currentLayer().id())

  def removeAll( self ):
    """ Remove all legend items """
    for layer in self.layers: 
       QgsMapLayerRegistry.instance().removeMapLayer( layer.layer().id())

  def collapseAll( self ):
    """ Collapse all layer items in the legend """
    for i in range( self.topLevelItemCount() ):
       item = self.topLevelItem( i )
       self.collapseItem( item )
  def expandAll( self ):
    """ Expand all layer items in the legend """
    for i in range( self.topLevelItemCount() ):
        item = self.topLevelItem( i )
        self.expandItem( item )

  def getLayerProperties( self):
      l=self.view.currentLayer()
      typelayer = l.type()
      print "layer type : %i " %(typelayer) 
      if typelayer == 0: # Vector
              wkbType = ["WKBUnknown","WKBPoint","WKBLineString","WKBPolygon",
                                 "WKBMultiPoint","WKBMultiLineString","WKBMultiPolygon",
                                 "WKBNoGeometry","WKBPoint25D","WKBLineString25D","WKBPolygon25D",
                                 "WKBMultiPoint25D","WKBMultiLineString25D","WKBMultiPolygon25D"]
              properties = "Source: %s\n" \
                                       "Geometry type: %s\n" \
                                       "Number of features: %s\n" \
                                       "SRS (EPSG): %s\n" \
                                       "Extent: %s " \
                                        % ( l.source(), wkbType[l.wkbType()], l.featureCount(), 
                                                self.layerSRID, 
                                                l.extent().toString() )
      elif typelayer == 1: # Raster
	      print "Properties from raster Layer"
              rType = [ "GrayOrUndefined (single band)", "Palette (single band)", "Multiband" ]
              properties = "Source: %s\n" \
                                       "Raster type: %s\n" \
                                       "Width-Height (pixels): %sx%s\n" \
                                       "Bands: %s\n" \
                                       "Extent: %s" \
                                       % ( l.source(), rType[l.rasterType()], l.width(), l.height(),
                                               l.bandCount(), l.extent().toString() )
                                              # l.bandCount(), self.layerSRID, l.extent().toString() )
                                       #"SRS (EPSG): %s\n" \
      QMessageBox.information(None, "Properties", properties)



w =MyCanvas()
w.show()
