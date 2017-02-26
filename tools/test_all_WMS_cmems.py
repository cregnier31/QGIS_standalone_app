# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
#!/usr/bin/env python
## C.REGNIER : Test all CMEMS WMS adress and save in a cPickle and text file
import sys,os
import xml.etree.ElementTree as ET
import os,urllib2
import cPickle

def getXML(url_base):
    mercator_url1="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-002"
    mercator_url2="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-002-2hourly-t-u-v-ssh"
    ll_request=False 
    if url_base is mercator_url1 or url_base is mercator_url2 :
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
    #url_base="http://nrtcmems.mercator-ocean.fr/thredds/wms/global-analysis-forecast-phys-001-002"
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


dir_statics=str(os.getcwd())+"/../statics/"
filename=dir_statics+"cmems_dic_tot_pit_V2.1.p"
filename=dir_statics+"cmems_dic_tot_pit_V2_4.p"
f = file(filename, 'r')
var=cPickle.load(f)
## Initialization
list_prod=[]
list_WMS_avail_prod={}
print "OK"
frame='GLOBAL'
list_frame=['ARCTIC','BAL','GLOBAL','IBI','MED','NWS']
file_txt=dir_statics+"results_connexions_new_wms.txt"
# Write namelist file
obFichier=open(file_txt,'w')
# Loop on keys
for key in var.keys():
    for frame in list_frame :
    #  if frame in key : 
        list_WMS_avail_prod[key]={}
        list_prod.append(str(key))
        print "------- Product ------------"
        obFichier.write('------- Product ------------\n')
        obFichier.write('---- %s ----\n'%(key))
        print key
        for key2 in var[key]: 
            print  "------ Dataset -----------"
            print key2
            print  "------ WMS adress -----------"
            print var[key][key2][5]
            adress=var[key][key2][5][0]
            ll_request=getXML(adress)
            list_WMS_avail_prod[key][key2]=ll_request
            obFichier.write('Dataset : %s  -- Connexion WMS : %s \n'%(key2,ll_request))
            print ll_request
obFichier.close()
print  "------ WMS Available -----------"
print list_WMS_avail_prod
## Write results in cpickle file
filetype=dir_statics+"cmems_wms_new_results.p"
ftype=file(filetype, 'wb')
cPickle.dump(list_WMS_avail_prod,ftype,protocol=cPickle.HIGHEST_PROTOCOL)
ftype.close

