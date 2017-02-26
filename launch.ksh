#!/bin/sh
## Linux Launcher for Qgis standalone application
## C.REGNIER November 2015

echo "start export"
#### Plugin
export PYTHONPATH="/usr/share/qgis/python"
export PYTHONPATH=$PYTHONPATH:"/usr/share/qgis/python/plugins/"
export LD_LIBRARY_path="/usr/lib/qgis/"
#export QGIS_PREFIX="/home/modules/versions/64/centos7/qgis/qgis-2.8.1_gnu4.8.2/"
export QGIS_PREFIX="/usr/share/qgis"
#export PYTHONPATH=$PYTHONPATH:"/home/cregnier/DEV/QGIS/Charly_V0/ThreddsViewer"
export PYTHONPATH=$PYTHONPATH:"/home/cregnier/DEV/QGIS/QGIS_standalone_app/THREDDSExplorer"
#/home/modules/versions/64/centos7/gdal/gdal-1.11.2_gnu4.8.2/lib64/python2.7/site-packages"

dir_var="/home/cregnier/DEV/QGIS/QGIS_standalone_app/"
cd ${dir_var}
echo $PWD
echo "Launch standalone"
python main_standalone.py 1
#python main_standalone_test.py
