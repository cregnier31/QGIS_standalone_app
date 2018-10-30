# coding: utf8
from __future__ import unicode_literals
from qgis.core import *
from qgis.gui import *
from qgis.utils import iface
import qgis.utils
import os, sys,re,math
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style 
from  Class_section import Section
from ui_user_interface_dialogs import OlaParams 
from sytoolkit.sydate import SyDate
import cPickle
### Extension of a maptool object
class MapToolMixin:
    def setLayer(self, layer):
        self.layer = layer
    def transformCoordinates(self, screenPt):
        return (self.toMapCoordinates(screenPt),
        self.toLayerCoordinates(self.layer, screenPt))
    def calcTolerance(self, pos):
        pt1 = QPoint(pos.x(), pos.y())
        pt2 = QPoint(pos.x() + 10, pos.y())
        mapPt1,layerPt1 = self.transformCoordinates(pt1)
        mapPt2,layerPt2 = self.transformCoordinates(pt2)
        tolerance = layerPt2.x() - layerPt1.x()
        return tolerance 
    def findFeatureAt(self, pos, excludeFeature=None):
        mapPt,layerPt = self.transformCoordinates(pos)
        tolerance = self.calcTolerance(pos)
        searchRect = QgsRectangle(layerPt.x() - tolerance,
        layerPt.y() - tolerance,
        layerPt.x() + tolerance,
        layerPt.y() + tolerance)
        request = QgsFeatureRequest()
        request.setFilterRect(searchRect)
        request.setFlags(QgsFeatureRequest.ExactIntersect)
        for feature in self.layer.getFeatures(request):
            if excludeFeature != None:
                if feature.id() == excludeFeature.id():
                    continue
            return feature
        return None
        
    def findVertexAt(self, feature, pos):
        mapPt,layerPt = self.transformCoordinates(pos)
        tolerance     = self.calcTolerance(pos)
        vertexCoord,vertex,prevVertex,nextVertex,distSquared =\
        feature.geometry().closestVertex(layerPt)
        distance = math.sqrt(distSquared)
        if distance > tolerance:
            return None
        else:
            return vertex
    def clearMemoryLayer(self, layer):
        featureIDs = []
        provider = layer.dataProvider()
        for feature in provider.getFeatures(QgsFeatureRequest()):
            featureIDs.append(feature.id())
            provider.deleteFeatures(featureIDs) 
    def plot(self,prof,var_insitu,var_mod,label,time_label):
        style.use('ggplot')
        fig, ax = plt.subplots(figsize=(5, 7))
        #if ( max(depth) > 0 ) :
        ax.invert_yaxis()
        ax.plot(var_insitu,0-prof,label="Insitu_"+label,linewidth=2)
        ax.plot(var_mod,0-prof,label="Model_"+label, linewidth=2)
        offset = 0.01
        x1, x2 = ax.get_xlim()[0] - offset, ax.get_xlim()[1] + offset
        ax.set_xlim(x1, x2)
        ax.legend (loc=4)
        #ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
        #    ncol=2, mode="expand", borderaxespad=0.)
        title="OLA Profile in "+label+" for Day : "+time_label
        ax.set_title(title)
        ax.set_xlabel(label)
        ax.set_ylabel('depth')
        print "before show"
        fig.show()
        return
        print "after show"

    def timer_fired(self,item,timer):
        print "inside timer fired"
        item.setColor(QColor(128,128,128))
        #self.canvas.scene().removeItem(item)
        timer.stop()
        print 'end of timer_fired'

class Bar(QProgressBar):
    value=0
    def increaseValue(self):
        self.setValue(self.value)
        self.value=self.value+1

class ExploreTool(QgsMapToolIdentify,MapToolMixin):
    def __init__(self,canvas,ll_standalone,filename):
        QgsMapToolIdentify.__init__(self,canvas)
        self.setCursor(Qt.ArrowCursor)
        self.canvas = canvas
        self.ll_standalone=ll_standalone
        self.filename=filename
        #self.layer=layer
        print "Init ok"
    def canvasReleaseEvent(self, event):
        print "canvasReleaseEvent"
        found_features = self.identify(event.x(), event.y(),
        self.TopDownStopAtFirst,
        self.VectorLayer)
        if len(found_features) > 0:
           layer = found_features[0].mLayer
           print layer
           feature = found_features[0].mFeature
           geometry = feature.geometry()
           print geometry
           info = []
           name = feature.attribute("Value_id")
           if self.ll_standalone:
              name=name.toPyObject()
        if name != None: info.append("  uid : "+str(name))
        prof_id = feature.attribute("profile")
        if self.ll_standalone:
           prof_id=prof_id.toPyObject()
        if prof_id != None: info.append("  NB prof : "+str(prof_id))
        name_var = feature.attribute("name")
        misfit = feature.attribute("Misfit")
        print (type(misfit))
        misfit=misfit.toPyObject()
        print (type(misfit))

        time_var = feature.attribute("time")
        if name_var and time_var:
           if self.ll_standalone:
               name_var=name_var.toPyObject()
               time_var=time_var.toPyObject()
           time_var_sys=SyDate.fromjulian(int(time_var))
          # time_var=str(SyDate.__str__(dateval_sys))
           time_var=str(time_var_sys)
           info.append("Type prof : "+str(name_var) + ", Date =" + str(time_var))
       # timezone = feature.attribute("TIMEZONE")
       # if timezone != None:
       #    info.append("Timezone: " + timezone)
        longitude = geometry.asPoint().x()
        latitude = geometry.asPoint().y()
        ## Add a Vertex Marker
        #if self.m :
        #   self.canvas.scene().removeItem(self.m)
        self.m = QgsVertexMarker(self.canvas)
        self.m.setCenter(QgsPoint(longitude,latitude))
        self.m.setColor(QColor(255,0, 0))
        self.m.setIconSize(20)
        self.m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
        self.m.setPenWidth(2)
        print "OK Vertex"
        #print longitude,latitude,first_frcst_temp
        info.append("Lat/Long: %0.4f, %0.4f" % (latitude,longitude))
        info.append("Misfit: %6.4f" % (misfit))
        QMessageBox.information(self.canvas,"Feature Info","\n".join(info))
        ## Plot the profile
        Type_var=str(name_var[0:4])
        indice=int(prof_id)
        nc_file=netCDF4.Dataset(str(self.filename),'r')
        prof_VP=nc_file.variables['depth_'+Type_var][indice,:]
        insitu_var=nc_file.variables[Type_var][indice,:]
        echeance = os.path.basename(str(self.filename)).split('_')[3]
        if echeance == "ANA":
            variable = 'second_frcst_'+Type_var.lower()
        elif echeance == "FCST":
            variable = 'first_frcst_'+Type_var.lower()
        mod_var=nc_file.variables[variable][indice,:]
        self.plot(prof_VP,insitu_var,mod_var,Type_var,time_var)
        ## Add to registry
        QgsMapLayerRegistry.instance().addMapLayers([self.m])   
        print "init bar"
      ##  bar=Bar()
      ##  bar.resize(300,40)
      ##  bar.setWindowTitle('Working ...')
      ##  timer = QTimer()
      ##  print "connect"
      ##  timer.timeout.connect(bar.increaseValue)
      ##  bar.show()
      ##  print "show bar"

        #timer = QTimer()
        #timer.start(500)
        #timer.setSingleShot(True)
        #print "Print start timer"
        #timer.timeout.connect(self.timer_fired(self.m,timer))
class PointTool(QgsMapTool):   
    def __init__(self, canvas,layer,parent):
        print "inside PointTool"
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas    
        self.setCursor(Qt.ArrowCursor)
        self.layer=layer
        self.mainwindow=parent
    def canvasPressEvent(self, event):
        if event.buttons() == "Qt::LeftButton" :
               print self.canvas.getCoordinateTransform()
               pass
        if event.buttons() == "Qt::RightButton" :
             self.canvas.scene().removeItem(self.m) 

    def canvasMoveEvent(self,event):
        #print 'canvasMoveEvent'
        x = event.pos().x()
        y = event.pos().y()
        #QgsMapTool.activate(self)
        self.canvas.setCursor(Qt.ArrowCursor)
        self.emit( SIGNAL("moved"), QPoint(event.pos().x(), event.pos().y()) )
        # QMessageBox.information(None, "Coords values", " x: " + str(point.x()) + " Y: " + str(point.y()) )

    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        print x,y
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        extent = self.canvas.extent()
        width = round(extent.width() / self.canvas.mapUnitsPerPixel());
        height = round(extent.height() / self.canvas.mapUnitsPerPixel())
        print "--- Point tool release event ---"
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
                bandvalue = ident[iband].toPyObject()
                if bandvalue is None:
                    bandvalue = "no data"
        ## Plot profile 
        l=self.layer
        if not l :
            print "Layer not selected"
        else :
            fileName=l.source().split('"')[1]
            print "Filename %s " %(str(fileName))
            nc_file=netCDF4.Dataset(str(fileName),'r')
            x0= float(point.x())
            y0=float(point.y())
            print x0,y0
            m = QgsVertexMarker(self.canvas)
            m.setCenter(QgsPoint(x0, y0))
            m.setColor(QColor(0, 255, 0))
            m.setIconSize(5)
            m.setIconType(QgsVertexMarker.ICON_BOX) # or ICON_CROSS, ICON_X
            m.setPenWidth(3)
            print "variable"
            variable=str(self.mainwindow.cboVars.currentText())
            print "variable : %s" %(str(variable))
            lon = nc_file.variables['longitude'][:]
            lat = nc_file.variables['latitude'][:]
            self.prof=nc_file.variables['depth'][:]
            min_prof=np.nanmin(self.prof)
            max_prof=np.nanmax(self.prof)
            print "OK"
            profdialog=OlaParams(str(min_prof),str(max_prof))
            profdialog.show()
            if profdialog.exec_() == QDialog.Accepted:
                prof_min = float(profdialog.minprof_fieldgrid.text())
                prof_max = float(profdialog.minprof_fieldgrid.text())
                ##  get position
                ind_min=self.getnearpos(self.prof,prof_min)
                ind_max=self.getnearpos(self.prof,prof_max)
                self.prof=self.prof[ind_min:ind_max]
                #profondeur=profondeur[ind_min:ind_max]
                print "read lon lat ok"
                ## Find Nearest point in the grid
                xi,yi=self.lookupNearest(x0,y0,lon,lat)
                #print xi,yi,lon[xi],lat[yi]
                temps=0
                print xi,yi
                self.var=nc_file.variables[variable][temps,ind_min:ind_max,yi,xi]
                self.xlabel=variable
                self.title=variable+" Profile pos lon:"+str(x0)[0:5]+" lat:"+str(y0)[0:5]
                self.ylabel="Pressure [dbar]"
                self.label=variable[0:4]
                print "plot !!"
                self.plot()
                print "outside plot"
                timer = QTimer()
                print "Print connect timer"
                timer.timeout.connect(self.timer_fired(self.m,timer))
                print "Print start timer"
                timer.setSingleShot(True)
                timer.start(10000)
        ## Add message box to see coordinates
        print "Launch message info" 
        QMessageBox.information(None, "Clicked coords", " Lon: " + str(point.x()) + " Lat: " + str(point.y()) + "\n Value: " + str(bandvalue))

    def getnearpos(self,array,value):                                                                                                            
        idx = (np.abs(array-value)).argmin()
        return idx


    def plot(self):
       print ("Inside plot")
       style.use('ggplot')
       fig, ax = plt.subplots(figsize=(5, 7))
       #if ( max(depth) > 0 ) :
       ax.invert_yaxis()
       ax.plot(self.var, self.prof, label=self.label, linewidth=2)
       offset = 0.01
       x1, x2 = ax.get_xlim()[0] - offset, ax.get_xlim()[1] + offset
       ax.set_xlim(x1, x2)
       ax.legend (loc=4)
       #ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
       #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
       #    ncol=2, mode="expand", borderaxespad=0.)
       ax.set_title(self.title)
       ax.set_xlabel(self.xlabel)
       ax.set_ylabel(self.ylabel)
       fig.show()

    def lookupNearest(self,x0, y0,lon,lat):
       print "lookupNearest"
       xi = np.abs(lon-x0).argmin()
       yi = np.abs(lat-y0).argmin()
       return xi,yi

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

class SelectTool(QgsMapToolIdentify):
   def __init__(self, canvas):
      QgsMapToolIdentify.__init__(self, canvas)
      self.canvas = canvas
      self.setCursor(Qt.ArrowCursor)
   def canvasReleaseEvent(self, event):
      print "inside canvas"
      found_features = self.identify(event.x(), event.y(),
      self.TopDownStopAtFirst,
      self.VectorLayer)
      print "found features"
      print event.x(), event.y()

      if len(found_features) > 0:
         layer = found_features[0].mLayer
         print layer
         feature = found_features[0].mFeature
         print feature
         if event.modifiers() & Qt.ShiftModifier:
            layer.select(feature.id())
            print "select"
         else:
            layer.setSelectedFeatures([feature.id()])
      else:
         self.canvas.layer.removeSelection()

## Grid Layer Creation
class Crea_layer(object):
    def __init__(self,name,type):
        self.type=type
        self.name = name
        self.layer =  QgsVectorLayer(self.type, self.name , "memory")
        self.pr =self.layer.dataProvider()
        props = { 'color' : 'transparent', 'style' : 'no', 'style' : 'solid' }
        s = QgsFillSymbolV2.createSimple(props)
        self.layer.setRendererV2( QgsSingleSymbolRendererV2( s ) )
        self.layer.setLayerTransparency(50)
    def create_poly(self,points):
        self.seg = QgsFeature()
        self.seg.setGeometry(QgsGeometry.fromPolygon([points]))
        self.pr.addFeatures( [self.seg] )
        self.layer.updateExtents()
    @property
    def disp_layer(self):
        self.layer.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayers([self.layer])

class IdentifyGeometry(QgsMapToolIdentify):
 def __init__(self, canvas):
   self.canvas = canvas
   QgsMapToolIdentify.__init__(self, canvas)
 
 def canvasReleaseEvent(self, mouseEvent):
   results = self.identify(mouseEvent.x(),mouseEvent.y(), self.TopDownStopAtFirst, self.VectorLayer)
   if len(results) > 0:
     self.emit( SIGNAL( "geomIdentified" ), results[0].mLayer, results[0].mFeature)

#class MessageBar(QgsMessageBar):
#    def __init__(self, parent=None):
#        super(MessageBar, self).__init__(parent)
#        self.parent().installEventFilter(self)
#
#    def showEvent(self, event):
#        self.resize(QSize(self.parent().geometry().size().width(), self.height()))
#        self.move(0, self.parent().geometry().size().height() - self.height())
#        self.raise_()
#
#    def eventFilter(self, object, event):
#        if event.type() == QEvent.Resize:
#            self.showEvent(None)
#
#        return super(MessageBar, self).eventFilter(object, event)
#
class DistanceCalculator(QgsMapTool): 
     def __init__(self, canvas,parent):    
        self.canvas=canvas
        self.parent=parent
        QgsMapTool.__init__(self, canvas)
     def canvasPressEvent(self, event): 
         transform = self.canvas.getCoordinateTransform()
         print "CanvasPressEvent"
         self._startPt = transform.toMapCoordinates(event.pos().x(),event.pos().y())
         print self._startPt
     def canvasReleaseEvent(self, event):
          transform = self.canvas.getCoordinateTransform()
          print "CanvasReleaseEvent"
          endPt = transform.toMapCoordinates(event.pos().x(),event.pos().y())
          print endPt
          crs = self.canvas.mapRenderer().destinationCrs()
          distance_calc = QgsDistanceArea()
          distance_calc.setSourceCrs(crs)
          distance_calc.setEllipsoid(crs.ellipsoidAcronym())
          distance_calc.setEllipsoidalMode(crs.geographicFlag())
          distance = distance_calc.measureLine([self._startPt,endPt]) / 1000
          QMessageBox.information(None,"Clicked coords","Distance = %d km" % distance)
         # messageBar = MessageBar(self.canvas)
         # messageBar.pushMessage("Distance","Distance = %d km" % distance,level= QMessageBox.information,duration=2)
       

class CaptureTool(QgsMapTool,MapToolMixin):
    CAPTURE_LINE    = 1
    CAPTURE_POLYGON = 2
    def __init__(self, canvas, layer,parent,onGeometryAdded,captureMode):
        QgsMapTool.__init__(self, canvas)
        self.canvas          = canvas
        self.layer           = layer
        self.onGeometryAdded = onGeometryAdded
        self.captureMode     = captureMode 
        self.rubberBand      = None
        self.tempRubberBand  = None
        self.capturedPoints  = []
        self.capturing       = False
        self.setCursor(Qt.CrossCursor)
        self.parent=parent
        self.dpi=300
	self.dim_titre = 12
	self.dim_coltext= 8 
    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.capturing:
                self.startCapturing()
            self.addVertex(event.pos())
        elif event.button() == Qt.RightButton:
            points = self.getCapturedGeometry()
            print points
            self.stopCapturing()
            if points != None:
                self.geometryCaptured(points)

    def canvasMoveEvent(self, event):
        if self.tempRubberBand != None and self.capturing:
            mapPt,layerPt = self.transformCoordinates(event.pos())
            self.tempRubberBand.movePoint(mapPt) 

    def getnearpos(self,array,value):
        #idx = (np.abs(array-value)).argmin()
        idx = np.abs(array-value).argmin()
        return idx

    def keyPressEvent(self, event):
         if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Delete:
             self.removeLastVertex()
             event.ignore()
         if event.key() == Qt.Key_Return or event.key() ==  Qt.Key_Enter:
             points = self.getCapturedGeometry()
             self.stopCapturing()
             if points != None:
                 self.geometryCaptured(points)

    def transformCoordinates(self, canvasPt):
        return (self.toMapCoordinates(canvasPt),
        self.toLayerCoordinates(self.layer, canvasPt))

    def startCapturing(self):
        color = QColor("red")
        color.setAlphaF(0.78)
        self.rubberBand = QgsRubberBand(self.canvas,self.bandType())
        self.rubberBand.setWidth(2)
        self.rubberBand.setColor(color)
        self.rubberBand.show()
        self.tempRubberBand = QgsRubberBand(self.canvas,self.bandType())
        self.tempRubberBand.setWidth(2)
        self.tempRubberBand.setColor(color)
        self.tempRubberBand.setLineStyle(Qt.DotLine)
        self.tempRubberBand.show()
        self.capturing = True

    def bandType(self):
        if self.captureMode == CaptureTool.CAPTURE_POLYGON:
            return QGis.Polygon
        else:
            return QGis.Line

    def stopCapturing(self):
        if self.rubberBand:
             self.canvas.scene().removeItem(self.rubberBand)
             self.rubberBand = None
        if self.tempRubberBand:
             self.canvas.scene().removeItem(self.tempRubberBand)
             self.tempRubberBand = None
        self.capturing = False
        self.capturedPoints = []
        self.canvas.refresh()

    def addVertex(self, canvasPoint):
        mapPt,layerPt = self.transformCoordinates(canvasPoint)
        self.rubberBand.addPoint(mapPt)
        self.capturedPoints.append(layerPt)
        self.tempRubberBand.reset(self.bandType())
        if self.captureMode == CaptureTool.CAPTURE_LINE:
            self.tempRubberBand.addPoint(mapPt)
        elif self.captureMode == CaptureTool.CAPTURE_POLYGON:
            firstPoint = self.rubberBand.getPoint(0, 0)
            self.tempRubberBand.addPoint(firstPoint)
            self.tempRubberBand.movePoint(mapPt)
            self.tempRubberBand.addPoint(mapPt)
            
    def removeLastVertex(self):
        if not self.capturing: return
        
        bandSize     = self.rubberBand.numberOfVertices()
        tempBandSize = self.tempRubberBand.numberOfVertices()
        numPoints    = len(self.capturedPoints)
        if bandSize < 1 or numPoints < 1:
            return
            
        self.rubberBand.removePoint(-1)
        
        if bandSize > 1:
            if tempBandSize > 1:
                point = self.rubberBand.getPoint(0, bandSize-2)
                self.tempRubberBand.movePoint(tempBandSize-2,
                point)
        else:
            self.tempRubberBand.reset(self.bandType())
        del self.capturedPoints[-1]
    
    def getCapturedGeometry(self):
        points = self.capturedPoints
        if self.captureMode == CaptureTool.CAPTURE_LINE:
            if len(points) < 2:
                return None
        if self.captureMode == CaptureTool.CAPTURE_POLYGON:
            if len(points) < 3:
                return None
        if self.captureMode == CaptureTool.CAPTURE_POLYGON:
            points.append(points[0]) # Close polygon.
        return points
        
    def geometryCaptured(self, layerCoords,name=None,list_param=None,prof=None):
        self.vpr = self.layer.dataProvider()
        self.clearMemoryLayer(self.layer)
        if self.captureMode == CaptureTool.CAPTURE_LINE:
            geometry = QgsGeometry.fromPolyline(layerCoords)
        elif self.captureMode == CaptureTool.CAPTURE_POLYGON:
            geometry = QgsGeometry.fromPolygon([layerCoords])
        feature = QgsFeature()
        feature.setGeometry(geometry)
        self.vpr.addFeatures([feature])
        print layerCoords
        print type(layerCoords)
        print "-------------------"
        print len(layerCoords)
        print "-------------------"
        #self.layer.addFeature(feature)
        self.layer.updateExtents()
        list_x0=[]
        list_y0=[]
        for var in layerCoords:
          list_x0.append(var[0])
          list_y0.append(var[1])
        print list_x0,list_y0
        new_sect=Section()
        nb_flag=0
        l=self.parent.view.currentLayer()
        if not l :
            print "Layer not selected"
            return
        else :
           print l.source()
           fileName=l.source().split('"')[1]
           #print "Filename %s " %(str(fileName))
        variable=str(self.parent.cboVars.currentText())
        if not variable :
            print "Variable not selected"
            return
        if len(list_param) > 3 :
            print "define prof min prof max"
            print list_param[3],list_param[4]
        print "Extract variable %s " %(variable)
        lgname_plot,unit_plot,longitude,latitude,profondeur,time_counter,plotvar, \
                nsect,latref,lonref,lon_list,lat_list= new_sect.sect_extract(list_x0,list_y0,fileName,variable,nb_flag)
        if prof :
            print "prof"
            print prof[0],prof[1]
            ind_min=self.getnearpos(profondeur,prof[0])
            ind_max=self.getnearpos(profondeur,prof[1])
            #profondeur2=profondeur[ind_min:ind_max]
            profondeur=profondeur[ind_min:ind_max]
            print plotvar.shape
            plotvar=plotvar[:,ind_min:ind_max,:,:]
            print plotvar.shape
            print "Find indice for depth"
            #print ind_min,ind_max,profondeur2
        X1,lonsec,latsec,sect_var= \
                     new_sect.sect_compute(longitude,latitude,profondeur,time_counter, \
                     plotvar,int(nsect),float(latref),float(lonref),lon_list,lat_list)
        print "Compute section OK"
        ## Load colormap
        file_color=str(self.parent.homepath)+'/statics/colormap.p'
        f = file(file_color, 'rb')
        dict_colorbar=cPickle.load(f)
        if name :
           section_name=str(name)
           reg=str(name)
           print "Sections %s " %(section_name)
        else :
            section_name="Section_"+str(list_x0[0])+'_'+str(list_y0[0])
            reg='Section_'+str(list_x0[0])+'_'+str(list_y0[0])
        echeance_name="hindcast"
        SysName=os.path.basename(str(fileName))[0:17]
        cmap_scal=dict_colorbar['DblBlLBlAqGrYeOrReDRe']
        date_str=os.path.basename(str(fileName)).split('_')[3]
        date=os.path.basename(str(fileName)).split('_')[4].split('.')[0][1:]
        ## To be changed
        longname=lgname_plot[0]
        unitname=unit_plot[0]
        dpi=new_sect.dpi
        dim_titre=new_sect.dim_titre
        dim_coltext=new_sect.dim_coltext
        img_dir=self.parent.tmp_path
        new_sect.sectplot(X1,lonsec,latsec,profondeur,sect_var[:,:,:],longname,unitname,\
             section_name,echeance_name,reg,date_str,date,img_dir,int(dpi),int(dim_titre),int(dim_coltext),SysName,cmap_scal,list_param)
        print "Plot OK"
        self.onGeometryAdded()
 
class SelectVertexTool(QgsMapTool, MapToolMixin):
    def __init__(self, canvas, Layer, CurrentLayer, parent,onVertexSelected):
        QgsMapTool.__init__(self, canvas)
        self.onVertexSelected = onVertexSelected
        self.setLayer(Layer)
        self.setCursor(Qt.CrossCursor)
        self.layer=Layer
        self.currentlayer=CurrentLayer
        self.vpr=self.layer.dataProvider()
        self.canvas=canvas
        self.mainwindow=parent
    def clearMemoryLayer(self, layer):
        featureIDs = []
        provider = layer.dataProvider()
        for feature in provider.getFeatures(QgsFeatureRequest()):
            featureIDs.append(feature.id())
            provider.deleteFeatures(featureIDs) 
    def plot(self,variable=None,posx=None,posy=None):
       ## print "Inside plot"
       style.use('ggplot')
       fig, ax = plt.subplots(figsize=(5, 7))
       #if ( max(depth) > 0 ) :
       ax.invert_yaxis()
       ax.plot(self.var, self.prof, label=self.label, linewidth=2)
       offset = 0.01
       x1, x2 = ax.get_xlim()[0] - offset, ax.get_xlim()[1] + offset
       ax.set_xlim(x1, x2)
       ax.legend (loc=4)
       #ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
       #ax.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
       #    ncol=2, mode="expand", borderaxespad=0.)
       ax.set_title(self.title)
       ax.set_xlabel(self.xlabel)
       ndpi=75
       rep_out=self.mainwindow.tmp_path
       print rep_out
       nom_image="Profile_"+variable+"_lon"+posx+"_lat_"+posy
       print nom_image 
       ax.set_ylabel(self.ylabel)
       plt.savefig(rep_out+nom_image,dpi=ndpi,format='png')
       print "save ok"
       plt.show()
     
    def lookupNearest(self,x0, y0,lon,lat):
        print "lookupNearest"
        xi = np.abs(lon-x0).argmin()
        yi = np.abs(lat-y0).argmin()
        return xi,yi
    def canvasReleaseEvent(self, event):
        #Get the click
        x = event.pos().x()
        y = event.pos().y()
        print x,y
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        extent = self.canvas.extent()
        width = round(extent.width() / self.canvas.mapUnitsPerPixel());
        height = round(extent.height() / self.canvas.mapUnitsPerPixel());
        print "---SelectVertexTool release event ---"
        print width,height
        layer=self.currentlayer
        point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
        position=self.canvas.getCoordinateTransform().toMapCoordinates(event.pos())
        
        if position is not None:
            ident = layer.dataProvider().identify(position, QgsRaster.IdentifyFormatValue,self.canvas.extent(), width, height ).results()
            iband=1
            self.clearMemoryLayer(self.layer)
            geometry = QgsGeometry.fromPoint(position)
            feature = QgsFeature()
            feature.setGeometry(geometry)
            self.vpr.addFeatures([feature])
            self.layer.updateExtents()
            if not ident or not ident.has_key( iband ): # should not happen
                  bandvalue = "?"
            else:
              bandvalue = ident[iband]#.toPyObject()
              if bandvalue is None:
                 bandvalue = "no data"
        ## Plot profile 
        l=self.currentlayer
        if not l :
           print "Layer not selected"
        else :
            print l.source()
            fileName=l.source().split('"')[1]
            print "Filename %s " %(str(fileName))
            nc_file=netCDF4.Dataset(str(fileName),'r')
            x0= float(point.x())
            y0=float(point.y())
            print x0,y0
            variable=str(self.mainwindow.cboVars.currentText())
            print "variable : %s" %(str(variable))
            lon = nc_file.variables['longitude'][:]
            lat = nc_file.variables['latitude'][:]
            self.prof=nc_file.variables['depth_TEMP'][:]
            min_prof=np.nanmin(self.prof)
            max_prof=np.nanmax(self.prof)
            profdialog=OlaParams(str(min_prof),str(max_prof))
            profdialog.show()
            if profdialog.exec_() == QDialog.Accepted:
                prof_min = float(profdialog.minprof_fieldgrid.text())
                prof_max = float(profdialog.maxprof_fieldgrid.text())
                ##  get position
                ind_min=self.getnearpos(self.prof,prof_min)
                ind_max=self.getnearpos(self.prof,prof_max)
                self.prof=self.prof[ind_min:ind_max]
                ## Find Nearest point in the grid
                xi,yi=self.lookupNearest(x0,y0,lon,lat)
                #print xi,yi,lon[xi],lat[yi]
                temps=0
                self.var=nc_file.variables[variable][temps,ind_min:ind_max,yi,xi]
                self.xlabel=variable
                self.title=variable+" Profile pos lon:"+str(x0)[0:5]+" lat:"+str(y0)[0:5]
                self.ylabel="Pressure [dbar]"
                self.label=variable[0:4]
                print "plot"
                self.plot(variable,str(x0),str(y0))
                self.onVertexSelected() 

    def getnearpos(self,array,value):
        idx = np.abs(array-value).argmin()
        return idx


#    def canvasReleaseEvent(self, event):
#        feature = self.findFeatureAt(event.pos())
#        if feature != None:
#            vertex = self.findVertexAt(feature, event.pos())
#            if vertex != None:
#                self.onVertexSelected(feature, vertex) 
#    
