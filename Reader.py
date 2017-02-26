# -*- coding: utf-8 -*-                                                                                                                                                                                         
import gdal
from gdalconst import *                                                                                                                              
from GDALParameters import GDALParameters
import numpy as np
def array_to_raster(array, cell_sizes, topleft_corner,noDataValue, out_filepath):
    """Array > Raster
    Save a raster from a C order array.

    :param array: ndarray
    """
    gdal.AllRegister()
    y_pixels, x_pixels = array.shape 
    cellsize_long, cellsize_lat = cell_sizes 
    x_min, y_max = topleft_corner

    #wkt_projection = 'a projection in wkt that you got from other file'

    driver = gdal.GetDriverByName('GTiff')

    dataset = driver.Create(
        out_filepath,
        x_pixels,
        y_pixels,
        1,
        gdal.GDT_Float32)

    dataset.SetGeoTransform((
        x_min,    # 0
        cellsize_long,  # 1
        0,                      # 2
        y_max,    # 3
        0,                      # 4
        -cellsize_lat))  

    #dataset.SetProjection(wkt_projection)
    dataset.GetRasterBand(1).SetNoDataValue(noDataValue)
    dataset.GetRasterBand(1).WriteArray(array)
    dataset.FlushCache()  # Write to disk.
 
def read_netcdf_variable(netcdf_file, var_name,band):                                                                                           

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
         print "More than one raster band in raster"
  #      raise TypeError, 'More than one raster band in raster' 
    
    # set critical grid values from geotransform array
    raster_params.set_topLeftX(netcdf_file_var.GetGeoTransform()[0])
    raster_params.set_pixSizeEW(netcdf_file_var.GetGeoTransform()[1])
    raster_params.set_rotationA(netcdf_file_var.GetGeoTransform()[2])
    raster_params.set_topLeftY(netcdf_file_var.GetGeoTransform()[3])
    raster_params.set_rotationB(netcdf_file_var.GetGeoTransform()[4])
    raster_params.set_pixSizeNS(netcdf_file_var.GetGeoTransform()[5])           
        
    # get single band 
    band = netcdf_file_var.GetRasterBand(band)    

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

###
def read_lightout(lightout_file):
    """
    M.Hamon 03/2016
    Lecture des fichiers alleges :
        - Lecture de l'entete du fichier binaire sur les 54 premiers bytes.
        - Lecture de la variable (Entier en 16 bits) à partir du 62eme byte jusqu'a la fin du fichier moins 4 bytes.
        - Conversion des valeurs.
    ALLEGE = read_lightout(lightout_file)
    """ 
    import os, sys, re
    from math import tan,atan,pi
    import numpy as np
    import struct
    print "Inside lightout file"
    print lightout_file
    print os.path.isfile(str(lightout_file)) 
    if not os.path.isfile(str(lightout_file)) :
      print "No such file or directory. Please Check the path/name of the file"
      sys.exit(1)
    try:
        print "Inside lightout file"
        f = open(lightout_file, mode='rb')
        fileContent = f.read()
        f.close()

        DIM=struct.unpack(">13fh", fileContent[:54])

        offsetbyte=62 # nombre de bytes du header
        # le header est étrangement range!
        LON=int(DIM[1])
        LAT=int(DIM[4])
        LEVEL=int(DIM[7])
        AUXMIN=DIM[10]
        AUXMAX=DIM[11]
        UNDEFO=DIM[12]
        MAXINT=DIM[13]

        nbbytes=len(fileContent)
        dimensions=LON*LAT*LEVEL
        var=np.zeros(dimensions)

        encodagevar='>'+str(dimensions)+'h'
        var=struct.unpack(encodagevar,fileContent[offsetbyte:nbbytes-4])

        AUXMID = (AUXMIN+AUXMAX)/2.
        scale = AUXMAX-AUXMID

        if(scale < 0.) :
           scale = 4./scale
        else :
           scale = 1.

        ATANMAX=atan( (AUXMAX - AUXMID )*scale )/pi
        ATANMIN=atan( (AUXMIN - AUXMID )*scale )/pi
        RMAXINT=MAXINT-1

        var_ok=np.zeros(dimensions)
        for ii in np.arange(dimensions) :
                if var[ii] != MAXINT :
                        var_ok[ii]=tan(var[ii]/(RMAXINT/ATANMAX)*pi)/scale+AUXMID
        ALLEGE=var_ok.reshape((LEVEL,LAT,LON))
        return ALLEGE
    except :
        print "Pb during reading lightened file"

