# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#!/usr/bin/env python
## C.REGNIER : Test all CMEMS WMS adress and save in a cPickle and text file
import sys,os
import xml.etree.ElementTree as ET
import os,urllib2
import cPickle

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
                dict_var=getXML2(adress)
                ##
                sys.exit(1)
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

