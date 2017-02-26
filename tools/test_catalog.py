import cPickle
import csv,sys
filetype="/home/cregnier/SVN/mo/TEP/SIG/branches/Charly_V0/statics/cmems_dic_tot_pit_V2_4.p"
dict_var={}
f = file(filetype, 'r')
self.dict_prod=cPickle.load(f)
print "Read pit  ok"
## Tests
frame="GLOBAL"
list_prod=[]
print dict_prod
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
        #print "product_id"
        #print dict_prod[key][key2][7]
    print "------------------------"
#    print dict_prod
