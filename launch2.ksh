#!/bin/ksh
## Linux Launcher for Qgis standalone application
## C.REGNIER November 2015

export PYTHONPATH="/home/modules/versions/64/centos7/qgis/qgis-2.11_gnu4.8.2/share/qgis/python"
## Plugin
export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/qgis/qgis-2.11_gnu4.8.2/share/qgis/python/plugins/"
export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/gdal/gdal-1.11.2_gnu4.8.2/lib64/python2.7/site-packages"
export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/netcdf4python/netcdf4python-1.0.7_gnu4.8.2/lib64/python2.7/site-packages"
export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/numpy/numpy-1.9.1_gnu4.8.2/lib64/python2.7/site-packages"
export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/scipy/scipy-0.15.1_gnu4.8.2/lib64/python2.7/site-packages" 
export PYTHONPATH=$PYTHONPATH:"/home/modules/versions/64/centos7/scientificpython/scientificpython-2.9.3_gnu4.8.2/lib64/python2.7/site-packages" 
export LD_LIBRARY_path="/home/modules/versions/64/centos7/qgis/qgis-2.11_gnu4.8.2/lib"
export QGIS_PREFIX="/home/modules/versions/64/centos7/qgis/qgis-2.11_gnu4.8.2/"
module load ipython
python main_standalone.py
