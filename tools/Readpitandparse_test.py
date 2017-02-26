# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
# C.REGNIER : May 2016 : Parse Pit 
import cPickle
import csv,sys
global str
filecsv='/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/statics/PIT_v2.1_Charly_TEST_WMS.csv'
filecsv='/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/statics/CMEMS-v2.4-PIT-v2.1.csv'
#filecsv='/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/statics/pit.csv'
prod_name="Product Reference"
var_name="Variables"
dataset_name="Dataset Reference"
lonmin_name="Westward Longitude"
lonmax_name="Eastward Longitude"
latmin_name="Southward Latitude"
latmax_name="Northward Latitude"
time_start="Temporal Coverage Start"
time_end="Temporal Coverage End"

server_name="SUBSETTER Server Address"
DGF_name="DGF Server Address"
MFTP_name="MFTP Server Address"
wms_name="WMS Server Address"
depth_name="Vertical Level Number"
temporal_resolution="Temporal Resolution"


with open(filecsv, 'r') as csvfile:
    pitreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    print pitreader
    i=0
    liste_products=[]
    list_resol_type=[]
    dict_prod={}
    dict_dataset={}
    for row in pitreader:
        if i !=0 : 
            ## Read file
            list_var=''.join(row).split(';')
            #print description_var
            ## Find indice for product reference in the list 
            ind_prod=description_var.index(prod_name)
            ## Find indice for variable the list
            print var_name
            ind_var=description_var.index(var_name)
            ind_dataset=description_var.index(dataset_name)
            ##ind_lonmax=description_var.index(lonmax_name)
            ##ind_lonmin=description_var.index(lonmin_name)
            ##ind_latmax=description_var.index(latmax_name)
            ##ind_latmin=description_var.index(latmin_name)
            ind_startime=description_var.index(time_start)
            ind_endtime=description_var.index(time_end)
            ind_endtime=description_var.index(time_end)
            ind_server_motu=description_var.index(server_name)
            ind_DGF=description_var.index(DGF_name)
            ind_MFTP=description_var.index(MFTP_name)
            ind_WMS=description_var.index(wms_name)
            ind_depth=description_var.index(depth_name)
            ind_resol=description_var.index(temporal_resolution)
          # print ind_prod,ind_var
            ind=0
            ll_cpt=True
            list_variables=[]
            list_position=[]
            list_time=[]
            list_server_motu=[]
            list_DGF=[]
            list_MFTP=[]
            list_WMS=[]
            list_depth=[]
            list_resol=[]
            list_product_id=[]
            for var in list_var: 
                #print ind,var 
                if ind == 0 :
                    product_name=var 
                    if list_var[ind_prod] != '' : #and list_var[ind_prod] not in liste_products : 
                        liste_products.append(list_var[ind_prod])
                    ind=ind+1
                elif ind==ind_dataset :
                    dataset=var
                    print "Dataset %s" %(dataset)
                    # list_variables.append(dataset)
                    ind=ind+1
                elif ind == ind_server_motu :
                    print "----Var-------"
                    print var
                    print len(var)
                    if len(var) > 10 :
                       # print var
                       # print '-------'
                        if 'service' in var : 
                            service_id=var.split('service=')[1]
                            print service_id
                            if 'Motu' in var : 
                                motu_server=var.split('Motu')[0]+'Motu'
                            elif 'Subsetter' in var :
                                motu_server=var.split('Subsetter')[0]+'fiMisSubsetter'
                            else :
                                print "Probleme"
                                sys.exit(1)
                        else : 
                            motu_server=var
                        #print motu_server
                    else :
                        motu_server=var
                        service_id=var
                    list_server_motu.append(motu_server)
                    list_product_id.append(service_id)
                    ind=ind+1 
                elif ind == ind_DGF : 
                    list_DGF.append(var)
                    ind=ind+1 
                elif ind == ind_MFTP : 
                    list_MFTP.append(var)
                    ind=ind+1
                elif ind == ind_WMS : 
                    list_WMS.append(var)
                    ind=ind+1
                elif ind == ind_depth : 
                    list_depth.append(var)
                    ind=ind+1
                elif ind == ind_resol :
                    if var not in list_resol_type : 
                        list_resol_type.append(var)
                    list_resol.append(var)
                    ind=ind+1
                elif ind == ind_startime or ind == ind_endtime :
                    list_time.append(var)
                    ind=ind+1
                ##elif ind == ind_lonmax or ind == ind_lonmin: 
                ##    list_position.append(var)
                ##    ind=ind+1
                ##elif ind == ind_latmax:
                ##    list_position.append(var)
                ##    ind=ind+1
                ##elif ind == ind_latmin: 
                ##    ind=ind+1
                ##    list_position.append(var)
                elif  ind == ind_var : 
                    print "Variables"
                    print var
                    if var.startswith('"') or ll_cpt==False :
                        print "Dans le if"
                        if ll_cpt==False :
                            if  var.endswith('"') :
                                list_variables.append(var[:-1])
                                print "fin problem"
                                print ind
                                ll_cpt=True
                                ind=ind+1
                                print "cas 3"
                            else :
                                print "cas 1"
                                list_variables.append(var)
                        else :
                            print "cas 2"
                            if ll_cpt==True :
                                list_variables.append(var[1:])
                            else :
                                list_variables.append(var)
                            ll_cpt=False
                    else  :
                        list_variables.append(var)
                        ind=ind+1
                else:
                    if var == "":
                        ind=ind+1
                    else :
                        if var.startswith('"') or ll_cpt==False :
                            if ll_cpt==False :
                                if  var.endswith('"') :
                                    print "fin problem"
                                    print ind
                                    ll_cpt=True
                                    ind=ind+1
                            else :
                                ll_cpt=False
                        else :
                            ind=ind+1
        #   print list_var[ind_prod]
        #   print dataset
            if list_var[ind_prod] != '' : 
                if not list_var[ind_prod] in dict_prod :
                    dict_prod[list_var[ind_prod]]={}
                list_tot=[]
                list_tot.append(list_variables)
                #list_tot.append(list_position)
                list_tot.append(list_time)
                list_tot.append(list_server_motu)
                list_tot.append(list_DGF)
                list_tot.append(list_MFTP)
                list_tot.append(list_WMS)
                list_tot.append(list_depth)
                list_tot.append(list_resol)
                list_tot.append(list_product_id)
            for var in list_var: 
                dict_prod[list_var[ind_prod]][dataset]=list_tot
        else :
            ## Header
            print "inside header"
            print ''.join(row)
            description_var=''.join(row).split(';')
            print description_var
            print '--------------'
            sys.exit(1)
        i=i+1 
        if i>2 : 
          print dict_prod
          for key in dict_prod.keys():
              ##
              print "------- Product ------------"
              print key
              for key2 in dict_prod[key]: 
                 print  "------ Dataset -----------"
                 print key2
                 print  "------ Variable -----------"
                 print dict_prod[key][key2][0]
                 print  "------ Area -----------"
                 print dict_prod[key][key2][1]
                 print  "------ Time -----------"
                 print dict_prod[key][key2][2]
                 print  "------ Server -----------"
                 print dict_prod[key][key2][3]
                 print  "------ DGF -----------"
                 print dict_prod[key][key2][4]
                 print  "------ MFTP -----------"
                 print dict_prod[key][key2][5]
                 print  "------ WMS -----------"
                 print dict_prod[key][key2][6]
                 print  "------ Depth -----------"
                 print dict_prod[key][key2][7]
                 print  "------ Resolution -----------"
                 print dict_prod[key][key2][8]
              print "------------------------"
          sys.exit(1)
    print "Products list : ",liste_products
print "Nb products : %i " %(len(liste_products))
## Write Outpout file in cPickle
#filetype="/home/cregnier/DEV/Python/csv/cmems_dic_pit_test.p"
#filetype="/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/statics/cmems_dic_tot_pit_V2.1.p"
filetype="/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/statics/cmems_dic_tot_pit_V2_4.p"
ftype=file(filetype, 'wb')
cPickle.dump(dict_prod,ftype,protocol=cPickle.HIGHEST_PROTOCOL)
ftype.close
## Tests
#### Find the list of global ##
print "Type de resolution"
print list_resol_type
frame="GLOBAL"
list_prod=[]
for key in dict_prod.keys():
    if frame in key :
        list_prod.append(str(key))
print list_prod
for key in dict_prod.keys():
    ##
    print "------- Product ------------"
    print key
    for key2 in dict_prod[key]: 
        print  "------ Dataset -----------"
        print key2
        print "motu"
        print dict_prod[key][key2][3]
        print "wms"
        print dict_prod[key][key2][6]
        print  "------ Variable -----------"
        print dict_prod[key][key2][0]
        print  "------ Area -----------"
        print dict_prod[key][key2][1]
        print  "------ Time -----------"
        print dict_prod[key][key2][2]
        print  "------ Server -----------"
        print dict_prod[key][key2][3]
        #print "product_id"
        #print dict_prod[key][key2][7]
    print "------------------------"
#    print dict_prod
