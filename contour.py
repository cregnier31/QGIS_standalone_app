#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       contour.py
#
#       Copyright 2009 Lionel Roubeyrie <lionel.roubeyrie@gmail.com>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

#  Modified by Chris Crook <ccrook@linz.govt.nz> to contour irregular data

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import QDomDocument
from qgis.core import *
import resources

import sys
import os.path
import string
import math
import re
import inspect

mplAvailable=True
try:
    import numpy as np
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.mlab import griddata
    from shapely.geometry import MultiLineString, MultiPolygon
except:
    mplAvailable=False


from frmContour import Ui_ContourDialog

EPSILON = 1.e-27
LINES='lines'
FILLED='filled'
LAYERS='layers'
BOTH='both'

def _interpolate(a, b, fraction):
    return a + (b - a)*fraction;

# Crude point thinning algorithm!

def _thindex1( x, y, x0, y0, resolution, index=None):
    if index is None:
        index=np.arange(x.shape[0],dtype=int)
    values,ix=np.unique(((x[index]-x0)/resolution).astype(int),return_inverse=True)
    values,iy=np.unique(((y[index]-y0)/resolution).astype(int),return_inverse=True)
    mix=ix*values.shape[0]+iy
    values,indices=np.unique(mix,return_inverse=True)
    thinned=np.zeros(values.shape,dtype=int)
    thinned[indices]=index
    return thinned

def _thindex(x,y,resolution):
    x0=np.min(x)
    y0=np.min(y)
    index=_thindex1(x,y,x0,y0,resolution)
    index=_thindex1(x,y,x0+resolution/2,y0,resolution,index)
    index=_thindex1(x,y,x0,y0+resolution/2,resolution,index)
    index=_thindex1(x,y,x0+resolution/2,y0+resolution/2,resolution,index)
    return index


  #  def run(self):
  #      try:
  #          dlg = ContourDialog(self._iface)
  #          dlg.exec_()
  #      except ContourError:
  #          QMessageBox.warning(self._iface.mainWindow(), "Contour error",
  #              unicode(sys.exc_info()[1]))

###########################################################

class ContourError(Exception):
    def __init__(self, message):
        self._message = message
    def __str__(self):
        return self._message

class ContourGenerationError(Exception):
    pass

###########################################################
class ContourDialog(QDialog,Ui_ContourDialog):

    def __init__(self,layer,canvas,is_standalone):
        QDialog.__init__(self)
        self._data = None
        self.layer=layer
        self.canvas=canvas
        self._loadedDataDef = None
        self._layer=None
        self._zField = ""
        self._dataIsGrid = False
        self._gridData = None
        self._nr = None
        self._nc = None
        self._gridSaved = False
        self._gridDisplayed = False
        self._zField = ''
        self._loadingLayer = False
        self._contourId = ''
        self._replaceLayerSet = None
        self._standalone=is_standalone
        ## test
        # Set up the user interface from Designer.
        #self.ui = Ui_ContourDialog()
        self.setupUi(self)
        # For the moment don't enable "contour layers"
        # Not sure that there is a valid use case?
        self.uLayerContours.hide()

        self._okButton = self.uButtonBox.button(QDialogButtonBox.Ok)
        self._okButton.setEnabled(False)
        re = QRegExp("\\d+\\.?\\d*(?:[Ee][+-]?\\d+)?")
        self.uLevelsList.setSortingEnabled(False)
        self.uSelectedOnly.setChecked(False)
        self.uSelectedOnly.setEnabled(False)
        self.uColorRamp.populate(QgsStyleV2.defaultStyle())
        self.uDataField.setExpressionDialogTitle("Value to contour")
        self.uLevelsNumber.setMinimum(2)
        self.uLevelsNumber.setValue(10)
        self.uLinesContours.setChecked(True)
        self.uExtend.setCurrentIndex(0)
        self.progressBar.setValue(0)

        self.loadSettings()

        #mapCanvas = self.canvas
        self._loadingLayer = True

        for layer in self.sourceLayers():
           self.uLayerName.addItem(layer.name(),layer)
        self.uLayerName.setCurrentIndex(-1)
        self._loadingLayer = False

        self.enableOkButton()

        #Signals
        self.uLayerName.currentIndexChanged[int].connect(self.uLayerNameUpdate)
        self.uDataField.fieldChanged['QString'].connect(self.uDataFieldUpdate)
        self.uSelectedOnly.toggled.connect(self.reloadData)
        self.uMinContour.valueChanged[float].connect(self.computeLevels)
        self.uMaxContour.valueChanged[float].connect(self.computeLevels)
        self.uLevelsNumber.valueChanged[int].connect(self.computeLevels)
        self.uPrecision.valueChanged[int].connect(self.updatePrecision)
        self.uTrimZeroes.toggled[bool].connect(self.updatePrecision)
        self.uLevelsList.itemDoubleClicked[QListWidgetItem].connect(self.editLevel)
        self.uButtonBox.helpRequested.connect(self.showHelp)
        self.uMethod.currentIndexChanged[int].connect(self.computeLevels)
        self.uLinesContours.toggled[bool].connect(self.modeToggled)
        self.uFilledContours.toggled[bool].connect(self.modeToggled)
        self.uBoth.toggled[bool].connect(self.modeToggled)
        self.uLayerContours.toggled[bool].connect(self.modeToggled)

        # populate layer list
        if self.uLayerName.count() <= 0:
            raise ContourError("There are no layers suitable for contouring.\n"+
                              "(That is, point layers with numeric attributes)")
        self.setupCurrentLayer( self.layer)
        if self.uLayerName.currentIndex() < 0 and self.uLayerName.count()==1:
            self.uLayerName.setCurrentIndex(0)
        
        # Is MPL version Ok?
        if self._isMPLOk() == False:
            self.message(text="Your matplotlib python module seems to not have the required "+
            "version for using the last contouring algorithms. "+
            "Please note : your points datas must be placed on a regular "+
            "grid before calling this plugin, or update your matplotlib "+
            "module to >= 1.0.0\n", title="Minimum version required")

    def closeEvent(self,event):
        self.saveSettings()
        QDialog.closeEvent(self,event)

    def _isGridded(self):
        """
        Check if points data are on a regular grid
        """
        data=self.getData()
        if not data:
            return
        (x, y, z) = data
        l = len(x)
        xd=np.diff(x)
        yd=np.diff(y)
        ld = l-1
        ends = np.flatnonzero(xd[0:ld-1]*xd[1:ld]+yd[0:ld-1]*yd[1:ld]<0)+2
        nr = ends[0]
        nc = (len(ends)/2)+1
        ok = True
        if (len(ends) < 2) or (nr*nc != l) or (any(ends%nr > 1)):
           ok = False
        self._nr = nr
        self._nc = nc
        return ok

    def _isMPLOk(self):
        """
        Check if matplotlib version > 1.0.0 for contouring fonctions selection
        """
        version = [int(i) for i in mpl.__version__.split('.')[0:2]]
        return version >= [1, 0]

    def updatePrecision( self, ndp ):
        ndp=self.uPrecision.value()
        self.uMinContour.setDecimals( ndp )
        self.uMaxContour.setDecimals( ndp )

    def setupCurrentLayer( self, layer ):
        if not layer:
            return
        properties = self.getContourProperties( layer )
        contourId = ''
        sourceLayer = None
        if properties:
            layerId = properties.get('SourceLayerId')
            for l in self.sourceLayers():
                if l.id() == layerId:
                    sourceLayer = l
                    break
            if sourceLayer:
                layer = sourceLayer
                contourId = properties.get('ContourId')
        index = self.uLayerName.findData(layer)
        if index >= 0:
            self.uLayerName.setCurrentIndex(index)
        # If valid existing contour layer, then reset
        if not contourId:
            return
        layerSet = self.contourLayerSet( contourId )
        try:
            attr = properties.get('SourceLayerAttr')
            self.uDataField.setField(attr)
            if layerSet.has_key(FILLED):
                if layerSet.has_key(LINES):
                    self.uBoth.setChecked(True)
                else:
                    self.uFilledContours.setChecked(True)
            elif layerSet.has_key(LAYERS):
                    self.uLayerContours.setChecked(True)
            else:
                self.uLinesContours.setChecked(True)
            levels = properties.get('Levels').split(';')
            self.uLevelsNumber.setValue(len(levels))
            self.uMinContour.setValue(float(properties.get('MinContour')))
            self.uMaxContour.setValue(float(properties.get('MaxContour')))
            index = self.uMethod.findText(properties.get('Method'))
            if index >= 0:
                self.uMethod.setCurrentIndex(index)
            index = self.uExtend.findText(properties.get('Extend'))
            if index >= 0:
                self.uExtend.setCurrentIndex(index)
            self.uLevelsList.clear()
            for level in levels:
                self.uLevelsList.addItem(level)
            self.uPrecision.setValue(int(properties.get('LabelPrecision')))
            self.uTrimZeroes.setChecked(properties.get('TrimZeroes') == 'yes' )
            self.uLabelUnits.setText(properties.get('LabelUnits') or '')
            self.uApplyColors.setChecked( properties.get('ApplyColors') == 'yes' )
            ramp=self.stringToColorRamp( properties.get('ColorRamp'))
            if ramp:
                self.uColorRamp.setSourceColorRamp(ramp)
            self.uReverseRamp.setChecked( properties.get('ReverseRamp') == 'yes' )
        finally:
            pass
        self._replaceLayerSet = layerSet

    def uLayerNameUpdate(self, index):
        if self._loadingLayer:
            return
        self._replaceLayerSet = None
        self._layer = self.uLayerName.itemData(index).toPyObject()
        self.uLayerDescription.setText("")
        # Get a default resolution for point thinning
        extent=self._layer.extent()
        resolution=(extent.width()+extent.height())/20000.0;
        radius=0.000001
        while radius < resolution:
            if radius * 2 > resolution:
                break
            if radius * 5 > resolution:
                radius *= 2
                break
            if radius * 10 > resolution:
                radius *= 5
                break
            radius *= 10
        self.uThinRadius.setValue( radius )
        self._loadingLayer=True
        haveSelected=self._layer.selectedFeatureCount() > 0
        self.uSelectedOnly.setChecked(haveSelected)
        self.uSelectedOnly.setEnabled(haveSelected)
        self._loadingLayer=False
        self.uDataField.setLayer( self._layer )
        # Force an update as setLayer may set value but not trigger update
        self.uDataFieldUpdate("")
        self.enableOkButton()

    def uDataFieldUpdate(self, inputField):
        self._zField,isExpression,isValid = self.uDataField.currentField()
        self.reloadData()

    def reloadData(self):
        if self._loadingLayer:
            return
        self._replaceLayerSet = None
        if not self._layer:
            return
        if not self._zField:
            self.enableOkButton()
            return
        data=self.getData()
        if not data:
            self.enableOkButton()
            return
        self.updateOutputName()
        self.enableOkButton()

    def updateOutputName(self):
        if self._layer.name() and self._zField:
            zf=self._zField
            if re.search(r'\W',zf):
                zf='expr'
            self.uOutputName.setText("%s_%s"%(self._layer.name(), zf ))

    def editLevel(self, item):
        val = item.text()
        data=self.getData()
        if data:
            z = data[2]
            newval, ok = QInputDialog.getText(self, "Update level", 
                             "Enter a single level to replace this one,\n"+
                             "or a space separated list of levels to replace all",
                             QLineEdit.Normal,
                             val)
            if ok:
                values=newval.split()
                for v in values:
                    try:
                        float(v)
                    except:
                        QMessageBox.warning(self.canvas.mainWindow(), "Contour error",
                                            "Invalid contour value "+v)
                        return
                if len(values) < 1:
                    return
                if len(values) == 1: 
                    item.setText(newval)
                    self.enableOkButton()
                    return
                values.sort(key=float)
                self.uLevelsNumber.setValue(len(values))
                self.uLevelsList.clear()
                for v in values:
                    self.uLevelsList.addItem(v)
                self.enableOkButton()

    def computeLevels(self):
        method = self.uMethod.itemText(self.uMethod.currentIndex())

        # If manually setting levels then don't do this work! and leave existing contours 
        # in place.

        if method == "Manual" and self.uLevelsList.count()==self.uLevelsNumber.value():
            return

        # Default if there is no data or using "Equal" method...
        levels = np.linspace(float(self.uMinContour.value()),
                        float(self.uMaxContour.value()),
                        self.uLevelsNumber.value())

        if method == "Quantile":
            data=self.getData()
            if data:
                values = np.sort(data[2].flatten())
                values = values[(float(self.uMinContour.value()) <= values) & (values <= self.uMaxContour.value())]
                if values.size > 1:
                    levels=list()
                    for per in np.linspace(0, 100, self.uLevelsNumber.value()):
                        idx = per /100. * (values.shape[0] - 1)
                        if (idx % 1 == 0):
                            levels.append(values[idx])
                        else:
                            v = _interpolate(values[int(idx)], values[int(idx) + 1], idx % 1)
                            levels.append(v)

        self.uLevelsList.clear()
        for i in range(0, len(levels)):
            self.uLevelsList.addItem(self.formatLevel(levels[i]))
        self.enableOkButton()

    def modeToggled(self,enabled):
        if enabled:
            self.enableOkButton()

    def enableOkButton(self):
        self._okButton.setEnabled(False)
        try:
            self.validate()
            self._okButton.setEnabled(True)
        except:
            pass

    def confirmReplaceSet(self,set):
        message = "The following layers already have contours of " + self._zField + "\n"
        message = message + "Do you want to replace them with the new contours?\n\n"

        for layer in set.values():
            message = message + "\n   " + layer.name()
        return QMessageBox.question(self,"Replace contour layers",message,
                             QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)

    def accept(self):
        try:
            self.validate()
            self.validateConditions()
            self._contourId = QDateTime.currentDateTime().toString("yyyyMMddhhmmss")
            replaceContourId = ''
            for set in self.candidateReplacementSets():
                result = self.confirmReplaceSet(set)
                if result == QMessageBox.Cancel:
                    return
                if result == QMessageBox.Yes:
                    self._replaceLayerSet = set
                    replaceContourId = self.layerSetContourId(set)
                    break

            try:
                QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
                if self.uLinesContours.isChecked():
                    self.makeContours()
                elif self.uFilledContours.isChecked():
                    self.makeFilledContours()
                elif self.uBoth.isChecked():
                    self.makeFilledContours()
                    self.makeContours()
                elif self.uLayerContours.isChecked():
                    self.makeFilledContours(True)
                oldLayerSet = self.contourLayerSet( replaceContourId )
                if oldLayerSet:
                    for layer in oldLayerSet.values():
                        QgsMapLayerRegistry.instance().removeMapLayer( layer.id() )
                self._replaceLayerSet = self.contourLayerSet(self._contourId)
            finally:
                QApplication.restoreOverrideCursor()

        except ContourError:
            self.message("Error calculating grid/contours: "+unicode(sys.exc_info()[1]))
        except ContourGenerationError:
            self.message("Exception encountered: " + unicode(sys.exc_info()[1])+" (Try thinning points)")
        # self._okButton.setEnabled(False)

    def message(self,text,title="Contour Error"):
        QMessageBox.warning(self, title, text)

    def showHelp(self):
        file = inspect.getsourcefile(ContourDialog)
        file = 'file://' + os.path.join(os.path.dirname(file),'index.html')
        file = file.replace("\\","/")
        self._iface.openURL(file,False)

    def validate(self):
        message = None
        if self.uLayerName.currentText() == "":
            message = "Please specify vector layer"
        if (self.uDataField.currentText() == ""):
            message = "Please specify data field"
        if message != None:
            raise ContourError(message)

    def validateConditions(self):
        if (self._isMPLOk() == False) and (self._isGridded() == False):
            message = "This layer does not have a regular data grid and your matplotlib module is not suitable to compute contouring"
            raise ContourError(message)
    #############################################################################
    # Contour calculation code

    def sourceLayers(self):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if (layer.type() == layer.VectorLayer) and (layer.geometryType() == QGis.Point):
                yield layer

    def getLevels(self):
        list = self.uLevelsList
        return [float(list.item(i).text()) for i in range(0, list.count())]

    def clearLayer(self, layer):
        pl = layer.dataProvider()
        request = QgsFeatureRequest()
        request.setFlags(QgsFeatureRequest.NoGeometry)
        request.setSubsetOfAttributes([])
        fids = []
        for f in pl.getFeatures(request):
            fids.append(f.id())
        pl.deleteFeatures(fids)
        pl.deleteAttributes(pl.attributeIndexes())
        layer.updateFields()

    def createVectorLayer(self, type, name, mode,fields):
        layer = None
        if self._replaceLayerSet:
            layer = self._replaceLayerSet.get(mode)

        if layer:
            self.clearLayer(layer)
        else:
            url=type+'?crs=internal:'+str(self._crs.srsid())
            layer = QgsVectorLayer(url, name, "memory")

        if not layer:
            raise ContourError("Could not create layer for contours")

        attributes = [
            QgsField(name,QVariant.Int,'Int') if ftype == int else
            QgsField(name,QVariant.Double,'Double') if ftype == float else
            QgsField(name,QVariant.String,'String')
            for name, ftype in fields
        ]
        pr = layer.dataProvider()
        pr.addAttributes( attributes )
        layer.updateFields()

        layer.setCrs(self._crs, False)
        levels = ";".join(map(str, self.getLevels()))
        properties = {
            'ContourId' : self._contourId,
            'SourceLayerId' : self._layer.id(),
            'SourceLayerAttr' : self._zField,
            'Mode' : mode,
            'Levels' : levels,
            'LabelPrecision' : str(self.uPrecision.value()),
            'TrimZeroes' : 'yes' if self.uTrimZeroes.isChecked() else 'no',
            'LabelUnits' : unicode(self.uLabelUnits.text()),
            'MinContour' : str(self.uMinContour.value()),
            'MaxContour' : str(self.uMaxContour.value()),
            'Extend' : self.uExtend.itemText(self.uExtend.currentIndex()),
            'Method' : self.uMethod.itemText(self.uMethod.currentIndex()),
            'ApplyColors' : 'yes' if self.uApplyColors.isChecked() else 'no',
            'ColorRamp' : self.colorRampToString( self.uColorRamp.currentColorRamp()),
            'ReverseRamp' : 'yes' if self.uReverseRamp.isChecked() else 'no',
            }
        self.setContourProperties(layer, properties)
        return layer

    def addLayer(self, layer):
        registry = QgsMapLayerRegistry.instance()
        if not registry.mapLayer(layer.id()):
            registry.addMapLayer(layer)
        else:
            self.canvas.legendInterface().setLayerVisible(layer, True)
            layer.setCacheImage(None)
            self.canvas.refresh()

    def setContourProperties( self, layer, properties ):
        for key in properties.keys():
            layer.setCustomProperty('ContourPlugin.'+key, properties[key])

    def getContourProperties( self, layer ):
        if layer.type() != layer.VectorLayer or layer.dataProvider().name() != "memory":
            return None
        properties = {}
        for key in [
            'ContourId',
            'SourceLayerId',
            'SourceLayerAttr',
            'Mode',
            'Levels',
            'LabelPrecision',
            'MinContour',
            'MaxContour',
            'Extend',
            'Method',
            'ApplyColors',
            'ColorRamp',
            'ReverseRamp'
            ]:
            properties[key] = unicode(layer.customProperty('ContourPlugin.'+key))
        if not properties['ContourId']:
            return None
        return properties

    def contourLayers(self, wanted={}):
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            properties = self.getContourProperties(layer)
            if not properties:
                continue
            ok = True
            for key in wanted.keys():
                if properties.get(key) != wanted[key]:
                    ok = False
                    break
            if ok:
                yield layer

    def contourLayerSet( self, contourId ):
        layers = self.contourLayers({'ContourId':contourId} )
        layerSet={}
        for layer in layers:
            properties = self.getContourProperties(layer)
            layerSet[properties.get('Mode')] = layer
        return layerSet

    def layerSetContourId( self, layerSet ):
        if layerSet:
            return self.getContourProperties(layerSet.values()[0]).get('ContourId')
        return None

    def candidateReplacementSets( self ):
        # Note: use _replaceLayerSet first as this will be the layer
        # set that the contour dialog was opened with. Following this
        # look for any other potential layers.
        ids = []
        if self._replaceLayerSet:
            set = self._replaceLayerSet
            self._replaceLayerSet = None
            ids.append(self.layerSetContourId(set))
            yield set

        for layer in self.contourLayers({
            'SourceLayerId' : self._layer.id(),
            'SourceLayerAttr' : self._zField } ):
            id = self.getContourProperties(layer).get('ContourId')
            if id in ids:
                continue
            ids.append(id)
            yield self.contourLayerSet(id)

    def makeContours(self):
        lines = self.computeContours()
        if lines is None:
            return
        clayer =  self.buildContourLayer(lines)
        self.addLayer(clayer)

    def makeFilledContours(self, asLayers=False):
        polygons = self.computeFilledContours( asLayers )
        if polygons is None:
            return
        if asLayers:
            clayer = self.buildLayeredContourLayer(polygons)
        else:
            clayer = self.buildFilledContourLayer(polygons)
        self.addLayer(clayer)

    def dataChanged( self ):
        data=self.getData()
        if data:
            z = data[2]
            self.uMinContour.setValue(np.min(z))
            self.uMaxContour.setValue(np.max(z))

    def getData(self):
        layer=self._layer
        zField=self._zField
        if not layer:
            return None
        if not zField:
            return None

        selectedOnly = self.uSelectedOnly.isChecked()
        radius=self.uThinRadius.value() if self.uThinPoints.isChecked() else 0.0

        dataDef=(layer.id(),zField,radius)
        if dataDef == self._loadedDataDef:
            return self._data

        try:
            self._data=None
            self._gridData = None
            self._loadedDataDef=dataDef
            self._crs = layer.crs()

            fids=None
            if selectedOnly:
                fids=set(layer.selectedFeaturesIds())

            self.progressBar.setRange(0, layer.featureCount())
            count = 0
            x = list()
            y = list()
            z = list()
            try:
                expression=QgsExpression(zField)
                if expression.hasParserError():
                    if layer.fieldNameIndex(zField) >= 0:
                        zField='"'+zField.replace('"','""')+'"'
                        expression=QgsExpression(zField)
                if expression.hasParserError():
                    raise ContourError("Cannot parse "+zField)
                fields=layer.pendingFields()
                if not expression.prepare(fields):
                    raise ContourError("Cannot prepare "+zField+" with "+unicode(fields))
                request = QgsFeatureRequest()
                request.setSubsetOfAttributes( expression.referencedColumns(),fields)
                for feat in layer.getFeatures( request ):
                    try:
                        if fids is not None and feat.id() not in fids:
                            continue
                        if self._standalone : 
                           zval=expression.evaluate(feat).toPyObject() 
                           if zval is not None:
                               geom = feat.geometry().asPoint()
                               x.append(geom.x())
                               y.append(geom.y())
                               z.append(zval)
                        else : 
                           zval=expression.evaluate(feat) 
                           if  type(zval) == type(float()): 
                               geom = feat.geometry().asPoint()
                               x.append(geom.x())
                               y.append(geom.y())
                               z.append(zval)
                    except:
                        raise
                        pass
                    count = count + 1
                    self.progressBar.setValue(count)
            finally:
                self.progressBar.setValue(0)

            if len(x) > 0:
                x=np.array(x)
                y=np.array(y)
                z=np.array(z)
                if radius > 0:
                    index=_thindex(x,y,radius)
                    x=x[index]
                    y=y[index]
                    z=z[index]
                self._data = [x,y,z]
                self._thinRadius=radius
        finally:
            self.dataChanged()
        return self._data

    def computeContours(self):
        extend = self.uExtend.itemText(self.uExtend.currentIndex())
        data=self.getData()
        if not data:
            return
        x, y, z = data
        levels = self.getLevels()
        if not levels:
            return
        try:
            if self._isMPLOk()==True: # If so, we can use the tricontour function
                try:
                    cs = plt.tricontour(x, y, z, levels, extend=extend)
                except:
                    raise ContourGenerationError()
            else:
                gx = x.reshape(self._nr,self._nc)
                gy = y.reshape(self._nr,self._nc)
                gz = z.reshape(self._nr,self._nc)
                cs = plt.contour(gx, gy, gz, levels, extend=extend)
        except:
            raise
        lines = list()
        levels = [float(l) for l in cs.levels]
        for i, line in enumerate(cs.collections):
            linestrings = []
            for path in line.get_paths():
                if len(path.vertices) > 1:
                    linestrings.append(path.vertices)
            lines.append([ i, levels[i], linestrings])
            self.progressBar.setValue(i+1)
        return lines

    def computeFilledContours(self,asLayers=False):
        levels = self.getLevels()
        if not levels:
            return
        data=self.getData()
        if not data:
            return
        polygons = list()
        if asLayers:
            maxvalue=np.max([2])+1000
            for l in levels:
                self._computeFilledContoursForLevel([l,maxvalue],'none',polygons,True)
        else:
            extend = self.uExtend.itemText(self.uExtend.currentIndex())
            self._computeFilledContoursForLevel(levels,extend,polygons)
        return polygons

    
    def _computeFilledContoursForLevel(self,levels,extend,polygons,oneLevelOnly=False):
        data=self.getData()
        if not data:
            return
        x, y, z = data
        if self._isMPLOk()==True: # If so, we can use the tricontour fonction
            try:
                cs = plt.tricontourf(x, y, z, levels, extend=extend)
            except:
                raise ContourGenerationError()
        else:
            gx = x.reshape(self._nr,self._nc)
            gy = y.reshape(self._nr,self._nc)
            gz = z.reshape(self._nr,self._nc)
            try:
                cs = plt.contourf(gx, gy, gz, levels, extend=extend)
            except:
                raise ContourGenerationError()
        levels = [float(l) for l in cs.levels]
        if extend=='min' or extend==BOTH:
            levels = np.append([-np.inf,], levels)
        if extend=='max' or extend==BOTH:
            levels = np.append(levels, [np.inf,])
        # self.progressBar.setRange(0, len(cs.collections))
        for i, polygon in enumerate(cs.collections):
            mpoly = []
            for path in polygon.get_paths():
                path.should_simplify = False
                poly = path.to_polygons()
                exterior = []
                holes = []
                if len(poly)>0:
                    exterior = poly[0] #and interiors (holes) are in poly[1:]
                    #Crazy correction of one vertice polygon, mpl doesn't care about it
                    if len(exterior) < 2:
                        continue
                    p0 = exterior[0]
                    exterior = np.vstack((exterior, self.epsi_point(p0), self.epsi_point(p0)))
                    if len(poly)>1: #There's some holes
                        for h in poly[1:]:
                            if len(h)>2:
                                holes.append(h)

                mpoly.append([exterior, holes])
            if len(mpoly) > 0:
                polygons.append([i, levels[i], levels[i+1], mpoly])
            if oneLevelOnly:
                break
            #self.progressBar.setValue(i+1)
        # self.progressBar.setValue(0)

    def epsi_point(self, point):
        x = point[0] + EPSILON*np.random.random()
        y = point[1] + EPSILON*np.random.random()
        return [x, y]

    def formatLevel( self, level ):
        ndp=self.uPrecision.value()
        trim=self.uTrimZeroes.isChecked()
        if trim:
            return unicode(np.round(level,ndp))
        else:
            return "{1:.{0}f}".format(ndp,level)

    def buildContourLayer(self, lines):
        name = self.uOutputName.text()
        zfield=self._zField
        vl = self.createVectorLayer("MultiLineString", name, LINES,
                                   [('index',int),
                                    (zfield,float),
                                    ('label',str)
                                   ])
        pr = vl.dataProvider()
        fields=pr.fields()
        msg = list()
        symbols=[]
        for i, level, line in lines:
            levels=self.formatLevel(level)+self.uLabelUnits.text()
            try:
                feat = QgsFeature(fields)
                try:
                    feat.setGeometry(QgsGeometry.fromWkt(MultiLineString(line).to_wkt()))
                except:
                    pass
                feat['index']=i
                feat[zfield]=level
                feat['label']=levels
                pr.addFeatures( [ feat ] )
                symbols.append([level,levels])
            except:
                msg.append(unicode(sys.exc_info()[1]))
                msg.append(levels)
        if len(msg) > 0:
            self.message("Levels not represented : "+", ".join(msg),"Contour issue")
        vl.updateExtents()
        vl.commitChanges()
        self.applyRenderer(vl,'line',zfield,symbols)
        return vl

    def buildFilledContourLayer(self, polygons, asLayers=False):
        name = self.uOutputName.text()
        zField = self._zField
        zmin=zField+'_min'
        zmax=zField+'_max'
        vl = self.createVectorLayer("MultiPolygon", name, FILLED,
                                   [('index',int),
                                    (zmin,float),
                                    (zmax,float),
                                    ('label',str)
                                   ])
        pr = vl.dataProvider()
        fields = pr.fields()
        msg = list()
        symbols=[]
        for i, level_min, level_max, polygon in polygons:
            levels = (
                self.formatLevel(level_min) + " - " +
                self.formatLevel(level_max) + self.uLabelUnits.text()
                )
            try:
                feat = QgsFeature(fields)
                try:
                    feat.setGeometry(QgsGeometry.fromWkt(MultiPolygon(polygon).to_wkt()))
                except:
                    continue
                feat['index']=i
                feat[zmin]=level_min
                feat[zmax]=level_max
                feat['label']=levels
                pr.addFeatures( [ feat ] )
                symbols.append([level_min,levels])
            except:
                self.message(unicode(sys.exc_info()[1]))
                msg.append(unicode(levels))
        if len(msg) > 0:
            self.message("Levels not represented : "+", ".join(msg),"Filled Contour issue")
        vl.updateExtents()
        vl.commitChanges()
        self.applyRenderer(vl,'polygon',zmin,symbols)
        return vl

    def buildLayeredContourLayer(self, polygons, asLayers=False):
        name = "%s"%self.uOutputName.text()
        zfield = self._zField
        vl = self.createVectorLayer("MultiPolygon", name, LAYERS,
                                   [('index',int),
                                    (zfield,float),
                                    ('label',str)
                                   ])
        pr = vl.dataProvider()
        fields = pr.fields()
        msg = list()
        symbols=[]
        for i, level_min, level_max, polygon in polygons:
            levels = self.formatLevel(level)+self.uLabelUnits.text()
            try:
                feat = QgsFeature(fields)
                try:
                    feat.setGeometry(QgsGeometry.fromWkt(MultiPolygon(polygon).to_wkt()))
                except:
                    continue
                feat['index']=i
                feat[zfield]=level_min
                feat['label']=levels
                pr.addFeatures( [ feat ] )
                symbols.append([level_min,levels])
            except:
                self.message(unicode(sys.exc_info()[1]))
                msg.append(levels)
        if len(msg) > 0:
            self.message("Levels not represented : "+", ".join(msg),"Layered Contour issue")
        vl.updateExtents()
        vl.commitChanges()
        self.applyRenderer(vl,'polygon',zfield,symbols)
        return vl

    def applyRenderer( self, layer, type, zfield, zlevels ):
        if not self.uApplyColors.isChecked():
            return
        ramp=self.uColorRamp.currentColorRamp()
        reversed=self.uReverseRamp.isChecked()
        if ramp is None:
            return
        nLevels=len(zlevels)
        if nLevels < 2:
            return
        renderer=QgsCategorizedSymbolRendererV2('index')
        for i, level in enumerate(zlevels):
            value,label=level
            rampvalue=float(i)/(nLevels-1)
            if reversed:
                rampvalue=1.0-rampvalue
            color=ramp.color(rampvalue)
            symbol=None
            if type=='line':
                symbol=QgsLineSymbolV2.createSimple({})
            else:
                symbol=QgsFillSymbolV2.createSimple({'outline_style':'no'})
            symbol.setColor(color)
            category=QgsRendererCategoryV2(i,symbol,label)
            renderer.addCategory(category)
        layer.setRendererV2(renderer)

    def colorRampToString( self, ramp ):
        if ramp is None:
            return '';
        d=QDomDocument()
        d.appendChild(QgsSymbolLayerV2Utils.saveColorRamp('ramp',ramp,d))
        rampdef=d.toString()
        return rampdef

    def stringToColorRamp( self, rampdef ):
        try:
            if '<' not in rampdef:
                return None
            d=QDomDocument()
            d.setContent(rampdef)
            return QgsSymbolLayerV2Utils.loadColorRamp( d.documentElement() )
        except:
            return None

    def saveSettings( self ):
        settings=QSettings()
        base='/plugins/contour/'
        mode=(LAYERS if self.uLayerContours.isChecked() else
              BOTH if self.uBoth.isChecked() else
              FILLED if self.uFilledContours.isChecked() else
              LINES)
        settings.setValue(base+'mode',mode)
        settings.setValue(base+'levels',str(self.uLevelsNumber.value()))
        settings.setValue(base+'extend',self.uExtend.itemText(self.uExtend.currentIndex()))
        settings.setValue(base+'method',self.uMethod.itemText(self.uMethod.currentIndex()))
        settings.setValue(base+'precision',str(self.uPrecision.value()))
        settings.setValue(base+'trimZeroes','yes' if self.uTrimZeroes.isChecked() else 'no')
        settings.setValue(base+'units',self.uLabelUnits.text())
        settings.setValue(base+'applyColors','yes' if self.uApplyColors.isChecked() else 'no')
        settings.setValue(base+'ramp',self.colorRampToString(self.uColorRamp.currentColorRamp()))
        settings.setValue(base+'reverseRamp','yes' if self.uReverseRamp.isChecked() else 'no')

    def loadSettings( self ):
        settings=QSettings()
        base='/plugins/contour/'
        try:
            mode=settings.value(base+'mode')
            if mode==LAYERS and self.uLayerContours.isVisible():
                self.uLayerContours.setChecked(True)
            elif mode==BOTH:
                self.uBoth.setChecked(True)
            elif mode==FILLED:
                self.uFilledContours.setChecked(True)
            else:
                self.uLinesContours.setChecked(True)

            levels=settings.value(base+'levels')
            if levels is not None and levels.isdigit():
                self.uLevelsNumber.setValue(int(levels))

            extend=settings.value(base+'extend')
            index = self.uExtend.findText(extend)
            if index >= 0:
                self.uExtend.setCurrentIndex(index)

            method=settings.value(base+'method')
            index = self.uMethod.findText(method)
            if index >= 0:
                self.uMethod.setCurrentIndex(index)

            precision=settings.value(base+'precision')
            if precision is not None and precision.isdigit():
                ndp=int(precision)
                self.uPrecision.setValue(ndp)
                self.uMinContour.setDecimals( ndp )
                self.uMaxContour.setDecimals( ndp )

            units=settings.value(base+'units')
            if units is not None:
                self.uLabelUnits.setText(units)

            applyColors=settings.value(base+'applyColors')
            self.uApplyColors.setChecked(applyColors=='yes')

            ramp=settings.value(base+'ramp')
            ramp=self.stringToColorRamp(ramp)
            if ramp:
                self.uColorRamp.setSourceColorRamp(ramp)

            reverseRamp=settings.value(base+'reverseRamp')
            self.uReverseRamp.setChecked(reverseRamp=='yes')

            trimZeroes=settings.value(base+'trimZeroes')
            self.uTrimZeroes.setChecked(trimZeroes=='yes')
        except:
            pass
