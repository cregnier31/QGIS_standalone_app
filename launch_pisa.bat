REM Launcher Appli Mercator C.REGNIER Fevrier 2016
SET QGIS_VERSION=C:\Program Files\QGIS Pisa
SET QGIS_PREFIX=%QGIS_VERSION%\apps\qgis
REM PYTHONPATH QGIS 
SET PYTHONPATH=%QGIS_PREFIX%\python;%QGIS_VERSION%\apps\Python27;%QGIS_VERSION%\apps\Python27\Lib;%QGIS_VERSION%\apps\qgis\python\plugins
REM PYTHONPATH Python
SET PYTHONPATH=C:\Python27\Lib\site-packages;%PYTHONPATH%
REM PYTHONPATH Appli
SET PYTHONPATH=C:\Users\dpeyrot\.qgis2\python\plugins;C:\Users\dpeyrot\pyqgis_scripts\external_appli_mo\contour;%PYTHONPATH%
SET PYTHONHOME=C:\Program Files\QGIS Pisa\apps\Python27
SET PATH=%QGIS_PREFIX%\bin;C:\Python27;C:\Python27\Scripts;C:\Program Files\QGIS Pisa\bin;C:\OSGeo4W64\bin
python main_standalone.py 1 
pause

