# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#!/usr/bin/env python
## C.REGNIER : Test all CMEMS WMS adress and save in a cPickle and text file
import sys,os,io,glob
import xml.etree.ElementTree as ET
import os,urllib2
import cPickle
from mpl_toolkits.basemap import Basemap
import pyproj
from datetime import datetime
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.image import imread
import numpy as np 
import owslib
from pylab import *
import matplotlib.cm as cm
import matplotlib.image as mpimg
import pylab as pl

##latmin=36.5
##lonmin=139
##latmax=42
##lonmax=142.5
##m = Basemap(
##        llcrnrlat=latmin,urcrnrlat=latmax,\
##                llcrnrlon=lonmin,urcrnrlon=lonmax,\
##                lat_ts=20,resolution='i',epsg=4326)
##m.wmsimage('http://www.finds.jp/ws/kiban25000wms.cgi?',xpixels=500,
##        layers=['PrefSmplBdr','RailCL'],styles=['thick',''])
##m.wmsimage('http://www.finds.jp/ws/pnwms.cgi?',xpixels=500,
##        layers=['PrefName'],styles=['large'],transparent=True)
##m.drawcoastlines()
##plt.show()
##
##sys.exit(1)
##serverurl='http://nowcoast.noaa.gov/wms/com.esri.wms.Esrimap/obs?'
##
##lon_min = -95; lon_max = -60
##lat_min = 5;  lat_max = 40.
##m = Basemap(llcrnrlon=lon_min, urcrnrlat=lat_max,
##                    urcrnrlon=lon_max, llcrnrlat=lat_min,resolution='l',epsg=4326)
##plt.figure()
##m.wmsimage(serverurl,layers=['RAS_GOES_I4'],xpixels=800,verbose=True)
##m.drawcoastlines(color='k',linewidth=1)
##plt.title('GOES IR Image')
##plt.show()
##sys.exit(1)

def getWMS(url_base):
    mercator_url1="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024"
    mercator_url2="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024-2hourly-t-u-v-ssh"
    mercator_url3="http://rancmems.mercator-ocean.fr/thredds/wms/dataset-global-reanalysis-phy-001-025-ran-fr-glorys2v4-daily"
    ll_request=False
    if url_base is mercator_url1 or url_base is mercator_url2 or url_base is mercator_url3:
        print "Mercator case"
        if 'http_proxy' in os.environ : 
            del os.environ['http_proxy']
        if 'https_proxy' in os.environ : 
            del os.environ['https_proxy']
    else :
        print "Not internal server"
        if not "http_proxy" in os.environ : 
            print "Set the http_proxy variable to pass the proxy"
            sys.exit(1)
    serverurl=url_base[0]
    version="1.1.1"
    url=url_base[0]+'?service=WMS&version='+version+'&request=GetCapabilities'
    lon_min = -118.8; lon_max = -108.6
    lat_min = 22.15;  lat_max = 32.34
    m = Basemap(llcrnrlon=lon_min, urcrnrlat=lat_max,
                        urcrnrlon=lon_max, llcrnrlat=lat_min,resolution='i',epsg=4326)
    m.wmsimage(serverurl,xpixels=500,verbose=True,
               layers=['thetao'],
               elevation='-0.49402499198913574',
               colorscalerange='271.2,308',numcolorbands='20',logscale=False,
               styles=['boxfill/ferret'])
              # styles=['boxfill/rainbow'])
               #time=datetime.utcnow().strftime('%Y-%m-%dT12:00:00.000Z'),
    plt.figure()
    m.drawcoastlines(linewidth=0.25)
    parallels = np.arange(20,36,2.)
    a=m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
    meridians = np.arange(-120,-100,2.)
    b=m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)



def getXML(url_base):
    mercator_url1="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024"
    mercator_url2="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024-2hourly-t-u-v-ssh"
    mercator_url3="http://rancmems.mercator-ocean.fr/thredds/wms/dataset-global-reanalysis-phy-001-025-ran-fr-glorys2v4-daily"
    ll_request=False
    print url_base
    if url_base is mercator_url1 or url_base is mercator_url2 or url_base is mercator_url3:
        print "Mercator case"
        if 'http_proxy' in os.environ : 
            del os.environ['http_proxy']
        if 'https_proxy' in os.environ : 
            del os.environ['https_proxy']
    else :
        print "Not internal server"
        if not "http_proxy" in os.environ : 
            print "Set the http_proxy variable to pass the proxy"
            sys.exit(1)
    version="1.1.1"
    url=url_base+'?service=WMS&version='+version+'&request=GetCapabilities'
    print " URL  %s " %(url)
    try :
        u=urllib2.urlopen(url,timeout=60)
        value=u.read()
        tree= ET.fromstring( value )
        ll_request=True
    except:
        ll_request=False 
        print "Probleme with WMS request"

    return ll_request



def getXML2(url_base):
    """ Get XML from WMS adress """
    mercator_url1="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024"
    mercator_url2="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-024-2hourly-t-u-v-ssh"
    mercator_url3="http://rancmems.mercator-ocean.fr/thredds/wms/dataset-global-reanalysis-phy-001-025-ran-fr-glorys2v4-daily"
    version="1.1.1"
    print "Adress %s " %(url_base[0])
    print mercator_url3
    try :
        if url_base[0] == mercator_url1 or url_base[0] == mercator_url2 or url_base[0] == mercator_url3 :
            print "Mercator case"
            if 'http_proxy' in os.environ : 
                del os.environ['http_proxy']
            if 'https_proxy' in os.environ : 
                del os.environ['https_proxy']
        else :
            print "Not internal server"
            if not "http_proxy" in os.environ : 
                print "Set the http_proxy variable to pass the proxy"
                sys.exit(1)
        ## Read xml with urllib2
        url=url_base[0]+'?service=WMS&version='+version+'&request=GetCapabilities'
        request = urllib2.Request(url, headers={"Accept" : "application/xml"})
        u = urllib2.urlopen(request)
        u=urllib2.urlopen(url)
        print url
        sys.exit(1)
        value=u.read()
        tree= ET.fromstring( value )
        #print ET.dump(tree)
        dict_var={}
        cap = tree.findall('Capability')[0]
        layer1 = cap.findall('Layer')[0]
        layer2 = layer1.findall('Layer')[0]
        layers = layer2.findall('Layer')
        for l in layers:
            #variable_name=l.find('Title').text
            variable_name=l.find('Name').text
            Title=l.find('Title').text
            #print "Title %s " %(Title)
            variable_name=l.find('Abstract').text
            #print 'variable %s ' %(variable_name)
            box=l.find('BoundingBox')
            lonmin=box.attrib['minx']
            lonmax=box.attrib['maxx']
            latmin=box.attrib['miny']
            latmax=box.attrib['maxy']
                #if var_box.attrib == 'minx' :
                #   lonmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxx' :
                #   latmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'miny' :
                #   lonmax=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxy' :
                #   latmax=str(dim.text).split(',')
            #for child in box:
            #    print child
            print lonmin,lonmax,latmin,latmax
            #dimensions=l.findall('LatLonBoundingBox')
            #print dimensions[1].text
            #for dim in dimensions : 
            #    print dim.text
                #if dim.attrib['name'] == 'minx' :
                #   lonmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxx' :
                #   latmin=str(dim.text).split(',')
                #if dim.attrib['name'] == 'miny' :
                #   lonmax=str(dim.text).split(',')
                #if dim.attrib['name'] == 'maxy' :
                #   latmax=str(dim.text).split(',')
            #print lonmin,lonmax,latmin,latmax
            dims=l.findall('Extent')
            list_prof=[]
            list_time=[]
            list_tot=[]
            for dim in dims : 
                if dim.attrib['name'] == 'elevation' :
                    list_prof=str(dim.text).split(',')
                if dim.attrib['name'] == 'time' :
                    list_time=str(dim.text).split(',')
            if  list_prof == [] : 
                list_prof.append('0')
            list_tot.append(list_prof)
            list_tot.append(list_time)
            dict_var[str(variable_name)]=list_tot
    except:
        raise
        print "Error in WMS procedure"
        sys.exit(1)
    return dict_var

def read_file(f):
  '''Read ncview colormaps_<name>.h file'''

  l=open(f).readlines()

  i=-1
  for k in l:
    i+=1
    if k.startswith('static'): break

  l=l[i:]

  i0=l[0].find('{')
  i1=l[-1].find('}')

  l[0]=l[0][i0+1:]
  l[-1]=l[-1][:i1]

  r=[]
  for i in range(len(l)):
    line=l[i].replace(',',' ').strip()
    vals=[int(j) for j in line.split()]
    r=np.hstack((r,vals))

  r.shape=r.size/3,3
  return r/255.


def gen_cmap(file,name='auto',N=None):
  '''Read ncview colormaps_<name>.h file'''
  if name=='auto': name=file.split('colormaps_')[-1][:-2]
  r=read_file(file)
  return pl.matplotlib.colors.ListedColormap(r, name=name, N=N)


##def show():
##  '''Display ncview colormaps'''
##
##  a=np.outer(np.arange(0,1,0.01),np.ones(10))
##  pl.figure(figsize=(8,5))
##  pl.subplots_adjust(top=0.8,bottom=0.05,left=0.05,right=0.95)
##
##  import glob
##  files=glob.glob('./colormaps_default.h')
##  files.sort()
##  maps=[gen_cmap(f) for f in files]
##
##  l=len(maps)+1
##  for i, m in enumerate(maps):



dir_statics=str(os.getcwd())+"/../statics/"
filename=dir_statics+"cmems_dic_tot_pit_V2_4.p"
f = file(filename, 'r')
var=cPickle.load(f)
## Initialization
list_prod=[]
list_WMS_avail_prod={}
frame='GLOBAL'
#list_frame=['ARCTIC','BAL','GLOBAL','IBI','MED','NWS']
list_frame=['GLOBAL']
##file_txt=dir_statics+"results_connexions_new_wms.txt"
### Write namelist file
##obFichier=open(file_txt,'w')
# Loop on keys
for key in var.keys():
  print key
  if key == "GLOBAL_ANALYSIS_FORECAST_PHY_001_024"  :
    for frame in list_frame :
    #  if frame in key : 
        list_WMS_avail_prod[key]={}
        list_prod.append(str(key))
        product=key
        print "------- Product ------------"
        #obFichier.write('------- Product ------------\n')
        #obFichier.write('---- %s ----\n'%(key))
        print('---- %s ----\n'%(key))
        print var[key].keys()
        for key2 in var[key] :
                print  "------ Variable -----------"
                print var[key][key2][0]
                print  "------ Time -----------"
                print var[key][key2][1]
                print  "------ Others -----------"
                print var[key][key2][2]
                print var[key][key2][3]
                print var[key][key2][4]
                adress=var[key][key2][5]
                print  "------ WMS adress -----------"
                print adress
                #getWMS(adress)
               # dict_var=getXML2(adress)

                try:
                    from owslib.wms import WebMapService
                except ImportError:
                    raise ImportError('OWSLib required to use wmsimage method')
                ##import urllib2, io
                ### find the x,y values at the corner points.
                ###p = pyproj.Proj(init="epsg:%s" % self.epsg, preserve_units=True)
                ### ypixels not given, find by scaling xpixels by the map aspect ratio.
                ##print adress
                wms = WebMapService(adress[0])
                formats=wms.getOperationByName('GetMap').formatOptions
                for form in formats :
                    print form.split('/')[1]
                print 'id: %s, version: %s' %\
                (wms.identification.type,wms.identification.version)
                print 'title: %s, abstract: %s' %\
                (wms.identification.title,wms.identification.abstract)
                print 'available layers:'
                layer_list=list(wms.contents)
                #print 'projection options:'
                print wms['thetao'].crsOptions
                options=wms['thetao'].crsOptions
                print options
                ## see all options dir(wms['thetao'])
                print "Styles"

                styles=wms['thetao'].styles
                print styles
                print dir(wms['thetao'])
                print " See all attributs" 
                print wms['thetao'].defaulttimeposition
                xmin=-180
                xmax=180
                ymin=-90
                ymax=90
                #xmin=-20
                #xmax=100
                #ymin=-20
                #ymax=40
                xpixels=1000
                aspect=0.5
                projection="mercator"
                #if projection == 'cyl':
                #    aspect = (urcrnrlat-llcrnrlat)/(urcrnrlon-llcrnrlon)
                #else:
                #    aspect = (ymax-ymin)/(xmax-xmin)
                #print aspect
                ypixels = int(aspect*xpixels)
                print ypixels
                format="jpeg"
                format="png"
                #plt.figure(figsize=(19.2,11.5))
                plt.figure(figsize=(20,12))
                variable='thetao'
                long_name=wms[variable].title
               # variable='bottomT'
                print options[2]
                #choose_style='boxfill/redblue'
                choose_style='boxfill/redblue'
                choose_style='boxfill/ncview'
                if choose_style == 'boxfill/redblue' : 
                    valuemap="bwr"
                elif choose_style == 'boxfill/rainbow' :
                    valuemap="jet"
                elif choose_style == 'boxfill/jet' :
                    valuemap="jet"
                elif choose_style == 'boxfill/ncview' :
                    valuemap="default"

                #choose_style='boxfill/jet'
                choose_legend=styles[choose_style]['legend']
                print choose_legend
                valmin='-5'
                valmax='35'
                numbercolor='20'
                nb_values=int(numbercolor)
                #mapper = cm.ScalarMappable(norm=norm, cmap=valuemap)
                intervalDiff = ( float(valmax) - float(valmin) )/(nb_values-1)
                print intervalDiff 
                rastermin=int(valmin)
                rastermax=int(valmax)
                value=rastermin
                norm = matplotlib.colors.Normalize(vmin=rastermin, vmax=rastermax, clip=True)
                items=[]
                item_ind=[]
                for class_val in range(0, nb_values):
                    val=float(class_val)/float(nb_values)
                    items.append(float('%.2f'%(value)))
                    item_ind.append(val)
                    value=value+intervalDiff
                print items
                rangeval="'"+str(valmin)+','+str(valmax)+"'"
                time_change="2017-01-20"
                norm_func = mpl.colors.Normalize
                norm = norm_func(vmin=rastermin, vmax=rastermax)
                #cmap = cm.jet
                #cmap = matplotlib.cm.get_cmap('Spectral')
                #print wms.getOperationByName('GetMap').formatOptions
                print [choose_style]
                print options[2]
                m = Basemap(llcrnrlon=xmin, urcrnrlat=ymax,
                                                  urcrnrlon=xmax, llcrnrlat=ymin,resolution='i',epsg=4326)
                print m.aspect
                img = wms.getmap(layers=[variable],service='wms',bbox=(xmin,ymin,xmax,ymax),
                                 size=(xpixels,ypixels),
                                 format='image/%s'%format,
                                 elevation='-0.49402499198913574',
                                 srs=options[2],
                                 time=time_change+'T12:00:00.000Z',
                                 colorscalerange=valmin+','+valmax,numcolorbands=numbercolor,logscale=False,
                                 styles=[choose_style],legend=choose_legend)
                                 #colorscalerange='-5,35',numcolorbands='100',logscale=False,
                colormap=choose_style.split('/')[1]
                files=glob.glob('./statics/colormaps_'+valuemap+'.h')
                files.sort()
                cmap=gen_cmap(files[0])
                cm.register_cmap(name='ncview', cmap=cmap)
                #,N=int(numbercolor))

                image=imread(io.BytesIO(img.read()))
                ##list_red=[]
                ##list_green=[]
                ##list_blue=[]

                ##for x in int(xpixels) :
                ##    for y in int(ypixels) :
                ##        red=image(image[x,y,0])
                ##        green=image(image[x,y,1])
                ##        blue=image(image[x,y,2])
                ##        list_red.append([red,green,blue]
               # print shape(image)
               # print '-- Red -------------'
               # print image[:,:,0]
               # print '-----Green----------'
               # print image[:,:,1]
               # print '-----Blue----------'
               # print image[:,:,2]
                ##def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
                ##    new_cmap = colors.LinearSegmentedColormap.from_list(
                ##         'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
                ##          cmap(np.linspace(minval, maxval, n)))
                ##    return new_cmap
                plt.imshow(image,cmap=(cm.get_cmap('ncview',int(numbercolor))))
                plt.colorbar()
                plt.savefig(product+"_"+long_name+"_"+time_change+"_new3.png",dpi=300,bbox_inches='tight')
                sys.exit(1)
           ##    # print image
                xparallels=20
                ymeridians=20
                font=16
                ylabel=wms[variable].abstract
                title=product+" - "+long_name+" "+" - "+time_change
                m.drawcoastlines(color='lightgrey',linewidth=0.25)
                m.fillcontinents(color='lightgrey')
                m.imshow(image,origin='upper',alpha=1,cmap=cmap,norm=norm)
                plt.colorbar()
                plt.show()
                sys.exit(1)
                cs=m.imshow(image,origin='upper',alpha=1,cmap=(cm.get_cmap(cmap,int(numbercolor))),norm=norm)
                #cs=m.imshow(image,origin='upper',alpha=1,cmap=(cm.get_cmap(valuemap,int(numbercolor))),norm=norm)
                #cs=m.imshow(image,origin='upper',alpha=1,norm=norm)
                #m.imshow(image,origin='upper',alpha=1)
                #cb=plt.colorbar(cs,orientation='vertical',format='%4.2f',pad=0.1,shrink=0.7)
                cb=plt.colorbar(cs,orientation='vertical',format='%4.2f',shrink=0.7)
                cb.ax.set_ylabel(ylabel, fontsize=int(font)+4)
                cl=plt.getp(cb.ax, 'ymajorticklabels')
                plt.setp(cl, fontsize=font)
                #plt.colorbar()
                plt.title(title,fontsize=font,y=1.05)
                parallels=np.round(np.arange(ymin,ymax+xparallels/2,xparallels))
                m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,linewidth=0.2)
                meridians = np.round(np.arange(xmin,xmax+ymeridians/2,ymeridians))
                m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,linewidth=0.2,dashes=[1, 5])
                plt.savefig(product+"_"+long_name+"_"+time_change+"_new3.png",dpi=300,bbox_inches='tight')
                plt.show()
           ##     sys.exit(1)
                #max_yticks = 5
                #yloc = plt.MaxNLocator(max_yticks)
               ## cbar = plt.colorbar(cmap=cm.get_cmap(valuemap))
               ## cbar.set_ticks(item_ind)
               ## cbar.set_ticklabels(items)
               ## cbar.ax.set_ylabel(long_name)
               ## cbar.ax.yaxis.set_major_locator(yloc)
                #cl=plt.getp(cbar.ax, 'ymajorticklabels')
               # plt.setp(cl, fontsize=12)
                #draw parallels
                # add colorbar 
                #cb.set_label(units)
                ##p = dict(cmin=int(valmin,
                ##         cmax=int(valmax),
                ##         width=500,
                ##         height=50,
                ##         colormap='jet',
                ##         showlabel=True,
                ##         units='degrees',
                ##         showvalues=True,
                ##         logscale=False,
                ##         numcontours=256)
                #fig = create_figure(p)
                ##alpha=0.5
                ##m.imshow(imread(io.BytesIO(img.read()),
                ##                format=format),origin='upper',alpha=alpha)#,ax=ax)
                #plt.show()

                ##print wms
                ##if verbose:
                ##    print 'id: %s, version: %s' %\
                ##    (wms.identification.type,wms.identification.version)
                ##    print 'title: %s, abstract: %s' %\
                ##    (wms.identification.title,wms.identification.abstract)
                ##    print 'available layers:'
                ##    print list(wms.contents)
                ##    print 'projection options:'
                ##    print wms[kwargs['layers'][0]].crsOptions
                ### remove keys from kwargs that are over-ridden
                ##for k in ['format','bbox','service','size','srs']:
                ##    if 'format' in kwargs: del kwargs['format']
                ##img = wms.getmap(service='wms',bbox=(xmin,ymin,xmax,ymax),
                ##                 size=(xpixels,ypixels),format='image/%s'%format,
                ##                 srs='EPSG:%s' % self.epsg, **kwargs)
                # return AxesImage instance.
                # this works for png and jpeg.
                # return AxesImage instance.
                # this works for png and jpeg.
                #return self.imshow(imread(io.BytesIO(urllib2.urlopen(img.url).read()),
                #                   format=format),origin='upper')
                # this works for png, but not jpeg
                #return self.imshow(imread(urllib2.urlopen(img.url),format=format),origin='upper')



                ##
            #obFichier.write('Dataset : %s  -- Connexion WMS : %s \n'%(key2,ll_request))
            #print ll_request
#obFichier.close()
print  "------ WMS Available -----------"
print list_WMS_avail_prod
## Write results in cpickle file
filetype=dir_statics+"cmems_wms_new_results.p"
ftype=file(filetype, 'wb')
cPickle.dump(list_WMS_avail_prod,ftype,protocol=cPickle.HIGHEST_PROTOCOL)
ftype.close

