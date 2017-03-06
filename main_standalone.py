from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis import core
from qgis.gui import *
import netCDF4
from ui_user_interface import Ui_ExplorerWindow
from ui_user_interface_dialogs import *
from Loader import *
from osgeo import gdal
import gdal
import numpy as np
import cPickle,os
from gdalconst import *
from osgeo import osr
from math import ceil
#from Class_Legend import *
from Maptool_extension import *
from MetaSearch.dialogs.maindialog import MetaSearchDialog
from MetaSearch.dialogs.newconnectiondialog import NewConnectionDialog
from MetaSearch.dialogs.manageconnectionsdialog import ManageConnectionsDialog
from Class_Legend import  *
from GDALParameters import GDALParameters
from Reader import read_netcdf_variable,array_to_raster,read_lightout
from Grid import Grid
from VectorFieldRenderer import VectorFieldRenderer
from VectorArrowMarker import VectorArrowMarker
from rasparenzadialog import rasparenzaDialog
from contour import ContourDialog
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
#from shapely.geometry import MultiLineString, MultiPolygon
from VectorScaleBox import VectorScaleBox
from VectorScaleBoxPluginLayer import VectorScaleBoxPluginLayer
#from ThreddsViewer.ThreddsViewer import ThreddsViewer
from THREDDSExplorer.Thredds_explorer import THREDDSViewer
print 'OK thredds'
## Mercator Main Qgis Standalone Application
## C.REGNIER November 2015

## Creation of MainWindow
class Mercator_Explorer(QMainWindow,Ui_ExplorerWindow):
    def __init__(self,is_standalone):
        QMainWindow.__init__(self)
        self.setWindowTitle("Mercator Explorer")
        if is_standalone :
            self.ll_standalone=True
        else :
            self.ll_standalone=False
        print self.ll_standalone
        self.debug=0
        self.resize(1600, 800)
        self.setupUi(self)
        self.layers = []
        self.canvas = QgsMapCanvas()
        self.canvas.useImageToRender(False)
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.enableAntiAliasing(True)
        self.canvas.setObjectName("PyQGIS viewer")
        self.canvas.show()
        layout = QVBoxLayout()
        self.homepath=os.getcwd()
        ## Setup workdir with a dialob box
        workdialog=DefWorkdir()
        workdialog.show()
        if workdialog.exec_() == QDialog.Accepted:
            print "OK1"
            self.tmp_path = str(workdialog.work_field.text())
        else :
            print 'Workdir not define'
            return
        ## Set proxy params if exist
        params_file=filename = [self.homepath+"/statics/params.cfg"]
        print params_file
        param_dict=Loader.factory('NML').load(params_file)
        self.proxyserver=str(param_dict.get('proxy','proxy_adress'))
        self.proxyuser=str(param_dict.get('proxy','proxy_user'))
        self.proxypass=str(param_dict.get('proxy','proxy_pass'))
        self.cmemsuser=str(param_dict.get('cmems_server','user_cmems'))
        self.cmemspass=str(param_dict.get('cmems_server','pass_cmems'))
        ## Get sections
        dict_list_sect=self.get_allsect_withreg(str(self.homepath)+"/statics/Def_section.p")
        for key in dict_list_sect.keys():
            print key
            ## Add region item non selectionnable
            item=QtGui.QStandardItem(key)
            item.setForeground(QtGui.QColor('red'))
            #font = QtGui.QFont("Times",20,QtGui.QFont.Bold,True)
            font = item.font()
            font.setPointSize(10)
            font.setBold(True) 
            item.setFont(font)
            item.setSelectable(False)
            model = self.secVars.model()
            ## Add selectionnable item
            model.appendRow(item)
            for section in dict_list_sect[key]:
                self.secVars.addItem(section[0])
        ## Connect the actions
        self.connect(self.secVars, SIGNAL("currentIndexChanged(QString)"),self.drawSection)
        self.connect(self.actionQuit,SIGNAL("triggered()"), qApp.quit)
        self.connect(self.actionZoomIn, SIGNAL("triggered()"), self.zoomIn)
        self.connect(self.actionZoomOut, SIGNAL("triggered()"), self.zoomOut)
        self.connect(self.actionPan, SIGNAL("triggered()"), self.pan)
        self.connect(self.actionSelect, SIGNAL("triggered()"), self.selectfeature)
        self.connect(self.actionZoomFull, SIGNAL("triggered()"), self.zoomFull)
        self.connect(self.actionAddRaster, SIGNAL("triggered()"), self.addRaster)
        self.connect(self.actionAddVector, SIGNAL("triggered()"), self.addVector)
        self.connect(self.actionAddGeojson, SIGNAL("triggered()"), self.AddGeojson)
        self.connect(self.actionReadLightout, SIGNAL("triggered()"), self.ReadLightout)
        self.connect(self.actionReadhdf, SIGNAL("triggered()"), self.ReadHdf)
        self.connect(self.actionComputeDiff, SIGNAL("triggered()"), self.ComputeDiff)
        self.connect(self.cboDim, SIGNAL("currentIndexChanged(QString)"), self.updateDims)
        self.connect(self.cboVars, SIGNAL("currentIndexChanged(QString)"), self.updateVariable)
        self.connect(self.cboNbcolor, SIGNAL("valueChanged(int)"),self.drawLayer)
        self.connect(self.combocolor,SIGNAL("currentIndexChanged(int)"),self.drawLayer) 
        self.connect(self.basemap, SIGNAL("clicked()"),self.on_basemap_triggered)
        self.connect(self.proj, SIGNAL("clicked()"),self.on_proj_triggered)
        self.connect(self.actionAddWmsLayer,SIGNAL("triggered()"), self.metaSearch)
        self.connect(self.actionPlotCurrent,SIGNAL("triggered()"), self.init_PlotCurrent)
        self.connect(self.actionAddGridd,SIGNAL("triggered()"), self.init_PlotGrid)
        self.connect(self.actionRescaling, SIGNAL("triggered()"),self.drawLayer)
        self.connect(self.invpal, SIGNAL("stateChanged(int)"),self.drawLayer)
        self.connect(self.actionTransparency, SIGNAL("triggered()"),self.setTransparency)
        self.connect(self.actionContouring, SIGNAL("triggered()"),self.init_PlotContour)
        self.connect(self.Valmaxvalue,SIGNAL("returnPressed ()"),self.drawLayer)
        self.connect(self.Valminvalue,SIGNAL("returnPressed ()"),self.drawLayer)
#        self.connect(self.actionSaveMap, SIGNAL("triggered()"), self.saveMap)
        self.connect(self.actionPlotProfile,SIGNAL("triggered()"), self.getProfile)
        self.connect(self.actionGetValue, SIGNAL("triggered()"), self.getValue)
        self.connect(self.actionDistance, SIGNAL("triggered()"), self.getDistance)
        self.connect(self.actionCapture, SIGNAL("triggered()"), self.getLines)
        self.connect(self.actionReadOla, SIGNAL("triggered()"), self.ReadOlaFile)
        self.connect(self.actionExplore, SIGNAL("triggered()"), self.SetExploreMode)
        #self.connect(self.actionReadCmemsCatalog, SIGNAL("triggered()"), self.ReadCmemsCatalog)
        self.connect(self.actionPlotsection, SIGNAL("triggered()"), self.PlotSection)
        self.connect(self.actionThreddsViewer, SIGNAL("triggered()"), self.ThreddsViewer)
        self.connect(self.canvas, SIGNAL( "xyCoordinates(const QgsPoint&)" ),self.updateXY )
        # self.connect(self.canvas, SIGNAL("moved"),self.move_xy)
        #self.connect(self.canvas, SIGNAL("xyCoordinates(const QgsPoint&)"),self.move_xy )
        self.compose=1
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.centralWidget.setLayout(layout)
        ## Add Legend to the layer
        self.addLegendtoLayer()
        ## Add tool pan
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        ## Add tool select
        self.selectTool=SelectTool(self.canvas)
        self.selectTool.setAction(self.actionSelect)

        self.toolZoomIn = QgsMapToolZoom(self.canvas,False) # false = in
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolZoomOut.setAction(self.actionZoomOut)
        # Init memory Layers
        #self.setupMapLayers()
    
    def ThreddsViewer(self): 
	print "Launch threddsViewer"
        canvas=self.canvas
        print type(canvas)
        install_dir=os.getcwd()
	print install_dir
        #thredds = THREDDSViewer(self,install_dir)
        thredds = THREDDSViewer(self,canvas)
	print "Launch threddsViewer show"
      #  self.canvas.mainWindow().addDockWidget(Qt.LeftDockWidgetArea,thredds)
        #self.addDockWidget(Qt.RightDockWidgetArea,thredds)
       # thredds=THREDDSViewer(self)
        thredds.show()
	print "Launch show ok"
    def ReadLightout(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                  self.tr("Lightout file in binary format ( * )"));
        if fileName is not None:
            print "Read Allege"
            ALLEGE=read_lightout(str(fileName))
            print type(ALLEGE)
            print np.nanmax(ALLEGE)
            print np.nanmin(ALLEGE)
            nz,nlat,nlon=np.shape(ALLEGE)
            print nz,nlat,nlon
            var_array_nan=np.ma.filled(ALLEGE[0,:,:],np.nan)
            var_array_nan=np.where(var_array_nan == 0 ,np.nan,var_array_nan)
            if nlat == 1019 and nlon == 1440 :
                print "Cas PSY4"
                ## Open static
                static_file="/sortref/systeme/psy4/PSY4V2/PSY4V2_common_files/ORCA12-T321.mask.nc" 
                ## Read Ola position
                nc_file=netCDF4.Dataset(str(static_file),'r')
                lon = nc_file.variables['nav_lon'][:,:]
                lat = nc_file.variables['nav_lat'][:,:]
                x_min = np.nanmin(lon)
                x_max = np.nanmax(lon)
                y_min = np.nanmin(lat)
                y_max = np.nanmax(lat)
                topleft_corner = (x_min, y_max)    
                #topleft_corner = (x_max, y_min)    
                #topleft_corner = (x_max, y_min)    
                dx = x_max - x_min
                dy = y_max - y_min
                print dx,dy
                x_pixels=nlon
                y_pixels=nlat
                cellsize_long = dx / x_pixels
                cellsize_lat = cellsize_long # dy / y_pixels
                cellsize_lat = dy / y_pixels
                print  cellsize_long, cellsize_lat
                cell_sizes = (cellsize_long, cellsize_lat)
                ligthout_filename='lightout.tiff'
                noDataValue=np.nan
                print np.nanmax(var_array_nan)
                print np.nanmin(var_array_nan)
                array_to_raster(np.flipud(var_array_nan), cell_sizes, topleft_corner,noDataValue,self.tmp_path+ligthout_filename)
                file2=os.path.basename(str(fileName))
                raster_lyr_lightout=QgsRasterLayer(self.tmp_path+ligthout_filename,"Lightout_"+str(file2))
                print "Add layer to registry ok"
                QgsMapLayerRegistry.instance().addMapLayer(raster_lyr_lightout)
                band=1
                self.addLayer(raster_lyr_lightout,band)
                self.compose=1
                ## Enabled group palette
                self.GroupBoxPal.setEnabled(True)

    def get_allsect_withreg(self,filename):
        list_sect=[]
        #f = file(filename, 'r')
        f = open(filename, 'rb')
        var=cPickle.load(f)
        self.file_sect=var
        return var

    def get_allsect(self,filename):
        list_sect=[]
        #f = file(filename, 'r')
        f = open(filename, 'rb')
        var=cPickle.load(f)
        self.file_sect=var
        for item,variable in var.items():
            for def_region in variable :
                name=def_region[0]
                list_sect.append(name)
        return list_sect

    def SetExploreMode(self):
        print "SetExploreMode"
        #self.pan.setChecked(True)
        self.actionExplore.setChecked(True)
        self.canvas.setMapTool(self.exploreTool)
    def ReadCmemsCatalog(self): 
        print "ReadCmemsCatalog"
        Cmemsdialog=CmemsProductDialog(self)
        Cmemsdialog.show()
        if Cmemsdialog.exec_() == QDialog.Accepted:
            print "OK"
        ##elif Cmemsdialog.exec_() == QDialog.Rejected:
        ##   print "Close window"
        ##   Cmemsdialog.close()
    def PlotSection(self):

        """ Define a section and plot it """

        Sectiondialog=SectionParams()
        Sectiondialog.show()
        if Sectiondialog.exec_() == QDialog.Accepted:
            lon_min=float(Sectiondialog.minlon_fieldgrid.text())
            lon_max=float(Sectiondialog.maxlon_fieldgrid.text())
            lat_min=float(Sectiondialog.minlat_fieldgrid.text())
            lat_max=float(Sectiondialog.maxlat_fieldgrid.text())
            point1=QgsPoint(lon_min,lat_min)
            point2=QgsPoint(lon_max,lat_max)
            list_points=[]
            list_points.append(point1)
            list_points.append(point2)
            cmin=float(Sectiondialog.cmin_fieldgrid.text())
            cmax=float(Sectiondialog.cmax_fieldgrid.text())
            step=float(Sectiondialog.step_fieldgrid.text())
            section_name=str(Sectiondialog.namesection_fieldgrid.text())
            prof_min=float(Sectiondialog.profmin_fieldgrid.text())
            prof_max=float(Sectiondialog.profmax_fieldgrid.text())
            print "section name %s "%(section_name)
            list_prof=[]
            list_prof.extend([prof_min,prof_max])
            list_var=[]
            list_var.extend([cmin,cmax,step,prof_min,prof_max])
            self.LineLayer = QgsVectorLayer("LineString?crs=EPSG:4326",section_name,"memory")
            self.setupRendererLineLayer()
            self.selectLines=CaptureTool(self.canvas,self.LineLayer,self,self.onGeomAdded,1)
            self.selectLines.geometryCaptured(list_points,section_name,list_var,list_prof)
            #self.selectLines.geometryCaptured(list_points,section_name,list_var)

    def ReadOlaFile(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                     self.tr("Ola in netcdf (*.nc *.NC )"));
        if fileName is not None:
            oladialog=OlaParams()
            oladialog.show()
            if oladialog.exec_() == QDialog.Accepted:
                self.prof_min = float(oladialog.minprof_fieldgrid.text())
                self.prof_max = float(oladialog.maxprof_fieldgrid.text())
                print "prof min max : %f %f  " %(self.prof_min,self.prof_max)
            ## Find dimensions and variables
            filevar=os.path.basename(str(fileName))
            echeance=filevar.split('_')[3]
            date_var1=filevar.split('_')[6]
            date_var2=filevar.split('_')[7]
            filename_layer_t="OLA_TEMP_prof_"+str(echeance)+"_"+date_var1+"_"+date_var2+"_"+str(self.prof_min)+"_"+str(self.prof_max)
            filename_layer_s="OLA_PSAL_prof_"+str(echeance)+"_"+date_var1+"_"+date_var2+"_"+str(self.prof_min)+"_"+str(self.prof_max) 
            #self.OlaPointLayer = QgsVectorLayer("Point?crs=EPSG:4326&field=time:double&field=name:string(255)&field=Value_id:integer&index=yes",\
            #					"OLA_point_layer", "memory")
            #self.OlaPointLayer = QgsVectorLayer("Point?crs=EPSG:4326&field=time:double&field=duid:string(255) &\
            self.OlaPointLayer_temp = QgsVectorLayer("Point?crs=EPSG:4326",filename_layer_t, "memory")
            self.OlaPointLayer_psal = QgsVectorLayer("Point?crs=EPSG:4326",filename_layer_s, "memory")
            #                                    field=name:string(255)& index=yes","OLA_point_layer", "memory")
            #self.OlaPointLayer = QgsVectorLayer("Point?crs=EPSG:4326&field=time:double & index=yes","OLA_point_layer", "memory")
            ## Setup renderer layer
            self.setupRendererPointLayer(self.OlaPointLayer_temp,1,"blue")
            self.setupRendererPointLayer(self.OlaPointLayer_psal,0.5,"green")
            ## Define QgsFields
            vpr_1 =self.OlaPointLayer_temp.dataProvider()
            vpr_2 =self.OlaPointLayer_psal.dataProvider()
            qd = QVariant.Double
            qi =  QVariant.Int
            qs=  QVariant.String
            ## Create Attributes fields
            vpr_1.addAttributes([QgsField ("id", QVariant.UInt), QgsField ("Value_id",qi), QgsField("time", qd),QgsField("name", qs),QgsField("profile", qi)])
            self.OlaPointLayer_temp.updateFields()
            vpr_2.addAttributes([QgsField ("id", QVariant.UInt), QgsField ("Value_id",qi), QgsField("time", qd),QgsField("name", qs),QgsField("profile", qi)])
            self.OlaPointLayer_psal.updateFields()
            ## Read Ola position
            nc_file=netCDF4.Dataset(str(fileName),'r')
            lon = nc_file.variables['longitude_VP'][:]
            lat = nc_file.variables['latitude_VP'][:]
            time_VP = nc_file.variables['time_VP'][:]
            duid_prof = nc_file.variables['duid'][:]
            prof_VP=nc_file.variables['depth'][:,:]
            temp_var=nc_file.variables['TEMP'][:,:]
            psal_var=nc_file.variables['PSAL'][:,:]
            if  echeance == 'FCST' : 
                temp_mod=nc_file.variables['first_frcst_temp'][:,:]
                psal_mod=nc_file.variables['first_frcst_psal'][:,:]
            elif  echeance == 'ANA' : 
                temp_mod=nc_file.variables['second_frcst_temp'][:,:]
                psal_mod=nc_file.variables['second_frcst_psal'][:,:]
            else : 
                print 'echeance not known %s '%(echeance)
            name_prof =  nc_file.variables['setid_VP'][:] 
            nb_points=len(lon) 
            print "Read OK"
            #self.OlaPointLayer.dataProvider().addAttributes([QgsField ("id", QVariant.UInt), QgsField ("NAME_ID",QVariant.UInt)])
           # self.OlaPointLayer.dataProvider().addAttributes([QgsField ("id", QVariant.UInt), QgsField ("NAME_ID",self.qd)])
           # self.OlaPointLayer.updateFields()
           # print "add Att ok"
            fields_1 = vpr_1.fields()
            fields_2 = vpr_2.fields()
            feature_list=[]
            feature_list2=[]
            charts={}
            #for pt in range(nb_points):
            #   id_file=int(duid_prof[pt])
            #   print "id %i" %(id_file)
            for pt in range(nb_points):
                x=float(lon[pt]) 
                y=float(lat[pt])
                point = QgsPoint (x,y) 
                #print '------------------------------'
                #print "x  y %f %f " %(x,y)
                ## open prof and var
                prof_val=prof_VP[pt,:]
                insitu_temp_val=temp_var[pt,:]
                insitu_psal_val=psal_var[pt,:]
                fcst_val_temp=temp_mod[pt,:]
                fcst_val_psal=psal_mod[pt,:]
                time_value=float(time_VP[pt])
                id_duid=int(duid_prof[pt])
                nb_prof=np.where(prof_val[:] != 0)
                ll_prof=False
                if len(fcst_val_temp[:]) > 0 and len(nb_prof[0]) > 0 :
                    ind_prof = np.where(prof_val[:] != 0)[0][-1]
                    if ind_prof == 0 : 
                        if ( float(-prof_val[ind_prof]) >=  float(self.prof_min) and float(-prof_val[ind_prof]) <=  float(self.prof_max)) :
                            ll_prof=True
                    else :
                        for prof in range(ind_prof): 
                            if ( float(-prof_val[prof]) >=  float(self.prof_min) and float(-prof_val[prof]) <=  float(self.prof_max)) :
                                ll_prof=True
                    if ll_prof : 
                        #print "Inside interval %f %f %f" %(val_prof,self.prof_min,self.prof_max)
                        mask_var_mod_temp=np.ma.masked_values(fcst_val_temp,9.96e36)
                        mask_var_prof=np.ma.masked_values(prof_val,0)
                        count_var_temp=mask_var_mod_temp.count()
                        count_prof=mask_var_prof.count()
                    else:
                        count_prof=0
                else :
                    count_prof=0
                if len(fcst_val_psal[:]) > 0 and len(nb_prof[0]) > 0 :
                    ind_prof = np.where(prof_val[:] != 0)[0][-1]
                    val_prof=-prof_val[ind_prof]
                    if ind_prof == 0 : 
                        if ( float(-prof_val[ind_prof]) >=  float(self.prof_min) and float(-prof_val[ind_prof]) <=  float(self.prof_max)) :
                            ll_prof=True
                    else :
                        for prof in range(ind_prof): 
                            if ( float(-prof_val[prof]) >=  float(self.prof_min) and float(-prof_val[prof]) <=  float(self.prof_max)) :
                                ll_prof=True
                    if ll_prof : 
                        mask_var_mod_psal=np.ma.masked_values(fcst_val_psal,9.96e36)
                        mask_var_prof=np.ma.masked_values(prof_val,0)
                        count_var_psal=mask_var_mod_psal.count()
                        count_prof=mask_var_prof.count()
                    else:
                        count_prof=0
                else : 
                    count_prof=0
                namevalue=str("".join(name_prof[pt]).strip()).split('.')[0]
                #print count_prof,count_var_temp,count_var_psal,ind_prof
                ## Populate feature for temp 
                if  count_prof > 0 and count_var_temp > 0 : #and ind_prof != 0 :
                    feature = QgsFeature(self.OlaPointLayer_temp.pendingFields())
                    # feature = QgsFeature()
                    feature.setGeometry(QgsGeometry.fromPoint(point))
                    feature.setFields(fields_1)
                    feature.setAttribute("time", time_value)
                    feature.setAttribute("Value_id",id_duid)
                    feature.setAttribute("name",'TEMP_'+namevalue)
                    feature.setAttribute("profile",pt)
                    feature_list.append(feature)
                ## Populate feature for psal 
                if  count_prof > 0 and count_var_psal > 0 :#and ind_prof != 0 :
                    feature2 = QgsFeature(self.OlaPointLayer_psal.pendingFields())
                    # feature = QgsFeature()
                    feature2.setGeometry(QgsGeometry.fromPoint(point))
                    feature2.setFields(fields_2)
                    feature2.setAttribute("time", time_value)
                    feature2.setAttribute("Value_id",id_duid)
                    feature2.setAttribute("name",'PSAL_'+namevalue)
                    feature2.setAttribute("profile",pt)
                    feature_list2.append(feature2)
             #print "OK %i %i" %(pt,nb_points)
             # print "----------------------"
            print "Add features"
            vpr_1.addFeatures(feature_list)
            self.OlaPointLayer_temp.updateExtents() 
            vpr_2.addFeatures(feature_list2)
            self.OlaPointLayer_psal.updateExtents() 
            print "Add layer to registry"
            QgsMapLayerRegistry.instance().addMapLayer(self.OlaPointLayer_temp)
            QgsMapLayerRegistry.instance().addMapLayer(self.OlaPointLayer_psal)
            self.exploreTool=ExploreTool(self.canvas,self.ll_standalone,fileName)#,prof_VP,temp_var,temp_mod)#,self.OlaPointLayer)
            self.exploreTool.setAction(self.actionExplore)
            self.actionExplore.setEnabled(True)
            self.GroupBoxPal.setEnabled(True) 
    def setupMapLayers(self):
        crs = QgsCoordinateReferenceSystem()
       # self.LineLayer = QgsVectorLayer('LineString?crs:%s' % crs,"LineLayer", "memory")
        self.LineLayer = QgsVectorLayer("LineString?crs=EPSG:4326","LineSection", "memory")
        #QgsMapLayerRegistry.instance().addMapLayer(self.LineLayer)
        #self.layers.append(QgsMapCanvasLayer(self.LineLayer)) 
        self.startPointLayer = QgsVectorLayer("Point?crs=EPSG:4326","Plot_Profile", "memory")
        #QgsMapLayerRegistry.instance().addMapLayer( self.startPointLayer)
        #self.layers.append(QgsMapCanvasLayer(self.startPointLayer)) 
        self.setupRendererLayer()

    def setupRendererLineLayer(self):
        root_rule = QgsRuleBasedRendererV2.Rule(None)
        symbol = QgsLineSymbolV2.createSimple({'color' : "black"})
        symbol.setWidth(0.5)
        rule = QgsRuleBasedRendererV2.Rule(symbol, elseRule=True)
        root_rule.appendChild(rule)
        renderer = QgsRuleBasedRendererV2(root_rule)
        self.LineLayer.setRendererV2(renderer)

    def setupRendererPointLayer(self,layer,size,color):
        symbol = QgsMarkerSymbolV2.createSimple({'color' : color})
        symbol.setSize(size)
        symbol.setAlpha(0.5)
        symbol.setOutputUnit(QgsSymbolV2.MapUnit)
        renderer = QgsSingleSymbolRendererV2(symbol)
        layer.setRendererV2(renderer)

    def setupRendererLayer(self):
        root_rule = QgsRuleBasedRendererV2.Rule(None)
        symbol = QgsLineSymbolV2.createSimple({'color' : "black"})
        rule = QgsRuleBasedRendererV2.Rule(symbol, elseRule=True)
        root_rule.appendChild(rule)
        renderer = QgsRuleBasedRendererV2(root_rule)
        self.LineLayer.setRendererV2(renderer)
        symbol = QgsMarkerSymbolV2.createSimple({'color' : "green"})
        symbol.setSize(2)
        symbol.setOutputUnit(QgsSymbolV2.MapUnit)
        renderer = QgsSingleSymbolRendererV2(symbol)
        self.startPointLayer.setRendererV2(renderer)

    def ReadHdf(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                     self.tr("Hdf Files (*.hdf *.hdf4 *.hdf5 *.HDF)"));
        if fileName is not None:
            ## Find dimensions and variables
            self.updateFileHDF(fileName)
            self.GroupBoxPal.setEnabled(True) 
    def updateFileHDF(self,filename):
        print filename
        hdf_file = gdal.Open(filename)
        print "Read HDF file"
        subDatasets = hdf_file.GetSubDatasets()
        print subDatasets

    def ComputeDiff(self):
        self.actionRescaling.setEnabled(True)
        self.GroupBoxPal.setEnabled(True) 
        self.Valminvalue.setText("")
        self.Valmaxvalue.setText("")
        try :
            self.dialog_comp=ComputeDiffDialog(self)
            self.dialog_comp.exec_()
##        if self.dialog_comp.exec_() == QDialog.Accepted:
        except :
            QMessageBox.warning(self.canvas, "Compute Diff Error",unicode(sys.exc_info()[1]))

    def selectfeature(self):
        print "inside selectfeature"
        self.actionPan.setChecked(False)
        self.actionSelect.setChecked(True)
        print "Select"
        self.canvas.setMapTool(self.selectTool)
        self.canvas.setMapTool(self.distanceTool)

        print "OK"

    def setContouring(self,resolution):
        ### First step Compute grid
        spacing = resolution
        inset = .1
        self.rasterlayer=self.view.currentLayer()
        if self.rasterlayer : 
            self.rldp = self.rasterlayer.dataProvider()
        else: 
            print "Layer not selected!"
            return
        crs = QgsCoordinateReferenceSystem()
        self.extentLayer = self.rasterlayer.extent()
        self.vector_lyr = QgsVectorLayer ('Point?crs:%s' %crs, 'Contour_resol'+str(resolution), "memory")
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
        print "compute points"
        for x, y in self.pts:
            self.f = QgsFeature(self.vector_lyr.pendingFields())
            self.p = QgsPoint (x,y)
            self.qry = self.rasterlayer.dataProvider().identify (self.p, QgsRaster.IdentifyFormatValue)
            self.r = self.qry.results()
            self.f.setAttribute (0, self.r[1])
            self.f.setGeometry (QgsGeometry.fromPoint(self.p))
            self.feats.append(self.f)
        print "compute points OK"
        self.vpr.addFeatures(self.feats)
        self.vector_lyr.updateExtents()
        QgsMapLayerRegistry.instance().addMapLayer(self.vector_lyr)
        try :
            dlg = ContourDialog(self.vector_lyr,self.canvas,self.ll_standalone)
            dlg.exec_()
        except ContourError:
            QMessageBox.warning(self.canvas, "Contour error",unicode(sys.exc_info()[1]))

    def setTransparency(self) :
        self.dlg=rasparenzaDialog()
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # do something useful (delete the line containing pass and
            # substitute with your code)
            rasterSlider = self.dlg.findChild(QSlider, "horizontalSlider")
            valore = float(rasterSlider.value())
            valoi  = rasterSlider.value()
            valoi255 = (valoi) * 255. / 100.
            valoi255 = 255. - (valoi255) 
            valo   = (100. - valore) / 100.
            for iLayer in range(self.canvas.layerCount()):
                layer = self.canvas.layer(iLayer)
                if layer.type() == layer.RasterLayer:
                    if QGis.QGIS_VERSION_INT < 10900:                 
                        layer.setTransparency(int(valoi255))
                    else:
                        layer.renderer().setOpacity(valo)
            self.canvas.refresh()
 
    def getProfile(self):
        self.startPointLayer = QgsVectorLayer("Point?crs=EPSG:4326","Plot_Profile", "memory")
        self.setupRendererPointLayer(self.startPointLayer,0.2,"transparent")
        currentLayer=self.view.currentLayer()
        if currentLayer: 
            self.getprofile=SelectVertexTool(self.canvas,self.startPointLayer,currentLayer,self,self.onStartPointSelected)
            self.getprofile.setAction(self.actionPlotProfile)
            self.canvas.setMapTool(self.getprofile)
            result=1    
        else: 
            print "Layer not selected!"
            return
    
    def getValue(self):
        print "inside getValue"
        self.canvas.setMapTool(self.getvalue)
        result=1
    def getDistance(self):
        self.canvas.setMapTool(self.selectTool)
        result=1
    def getLines(self):
        print "getLines"
        self.LineLayer = QgsVectorLayer("LineString?crs=EPSG:4326","LineSection", "memory")
        print "create LineLayer"
        self.setupRendererLineLayer()
        print "getLines 1"
        self.selectLines=CaptureTool(self.canvas,self.LineLayer,self,self.onGeomAdded,1)
        print "getLines "
        self.selectLines.setAction(self.actionCapture)
        self.canvas.setMapTool(self.selectLines)
        print "========================"     
        result=1  

    def move_xy(self,p):
        x = p.x()
        y = p.y()
        extent = self.canvas.extent()
        width = round(extent.width() / self.canvas.mapUnitsPerPixel());
        height = round(extent.height() / self.canvas.mapUnitsPerPixel());
        position=self.canvas.getCoordinateTransform().toMapCoordinates(x,y)
        #print position
        #print extent
        #print width 
        #print height
        if position is not None:
            ident =self.view.currentLayer().dataProvider().identify(position, QgsRaster.IdentifyFormatValue,extent, width, height ).results()
            iband=1
            if not ident or not ident.has_key( iband ): # should not happen
                bandvalue = "?"
            else:
                #print  bandvalue
                if  self.ll_standalone : 
                    bandvalue = ident[iband].toPyObject()
                else : 
                    bandvalue = ident[iband]
                #print 'bandvalue',str(bandvalue)
                #print eval( str( bandvalue.toString() ) )
                if bandvalue is None:
                    bandvalue = "no data"
        self.valueXY.setText(str( bandvalue))

    def updateXY( self, p ):
        x = p.x()
        y = p.y()
        self.lblXY.setText("Lon : " + str(x) + " Lat : " + str(y) )

    def PlotGrid(self,resolution):
        #xmin,ymin,xmax,ymax = self.view.currentLayer().extent().toRectF().getCoords()
        xmin=-180
        ymin=-80
        xmax=180
        ymax =90
        res=int(resolution)
        gridWidth = res
        gridHeight = res
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

    def init_PlotCurrent(self):
        dialog=VectorDialog()
        dialog.show()
        if dialog.exec_() == QDialog.Accepted:
            resolution = float(dialog.resol_field.text())
            print "resolution %f " %(resolution)
            scale=float(dialog.scale_field.text())
            print "scale %f " %(scale)
            rcolor=int(dialog.color_rfield.text())
            gcolor=int(dialog.color_gfield.text())
            bcolor=int(dialog.color_bfield.text())
            u_current=str(dialog.zonalspeed_field.text())
            v_current=str(dialog.meridianspeed_field.text())
            print "color %i,%i,%i " %(rcolor,gcolor,bcolor)
            self.PlotCurrent(resolution,scale,rcolor,gcolor,bcolor,u_current,v_current)

    def init_PlotContour(self):
        print "init_PlotContour"
        cdialog=ContourDialogParams()
        cdialog.show()
        print "init_PlotContour"
        if cdialog.exec_() == QDialog.Accepted:
            resolution = float(cdialog.resol_cfield.text())
            print "Resolution %f " %(resolution)
            self.setContouring(resolution)

    def init_PlotGrid(self):
        print "init_PlotGrid"
        cdialog=GridDialogParams()
        cdialog.show()
        if cdialog.exec_() == QDialog.Accepted:
            resolution = float(cdialog.resol_cfieldgrid.text())
            print "Resolution %f " %(resolution)
            self.PlotGrid(resolution)

    def PlotCurrent(self,resolution,scale,rcolor,gcolor,bcolor,u_vel,v_vel):
        netcdf_datafile=str(self.filename)
        # Read variable from netcdf file
        dim_val=self.cboDim.currentText()
        band=int(dim_val)
        u_varname=str(u_vel)
        v_varname=str(v_vel)
        ds_in = gdal.Open(netcdf_datafile)  
        metadata = ds_in.GetMetadata()  
        x_min = float(metadata['NC_GLOBAL#longitude_min'])
        x_max = float(metadata['NC_GLOBAL#longitude_max'])
        y_min = float(metadata['NC_GLOBAL#latitude_min'])
        y_max = float(metadata['NC_GLOBAL#latitude_max'])
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
        nc=netCDF4.Dataset(netcdf_datafile,'r')
        u_array_2=nc.variables[u_varname][0,band-1,:,:]
        v_array_2=nc.variables[v_varname][0,band-1,:,:]
        vector_array = np.ma.zeros((u_raster_params.get_rows(), u_raster_params.get_cols(), 2))
        vector_array[:,:,:]=np.nan
        vector_array[:,:,0], vector_array[:,:,1] = np.flipud(u_array_2),np.flipud(v_array_2)
        vector_field = Grid(u_raster_params, vector_array)  
        magnitude_field_array = vector_field.magnitude().get_grid_data()
        orientation_field_array = vector_field.orientations().get_grid_data()
        filepath=self.tmp_path
        magnitude_filename='magnitude_'+str(band)+'.tiff'
        noDataValue=np.nan
        array_to_raster(magnitude_field_array, cell_sizes, topleft_corner,noDataValue,filepath+magnitude_filename)
        orientation_filename='orientation_'+str(band)+'.tiff'
        array_to_raster(orientation_field_array, cell_sizes, topleft_corner,noDataValue,filepath+orientation_filename)
        ## Create raster layer for magnitude and orientation 
        spacing = resolution
        #spacing = 1.
        inset = .05
        raster_lyr_magn=QgsRasterLayer(filepath+magnitude_filename,"magnitude_band_"+str(band))
       # raster_lyr_magn=QgsRasterLayer(filepath+magnitude_filename,"magnitude")
        raster_lyr_magn.isValid()
        raster_lyr_orient=QgsRasterLayer(filepath+orientation_filename,"orientation_"+str(band))
        #raster_lyr_orient=QgsRasterLayer(filepath+orientation_filename,"orientation")
        raster_lyr_orient.isValid()
        rprm = raster_lyr_magn.dataProvider()
        crs = QgsCoordinateReferenceSystem()
        ext_magn = raster_lyr_magn.extent()
        rpro = raster_lyr_orient.dataProvider()
        crs = QgsCoordinateReferenceSystem()
        ext_orient = raster_lyr_orient.extent()
        ## Add Grid layer 
        vector_lyr = QgsVectorLayer ('Point?crs:%s' % crs, 'Vector_layer_resol_'+str(resolution), "memory")
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
        print 'add Layer to registry'
        #QgsMapLayerRegistry.instance().addMapLayer(raster_lyr_orient)
        #self.addLayer(raster_lyr_orient,band)
        pts = [(x,y) for x in (i for i in np.arange (xmin_orient, xmax_orient, spacing)) for y in (j for j in np.arange (ymin_orient, ymax_orient, spacing))]
        ## Population Grid layer with amp and rot values
        for x, y in pts:
            f = QgsFeature(vector_lyr.pendingFields())
            p = QgsPoint (x,y)
            qry_o = rpro.identify (p, QgsRaster.IdentifyFormatValue)
            qry_m = rprm.identify (p, QgsRaster.IdentifyFormatValue)
            r_o = qry_o.results()
            r_m = qry_m.results()
            if  self.ll_standalone :
                f.setAttribute (0, r_o [1].toPyObject())
                f.setAttribute (1, r_m [1].toPyObject())
            else :
                f.setAttribute (0, r_o [1])
                f.setAttribute (1, r_m [1])
            f.setGeometry (QgsGeometry.fromPoint(p))
            feats.append(f)
        ## pass the point values to the data provider of points layer
        vpr.addFeatures(feats)
        ## Update layer extend 
        vector_lyr.updateExtents()
        ## Creation of vectorfieldRenderer
        r = VectorFieldRenderer(self.ll_standalone)
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
        arrow.setBaseFillColor(QColor.fromRgb(rcolor,gcolor,bcolor))
        arrow.setBaseBorderColor(QColor.fromRgb(rcolor,gcolor,bcolor))
        arrow.setFillBase(True)

        # Configure the arrow - setColor applies to the shaft and outline of the arrow head.
        #arrow.setColor(QColor.fromRgb(0,0,0))
        arrow.setColor(QColor.fromRgb(rcolor,gcolor,bcolor))
        arrow.setShaftWidth(0.7)
        arrow.setRelativeHeadSize(0.3)
        arrow.setMaxHeadSize(3.0)
        arrow.setHeadShape(0.0,-1.0,-0.7)
        arrow.setHeadWidth(0.0)
        arrow.setHeadFillColor(QColor.fromRgb(rcolor,gcolor,bcolor))
        arrow.setFillHead(True)

        ## ADD Vector scale box
        self._scaleBox = VectorScaleBox(self.canvas)
        l = VectorScaleBoxPluginLayer()
        l.setScaleBox( self._scaleBox )
        QgsMapLayerRegistry.instance().addMapLayer(l)
        l.repaintScaleBox() 
        # Set other symbology properties
        r.setScale(scale)
        r.setUseMapUnit(False)

        r.setScaleGroup('def')
        r.setScaleGroupFactor(1.0)

        r.setScaleGroup('deformation')
        r.setLegendText(' horizontal')
        r.setScaleBoxText(' hor (95% conf lim)')
        r.setShowInScaleBox(True)
        print "Scale box"
        # Assign the renderer to the layer and refresh the symbology
        # Not sure whether clearing the image cache is necessary, should be 
        # done by QGis on setting the renderer
        vector_lyr.setRendererV2(r)
        vector_lyr.triggerRepaint()
        QgsMapLayerRegistry.instance().addMapLayer(vector_lyr)
        self.addLayer(vector_lyr,band)
        ## 
    def zoomIn(self):
        self.canvas.setMapTool(self.toolZoomIn)
        self.actionRescaling.setEnabled(True)
    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)
    def zoomFull(self):
        self.canvas.zoomToFullExtent()
        self.actionRescaling.setEnabled(False)
        self.drawLayer()
    def pan(self):
        self.canvas.setMapTool(self.toolPan)
    def drawSection(self):
        section_name=self.secVars.currentText()
        print "section name %s "%(section_name)
        ## Find coords of section
        list_x0,list_y0,tmin,tmax,smin,smax, \
              tstep,sstep,flag=self.get_coords(self.file_sect,str(section_name))
        print list_x0,list_y0
        list_var=[]
        variable=self.cboVars.currentText()
        if "salinity" in variable:
            list_var.extend([smin,smax,sstep])
        if "temperature" in variable:
            list_var.extend([tmin,tmax,tstep])
        list_points=[]
        for val in range(len(list_x0)) :
            point=QgsPoint(list_x0[val],list_y0[val]) 
            list_points.append(point)
        self.LineLayer = QgsVectorLayer("LineString?crs=EPSG:4326","LineSection", "memory")
        self.setupRendererLineLayer()
        self.selectLines=CaptureTool(self.canvas,self.LineLayer,self,self.onGeomAdded,1)
        self.selectLines.geometryCaptured(list_points,section_name,list_var)

    def get_coords(self,pfile,namesect):
        list_x0=[]
        list_y0=[]
        var=pfile
        for item,variable in var.items():
            for def_region in variable :
                name=def_region[0]
                if str(name) == str(namesect) :
                    x1,y1=def_region[1]
                    x2,y2=def_region[2]
                    tmin,tmax=def_region[3]
                    smin,smax=def_region[4]
                    tstep,sstep=def_region[5]
                    flag=def_region[6]
                    list_x0=[]
                    list_x0.append(x1)
                    list_x0.append(x2)
                    list_y0=[]
                    list_y0.append(y1)
                    list_y0.append(y2)
        return list_x0,list_y0,tmin,tmax,smin,smax,tstep,sstep,flag


    def addRaster(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                     self.tr("netCDF Files (*.nc *.cdf *.nc2 *.nc4 *.tiff *.tif *)"));
        if fileName is not None:
            ## Multiple cases depending on the file type
            type_file=os.path.basename(str(fileName)).split('.')[1]
            print type_file
            if type_file == "nc" or type_file == "nc4" or type_file == "cdf" :
                self.updateFileNC(fileName)
            else : 
                self.updateFileRaster(fileName)
            self.GroupBoxPal.setEnabled(True) 
    def addVector(self):
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), "",
                      self.tr("Shapes Files (*)"));
        if fileName is not None:
            ## Find dimensions and variables
            ll_color=True
            self.updateFileVector(fileName,20,ll_color)
            self.GroupBoxPal.setEnabled(True) 
    def AddGeojson(self):
        dir_geojson='/home/cregnier/DEV/Data_test/Geojson/' 
        fileName = QFileDialog.getOpenFileName(self, self.tr("Open File"), dir_geojson,
                     self.tr("Geojson (*geojson)"));
        if fileName is not None:
            ll_color=False
            self.updateFileVector(fileName,20,ll_color)
            self.GroupBoxPal.setEnabled(True) 
    def metaSearch(self):
        print "OPEN Metasearch"
        # Open CSW plugin
        self.openCSWplugin= MetaSearchDialog(self.canvas)
        self.openCSWplugin.exec_()
    def updateFileRaster(self,name):
        print "updateFileRaster"
        self.layer_raster=QgsRasterLayer(name,os.path.basename(str(name)))   
        if not self.layer_raster.isValid():
            print "Layer failed to load!"
        QgsMapLayerRegistry.instance().addMapLayers([self.layer_raster])
        ## Set active layer to previous layer to use redrawing function
        # Set up the map canvas layer set
        self.layers.append( QgsMapCanvasLayer(self.layer_raster) )
        self.canvas.setExtent(self.layer_raster.extent())
        band=1
        self.addLayer(self.layer_raster,band)
        self.compose=1

    def updateFileVector(self,name,transparency,ll_color):
        #  if self.canvas.activeLayer() : 
        #    layer1=self.canvas.activeLayer()
        self.layer2=QgsVectorLayer(name,os.path.basename(str(name)),"ogr")   
        if not self.layer2.isValid():
            print "Layer failed to load!"
        print transparency
        self.layer2.setLayerTransparency(transparency)
        if ll_color : 
            props = { 'color' : '192,192,192', 'style' : 'no', 'style' : 'solid' }
            s = QgsFillSymbolV2.createSimple(props)
            self.layer2.setRendererV2( QgsSingleSymbolRendererV2( s ) ) 
        print "Add vector layer to registry"
        QgsMapLayerRegistry.instance().addMapLayers([self.layer2])
        ## Set active layer to previous layer to use redrawing function
        # Set up the map canvas layer set
        self.layers.append( QgsMapCanvasLayer(self.layer2) )
      # # self.canvas.setLayerSet(self.layers)
        self.canvas.setExtent(self.layer2.extent())

    def updateFileNC(self,fileName):
        if fileName == '':
            return
        self.ll_speedu=False
        self.ll_speedv=False
        self.filename=fileName
        print "UPDATE_FILE %s "%(fileName) 
        self.variables = []
        self.dim_values = dict()
        self.dim_def = dict()
        self.dim_band = dict()
        if not str(fileName) : 
            print "Pb with filename"
            return 
        self.filename=str(fileName)
        if self.debug>0:
            print "Open dataset"
        nc=netCDF4.Dataset(str(fileName),'r')
        ## Populate Variable list and put a flag for speed u and v
        list_lon=['longitude','lon','nav_lon']
        list_lat=['latitude','lat','nav_lat']
        list_depth=['depth','deptht']
        list_time=['time','time_counter']
        if self.debug>0:
            print "Open dataset OK"
        for var in nc.variables:
            if var not in list_lon and var not in list_lat and var not in list_depth and var not in list_time : 
            #if var != 'longitude' and var != 'latitude' and var != 'nav_lon' \
             #and var != 'nav_lat' and var != 'depth' and var != 'deptht' and var != 'time_counter' and var != 'time' :
                if str(var) == 'u' or str(var) == 'vomecrty':
                    self.ll_speedu=True
                if str(var) == 'v' or str(var) == 'vozocrtx' :
                    self.ll_speedv=True
                self.variables.append(str(var))
        if self.debug>0:
            print('variables: '+str(self.variables))
        self.cboVars.blockSignals(True)
        self.cboVars.clear()
        self.cboDim.clear()
        item=QtGui.QStandardItem("Variable")
        item.setForeground(QtGui.QColor('black'))
        #font = QtGui.QFont("Times",20,QtGui.QFont.Bold,True)
        font = item.font()
        font.setPointSize(8)
        font.setBold(True) 
        item.setFont(font)
        item.setSelectable(False)
        model = self.cboVars.model()
        model.appendRow(item)
        for var in self.variables:
            print('variables: %s'%(var))
            self.cboVars.addItem( var )
        self.cboVars.blockSignals(False)
        self.cboVars.setCurrentIndex(1)
        if self.debug>0:
            print('done updateFile '+fileName)
        ## Update dimension
        variable=self.cboVars.currentText()
        nc=netCDF4.Dataset(str(fileName),'r')
        dim_var=nc.variables[str(variable)].dimensions
        dim_len=nc.variables[str(variable)].shape
        i=0
        if self.debug>0:
            print 'Dim var and len : '
            print dim_var,dim_len
            print 'var %s ' %(variable)
        self.dim_names = []
        for dim in dim_var :
            if self.debug>0:
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
            #if dim_def[dim][0] <= 1 or dim /= 'depth' or dim /= 'deptht' :
            if dim == 'depth'  or dim == 'deptht':
                dim_prof=dim
                self.dim_names.append(dim)
                print 'dim ok %s ' %(dim)
            elif dim == 'time_counter' and dim_def[dim][0] > 1 : 
                self.dim_names.append(dim)
            else:
                del self.dim_values[dim]
                del self.dim_def[dim]
        if self.debug>0:
            print(str(self.dim_names))
            print "Dimensions"
            print "--------------------"
            print self.dim_names
            print self.dim_def
            print type(self.dim_names)
            print type(self.dim_def)
            print "-------------------"
        if len(self.dim_names) > 1:
            #self.cboDim.setEnabled(True)
            def_var=self.dim_def[dim]
            dim = self.dim_names[0]
            if int(self.dim_def[dim][0]) <= 1 :
                self.cboDim.setEnabled(False)
            else :
                self.cboDim.setEnabled(True)
            #self.cboDim.addItem("Dim")
            self.cboDim.clear()
            ## Update dimension values
            self.compose=0
            for value in range(0,def_var[1]): 
                self.cboDim.addItem(str(value))
        elif len(self.dim_names) == 1  :
            dim_name=self.dim_names[0]
            if int(self.dim_def[dim_name][0]) <= 1 :
                self.cboDim.setEnabled(False)
            else :
                self.cboDim.setEnabled(True)
        else :
            self.cboDim.setEnabled(False)

    def updateVariable(self):
        self.Valminvalue.setText("")
        self.Valmaxvalue.setText("")
        print "UPDATEVARIABLE" 
        self.dim_names = []
        self.dim_values = dict()
        self.dim_def = dict()
        self.dim_band = dict()
        self.actionMakeoperation.setEnabled(True)
        self.actionPlotsection.setEnabled(True)
        ## Enable Plot current action if exist
        if self.ll_speedu and self.ll_speedv : 
            self.actionPlotCurrent.setEnabled(True)
        ## Update dimension
        variable=self.cboVars.currentText()
        nc=netCDF4.Dataset(str(self.filename),'r')
        if self.debug>0: 
            print 'Update variable var %s ' %(variable) 
        dim_var=nc.variables[str(variable)].dimensions
        dim_len=nc.variables[str(variable)].shape
        i=0
        if self.debug>0: 
            print dim_var
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
        dim_prof=1
        for dim in dim_names:
            #print 'dim %s ' %(dim)
            #if dim_def[dim][0] <= 1 or dim /= 'depth' or dim /= 'deptht' :
            if dim == 'depth'  or dim == 'deptht': 
                self.dim_names.append(dim)
                def_var=self.dim_def[dim]
                dim_prof=dim
            elif dim == 'time_counter' and dim_def[dim][0] > 1 : 
                self.dim_names.append(dim)
            else:
                del self.dim_values[dim]
                del self.dim_def[dim]
        print "Dimension "
        print len(self.dim_names)
        if len(self.dim_names) > 0:
            dim = self.dim_names[0]
            def_var=self.dim_def[dim]
            if int(self.dim_def[dim][0]) <= 1 :
                self.cboDim.setEnabled(False)
            else :
                self.cboDim.setEnabled(True)
            ## Update dimension values
            self.cboDim.clear()
            for value in range(0,def_var[0]): 
                self.compose=0
                self.cboDim.addItem(str(value+1))
            dim_val=self.cboDim.currentText()
            self.compose_layer(self.filename,variable,dim_val)
        elif len(self.dim_names) == 2:
            self.addLayerMulti(self.filename,variable,dim_val)
        else:
            self.compose=0
            if  dim_prof == 1 :
                self.cboDim.setEnabled(False)
            else :
                self.cboDim.setEnabled(True)
            self.cboDim.clear()
            self.cboDim.addItem(str(1))
            self.compose_layer(self.filename,variable,1)

    def updateDims(self): 
        print "Update dimensions"
        print self.compose
        band=self.cboDim.currentText()
        var=self.cboVars.currentText()
        if self.compose == 1 : 
            self.compose_layer(str(self.filename),str(var),band)

    def onStartPointSelected(self):
        self.modified = True
        QgsMapLayerRegistry.instance().addMapLayer( self.startPointLayer)
        self.layers.append(QgsMapCanvasLayer(self.startPointLayer)) 
        self.canvas.refresh()
        self.actionCapture.setChecked(False)
        self.pan()
#       self.curStartPt = feature.geometry().vertexAt(vertex)
#       self.clearMemoryLayer(self.startPointLayer)
#       feature = QgsFeature()
#       feature.setGeometry(QgsGeometry.fromPoint(self.curStartPt))
#       self.startPointLayer.dataProvider().addFeatures([feature])
#       self.startPointLayer.updateExtents() 
     #   self.adjustActions()
        
    def onGeomAdded(self):
        print "inside onGeomAdded"
        self.modified = True
        QgsMapLayerRegistry.instance().addMapLayer(self.LineLayer)
        self.layers.append(QgsMapCanvasLayer(self.LineLayer)) 
        self.canvas.refresh()
        self.actionCapture.setChecked(False)
        self.pan()
        print "ok"

    def compose_layer(self,fileName,var,band):
        if self.debug>0:
            print('Compose layer (%s,%s,%s)' % (fileName,var,band))
        uri = 'NETCDF:"%s":%s' % (fileName, var)
        print "Compose Layer uri %s" %(uri)
        #name = '%s_var=%s' % (fileName,var) 
        name = '%s_var=%s' % (QFileInfo(fileName).fileName(),var)
        print 'band %s'  %(band)
        print "Dimensions "
        print self.dim_names
        print "Dim OK"
        if int(band) == 1 :
            print "Cas1"
            name = '%s_band=%s' % (name, str(band))
        else:
            print "Cas2"
            name = "%s_%s=%s" % (str(name),str(self.dim_names[0]),str(band))
            name = '%s_band=%s' % (name, str(band))

        print 'uri %s' %(uri)
        print 'Name raster %s' %(name)
        s = QSettings()
        new_name=os.path.basename(name)
        name_model=new_name.split('_')[0]
        datevalue=new_name.split('_')[3]
        name_layer=name_model+'_'+datevalue+'_lvl'+str(band)+'_'+var
        self.rlayer = QgsRasterLayer( uri, name_layer)
        self.rlayer.setCrs( QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        QgsMapLayerRegistry.instance().addMapLayers([self.rlayer])
        print 'Add map to the registry'
        ## root = QgsProject.instance().layerTreeRoot()
        ## node_layer1 = root.addLayer(self.rlayer)
        ## node_layer2 = QgsLayerTreeLayer(self.rlayer)
        ## root.insertChildNode(0, node_layer2)
        ## Add layer to legend
        #self.legend.addLayerToLegend(self.rlayer)
        ##
        self.addLayer(self.rlayer,band)	
        print 'Add layer OK'
        self.actionGetValue.setEnabled(True)
        self.actionPlotProfile.setEnabled(True)
        self.actionCapture.setEnabled(True)
        self.actionTransparency.setEnabled(True)
        self.actionContouring.setEnabled(True)
        self.getvalue=PointTool(self.canvas,self.rlayer,self) # false = in
        print 'Add PoinTool'
        self.getvalue.setAction(self.actionGetValue)
        self.selectTool=DistanceCalculator(self.canvas,self)
        self.selectTool.setAction(self.actionDistance)
        print 'Add setAction'
        self.compose=1

    def addLayer(self,layer,band):
        self.layer=layer
        print type(layer)

        if self.layer is None or not self.layer.isValid():
            print('Netcdf raster %s failed to load')
            return
        ## Test
        #self.canvas.mapRenderer().setProjectionsEnabled(True)
        #self.projSelector = QgsGenericProjectionSelector()
        #self.projSelector.exec_()
        #self.projSelector.selectedCrsId()
        #self.projSelector.selectedAuthId()
        #print "ok projection dialog box"
        #self.newprojec=self.projSelector.selectedAuthId()
        #self.idprojec=self.projSelector.selectedCrsId()
        #layer_EPSG_int=int(self.newprojec[5:])
        #print "Projection selected : EPSG",str(layer_EPSG_int)
        #print layer_EPSG_int
        #CRS = QgsCoordinateReferenceSystem(layer_EPSG_int,QgsCoordinateReferenceSystem.EpsgCrsId)
        #self.layer.setCrs(CRS)
        ##
        colorRamp=self.combocolor.currentColorRamp()	
        if colorRamp is None :
            print('Colorramp is none')
            pass
        if self.layer.type() == 1  :
            nb_classes=self.cboNbcolor.value()
            self.updatelayerwithpal(layer,colorRamp,int(nb_classes),band)
            self.canvas.setExtent(self.layer.extent())
        else : 
            print "Vector Layer"
        self.canvas.enableAntiAliasing(True)    

        myLayerSet=[]
        #self.layer.setLayerTransparency(80)
        cl1=QgsMapCanvasLayer(layer)
        myLayerSet.append(cl1)
        self.layers.append( QgsMapCanvasLayer(layer) )
        self.canvas.setExtent(self.layer.extent())
        self.canvas.freeze(False)
        # set the map canvas layer set
        self.canvas.refresh()
        self.canvas.update()
        self.canvas.zoomToFullExtent()
        layer_crs = self.layer.crs()
        layer_crs_str=layer_crs.authid()
        layer_EPSG_int=int(layer_crs_str[5:])
        self.proj.setText("EPSG:"+str(layer_EPSG_int))
        self.compose=1

    def drawLayer(self): 
        ## Get current colormap
        print "do drawLayer "
        self.layer=self.view.currentLayer()
        print "Layer",self.layer
        typelayer = self.layer.type()
        print "layer type : %i " %(typelayer) 
        if typelayer == 1 : # Raster
            print "Layer raster"
            colorRamp=self.combocolor.currentColorRamp()      
            nb_classes=self.cboNbcolor.value()
            print nb_classes
            dim_val=self.cboDim.currentText()
            if dim_val == "Dims" : 
                dim_val=1
                print dim_val
            print "updatelayerwithpal"
            self.updatelayerwithpal(self.layer,colorRamp,int(nb_classes),dim_val)

    def updatelayerwithpal (self,layer,colorRamp,nb_values,band) :
        ## Update layer with proper coloramp depending on coloramp and nb classes
        if layer.isValid() :
            print "layer valid"
            print band
            myRasterShader = QgsRasterShader()
            myColorRamp = QgsColorRampShader()
            renderer = layer.renderer()
            provider = layer.dataProvider()
            band=int(band)
            cmin= self.Valminvalue.text()
            cmax= self.Valmaxvalue.text()
            print cmin,cmax
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
            if cmin == "" and cmax == "" :
                print "Empty values"
            else :
                "Values not empty"
                rastermin=float(cmin)
                rastermax=float(cmax)

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
    def addLayerwithproj2(self,layer,band):
        self.layer=layer
        if self.layer is None or not self.layer.isValid():
            print('Netcdf raster %s failed to load')
            return
        self.crsInit=QgsCoordinateReferenceSystem(self.layer.crs())
        print "Crs init " 
        print self.crsInit
        ## Test
        myrender = self.canvas.mapRenderer()
        myrender.setProjectionsEnabled(True)
        self.projSelector = QgsGenericProjectionSelector()
        self.projSelector.exec_()
        self.projSelector.selectedCrsId()
        self.projSelector.selectedAuthId()
        print "ok projection dialog box"
        self.newprojec=self.projSelector.selectedAuthId()
        self.idprojec=self.projSelector.selectedCrsId()
        print self.idprojec
        layer_EPSG_int=int(self.newprojec[5:])
        print "Projection selected : EPSG",str(layer_EPSG_int)
        crsDest=layer_EPSG_int
        print "OK1"
        # Add layers to canvas
        if self.layer.isValid():
            print "OK2"
            if self.layer.type() == layer.RasterLayer:
                print "Rasterlayer"
                CRS = QgsCoordinateReferenceSystem(layer_EPSG_int,QgsCoordinateReferenceSystem.EpsgCrsId)
                crs = self.layer.crs()
                print crs.toProj4()
                if CRS.isValid() :
                    print "Set crs for the layer"
                    self.layer.setCrs(CRS)
                    print "Set crs for the canvas"
                    self.canvas.setMapUnits(0) 
                    #myrender.setDestinationCrs(CRS)
                    print "set CRS OK"
                # ensure any cached render data for this layer is cleared
                crs = self.layer.crs()
                print crs.toProj4()
                self.layer.setCacheImage(None)
                self.layer.triggerRepaint()
                # Set extent to the extent of our layer
                #self.canvas.setExtent(self.layer.extent())
                self.canvas.enableAntiAliasing(True)
                self.canvas.freeze(False)
                self.canvas.refresh()
                self.canvas.zoomToFullExtent()
                print "Passe la!!!!!!!!!!!!!"
                layer_crs = self.layer.crs()
                layer_crs_str=layer_crs.authid()
                layer_EPSG_int=int(layer_crs_str[5:])
                self.proj.setText("EPSG:"+str(layer_EPSG_int))
                self.compose=1
        else : 
            print "Layer not valid"

    def addLayerwithproj(self,layer,band):
        print type(layer)
        self.layer=layer
        if self.layer is None or not self.layer.isValid():
            print('Netcdf raster %s failed to load')
            return
        ## Test
        myrender = self.canvas.mapRenderer()
        myrender.setProjectionsEnabled(True)
        self.projSelector = QgsGenericProjectionSelector()
        self.projSelector.exec_()
        self.projSelector.selectedCrsId()
        self.projSelector.selectedAuthId()
        print "ok projection dialog box"
        self.newprojec=self.projSelector.selectedAuthId()
        self.idprojec=self.projSelector.selectedCrsId()
        layer_EPSG_int=int(self.newprojec[5:])
        print "Projection selected : EPSG",str(layer_EPSG_int)
        print layer_EPSG_int
       # CRS = QgsCoordinateReferenceSystem(layer_EPSG_int,QgsCoordinateReferenceSystem.EpsgCrsId)
        CRS = QgsCoordinateReferenceSystem(2154,QgsCoordinateReferenceSystem.EpsgCrsId)
        self.layer.setCrs(CRS)
        print "Projection layer",str(self.layer.crs())
        ## test
        print "OK1"
        #srs = QgsCoordinateReferenceSystem()
        #print "OK2"
        #srs.createFromEpsg(3408)
        #print "OK3"
        #self.canvas.setMapUnits(QGis.METERS)
        #self.rect = self.canvas.extent()
        #mapRender = self.canvas.mapRenderer()
        #print "OK2"
        #mapRender.setDestinationSrs(srs)
        #print "OK3"
        #mapRender.fullExtent()
        #print "OK4"
        #self.canvas.refresh()
        print "OK5"
        #myrender.setDestinationSrs(CRS)
        ##
        colorRamp=self.combocolor.currentColorRamp()      
        #if colorRamp is None :
        #   print('Colorramp is none')
        #   pass
        #if self.layer.type() == 1  :
        #  nb_classes=self.cboNbcolor.value()
        #  self.updatelayerwithpal(self.layer,colorRamp,int(nb_classes),band)
        #  self.canvas.setExtent(self.layer.extent())
        #else : 
        #  print "Vector Layer"
        self.canvas.enableAntiAliasing(True)    

        myLayerSet=[]
        #self.layer.setLayerTransparency(80)
        cl1=QgsMapCanvasLayer(self.layer)
        myLayerSet.append(cl1)
        self.layers.append( QgsMapCanvasLayer(self.layer) )
        self.canvas.setExtent(self.layer.extent())
        self.canvas.freeze(False)
        #self.layer.triggerRepaint()
        # set the map canvas layer set
        self.canvas.refresh()
        self.canvas.update()
        self.canvas.zoomToFullExtent()
        print "Passe la!!!!!!!!!!!!!"
        layer_crs = self.layer.crs()
        layer_crs_str=layer_crs.authid()
        layer_EPSG_int=int(layer_crs_str[5:])
        self.proj.setText("EPSG:"+str(layer_EPSG_int))
        self.compose=1


        ##if layer is None or not layer.isValid():
        ##    print('Netcdf raster %s failed to load')
        ##    return
        #### Test
        ##self.projSelector = QgsGenericProjectionSelector()
        ##self.projSelector.exec_()
        ##self.projSelector.selectedCrsId()
        ##self.projSelector.selectedAuthId()
        ##print "ok projection dialog box"
        ##self.newprojec=self.projSelector.selectedAuthId()
        ##self.idprojec=self.projSelector.selectedCrsId()
        ##layer_EPSG_int=int(self.newprojec[5:])
        ##print "Projection selected : EPSG",str(layer_EPSG_int)
        ##print layer_EPSG_int
        ##CRS = QgsCoordinateReferenceSystem(layer_EPSG_int,QgsCoordinateReferenceSystem.EpsgCrsId)
        ##layer.setCrs(CRS)
        ###myrender = self.canvas.mapRenderer()                                                                                                                                                                    
        ###myrender.setProjectionsEnabled(True)
        ###myrender.setDestinationCrs(CRS)
        ##colorRamp=self.combocolor.currentColorRamp()      
        ##if colorRamp is None :
        ##   print('Colorramp is none')
        ##   pass
        ##if self.layer.type() == 1  :
        ##  nb_classes=self.cboNbcolor.value()
        ##  self.updatelayerwithpal(layer,colorRamp,int(nb_classes),band)
        ##  self.canvas.setExtent(self.layer.extent())
        ##else : 
        ##  print "Vector Layer"
        ##self.canvas.enableAntiAliasing(True)    

        ##myLayerSet=[]
        ###self.layer.setLayerTransparency(80)
        ##cl1=QgsMapCanvasLayer(layer)
        ##myLayerSet.append(cl1)
        ##self.layers.append( QgsMapCanvasLayer(layer) )
        ##self.canvas.setExtent(self.layer.extent())
        ##self.canvas.freeze(False)
        ### set the map canvas layer set
        ##self.canvas.refresh()
        ##self.canvas.update()
        ##self.canvas.zoomToFullExtent()
        ##print "Passe la!!!!!!!!!!!!!"
        ##layer_crs = self.layer.crs()
        ##layer_crs_str=layer_crs.authid()
        ##layer_EPSG_int=int(layer_crs_str[5:])
        ##self.proj.setText("EPSG:"+str(layer_EPSG_int))
        ##self.compose=1

##      myLayerSet=[]
##      #self.layer.setLayerTransparency(80)
##      cl1=QgsMapCanvasLayer(layer)
##      myLayerSet.append(cl1)
##      self.layers.append( QgsMapCanvasLayer(layer) )
##      self.canvas.mapRenderer().setDestinationCrs(CRS)
##      self.canvas.setExtent(self.layer.extent())
##      print "OK1"
##      layer.triggerRepaint()
##      self.canvas.freeze(False)
##      print "OK2"
##      # set the map canvas layer set
##      self.canvas.refresh()
##      self.canvas.update()
##      self.canvas.zoomToFullExtent()
##      print "Passe la!!!!!!!!!!!!!"
##      layer_crs = layer.crs()
##      layer_crs_str=layer_crs.authid()
##      layer_EPSG_int=int(layer_crs_str[5:])
##      self.proj.setText("EPSG:"+str(layer_EPSG_int))
##      self.compose=1

    def on_proj_triggered(self):
        print "New proj !!"
        rasterlayer=self.view.currentLayer()
        if rasterlayer : 
            band=1
            self.addLayerwithproj2(rasterlayer,band)         

    def on_proj_triggered_old(self):
        ## Open Projection dialog 
        self.projSelector = QgsGenericProjectionSelector()
        self.projSelector.exec_()
        self.projSelector.selectedCrsId()
        self.projSelector.selectedAuthId()
        #self.myEpsg=self.projSelector.selectedAuthId()
        #self.projSelector.setSelectedAuthId(self.myEpsg)
        print "ok projection dialog box"
        self.newprojec=self.projSelector.selectedAuthId()
        self.idprojec=self.projSelector.selectedCrsId()
        layer_EPSG_int=int(self.newprojec[5:])
        print "Projection selected : EPSG",str(layer_EPSG_int)
        rasterlayer=self.view.currentLayer()
        if rasterlayer : 
            band=1
            self.addLayer(rasterlayer,band)         
###          self.canvas.mapRenderer().setProjectionsEnabled(True)
###          print "CRS before : " + rasterlayer.crs().geographicCRSAuthId()
###      #   print "Add projection to the layer"
###      #   crslayer=self.rasterlayer.crs()
###      #   print "OK1"
###      #   crslayer.createFromId(layer_EPSG_int)
###      #   print "OK2"
###      #   self.rasterlayer.setCrs(crslayer)
###      #   #print "OK3"
###      #   print "OK1"
###      #   #self.rasterlayer.setCrs(QgsCoordinateReferenceSystem(layer_EPSG_int,QgsCoordinateReferenceSystem.EpsgCrsId))
###      #   my_crs = qgis.core.QgsCoordinateReferenceSystem(layer_EPSG_int, qgis.core.QgsCoordinateReferenceSystem.EpsgCrsId)
###      #   print "OK2"
###      #   self.canvas.mapRenderer().setDestinationCrs(my_crs)
###      #   QgsMapLayerRegistry.instance().addMapLayers([self.rasterlayer])  
###      #   print "OK3"
###      #   self.canvas.refresh()
###      #   self.proj.setText("EPSG:"+str(layer_EPSG_int))
#####    #     print "OK4"
###      #   self.canvas.update()
#####    #     print "Add projection to the layer OK"
###          if self.canvas.mapRenderer().hasCrsTransformEnabled():
###             print "Transform enabled"
###             CRS = QgsCoordinateReferenceSystem()
###             print layer_EPSG_int
###            # CRS.createFromSrid(layer_EPSG_int)
###             CRS = qgis.core.QgsCoordinateReferenceSystem(layer_EPSG_int,qgis.core.QgsCoordinateReferenceSystem.EpsgCrsId)
### #            my_crs = qgis.core.QgsCoordinateReferenceSystem(3408,qgis.core.QgsCoordinateReferenceSystem.EpsgCrsId)
###             #my_crs = core.QgsCoordinateReferenceSystem(3408,core.QgsCoordinateReferenceSystem.EpsgCrsId)
###            # my_crs = QgsCoordinateReferenceSystem(layer_EPSG_int)
###             print "Define new crs"
###             rasterlayer.setCrs(CRS)
###             rasterlayer.setCacheImage(None)
###             rasterlayer.triggerRepaint()
###             self.canvas.mapRenderer().setDestinationCrs(CRS)
###             print "CRS after : " + rasterlayer.crs().authid()
###             self.proj.setText("EPSG:"+str(layer_EPSG_int))
###             print "Canvas crs " +self.canvas.mapRenderer().destinationCrs().authid()
###             self.canvas.setExtent(rasterlayer.extent())
###             self.canvas.freeze(False)
###             # set the map canvas layer set
###             self.canvas.refresh()
###             self.canvas.update()
###             self.canvas.zoomToFullExtent()
###             #QgsMapLayerRegistry.instance().addMapLayers([rasterlayer])  
###             print "Add crs to map canvas"
###          else : 
###             print "Transform not enabled"
        else: 
            print "Layer not selected!"
        return

    def on_basemap_triggered(self):
        statics_dir=str(self.homepath)+"/statics/"
        filename="ne_50m_land.shp"
        ll_color=True
        self.updateFileVector(statics_dir+filename,0,ll_color)
        ## Cas 2
        ##filename="NE1_50M_SR.tif"
        ##print statics_dir+filename
        ##self.updatetif(statics_dir+filename)

    def updatetif(self,fileName):
        fileInfo = QFileInfo(fileName)
        print fileInfo
        baseName = fileInfo.baseName()
        print baseName
        rlayer = QgsRasterLayer(fileName, baseName)
        if not rlayer.isValid():
            print "Layer failed to load!"
        rlayer.setCrs( QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId))
        QgsMapLayerRegistry.instance().addMapLayers([rlayer])

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
        provider=MyMenuProvider(self.view,self.layers,self.canvas,self)
        self.view.setMenuProvider(provider)

## Define Main
def main():
    print "launch Main"
    QgsApplication.setPrefixPath(os.environ['QGIS_PREFIX'], True)
    QgsApplication.initQgis()
    try : 
        app = QApplication(sys.argv)
        standalone=int(sys.argv[1])
        if QgsApplication.showSettings() :
	   print "Settings OK"
 	   print QgsApplication.showSettings()
	else :
	   print "settings nok"
	   sys.exit(1)
        window = Mercator_Explorer(standalone)
        window.show()
        window.raise_()
        app.exec_()
        app.deleteLater()
        QgsApplication.exitQgis()
    except: 
        raise
if __name__ == "__main__":
    print "launch Main"
    main()
