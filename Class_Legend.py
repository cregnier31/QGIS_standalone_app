from qgis.core import *
from qgis.gui import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from rasparenzadialog import rasparenzaDialog
import resources_rc

# A Menu Class to do apply actions on the selected layer
class MyMenuProvider(QgsLayerTreeViewMenuProvider):
  def __init__(self, view,list_layers,canvas,explorer):
    QgsLayerTreeViewMenuProvider.__init__(self)
    print "Init MyMenuProvider"
    self.view = view
    self.canvas=canvas
    self.root = QgsProject.instance().layerTreeRoot()
    self.layers=list_layers
    self.explorer=explorer
  def createContextMenu(self):
    imgs_dir=":images/icons/"
    if not self.view.currentLayer():
      return None
    m = QMenu()
    #m.addSeparator()
    m.addAction(QIcon(imgs_dir+"mIconAtlas.png"), "&Show Extent", self.showExtent) 
    m.addAction(QIcon(imgs_dir+"mActionZoomFullExtent.png"),"&Zoom to layer extent", self.zoomToLayer )
    m.addAction(QIcon(imgs_dir+"removeLayer.png"), "&Remove layer",self.removeCurrentLayer )
    m.addAction(QIcon(imgs_dir+"mActionRemoveAllFromOverview.png"),"&Remove all layers",self.removeAll )
    m.addAction(QIcon(imgs_dir+"mIconInfo.png"),"&Get properties",self.getLayerProperties )
    m.addAction(QIcon(imgs_dir+"mIconTransparency.png"),"&Set transparency",self.SetTransparency)
    m.addAction(QIcon(imgs_dir+"mActionDraw.png"),"&Reload file",self.ReloadFile)

    return m

  def ReloadFile(self):
    l=self.view.currentLayer()
    if not l :
       print "Layer not selected"
    else :
      fileName=l.source().split('"')[1]
      print type(fileName)
      print "Filename %s " %(str(fileName))
      self.explorer.updateFile(str(fileName))

  def showExtent(self):
    r = self.view.currentLayer().extent()
    QMessageBox.information(None, "Extent", r.toString())

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
    self.clear()

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
  def SetTransparency(self):
     self.dlg=rasparenzaDialog()
     self.dlg.show()
     # Run the dialog event loop
     result = self.dlg.exec_()
     # See if OK was pressed
     if result == 1:
        rasterSlider = self.dlg.findChild(QSlider, "horizontalSlider")
        valore = float(rasterSlider.value())
        valoi  = rasterSlider.value()
        valoi255 = (valoi) * 255. / 100.
        valoi255 = 255. - (valoi255)
        valo   = (100. - valore) / 100.
        layer=self.view.currentLayer()
        if layer.type() == layer.RasterLayer:
          if QGis.QGIS_VERSION_INT < 10900:
            layer.setTransparency(int(valoi255))
          else:
            layer.renderer().setOpacity(valo)
        self.canvas.refresh()

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
