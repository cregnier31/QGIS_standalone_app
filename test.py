layername="&crs=EPSG:4326&srs=EPSG:4326&dpiMode=7&format=image/png&WIDTH=2048&HEIGHT=2048&SERVICE=WMS&layers=hurs&styles=boxfill/sst_36&url=http://www.meteo.unican.es/thredds/wms/PNACC2012/Rejilla/indicadores_PNACC_2012/nc_files/WSSMAX/CTL/ENSEMBLES/WSSMAX_SMHI_ERA40_CTL_1961_2000.nc"
resultLayer=QgsRasterLayer(layername,'testlayer2','wms')
QgsMapLayerRegistry.instance().addMapLayer(resultLayer)


