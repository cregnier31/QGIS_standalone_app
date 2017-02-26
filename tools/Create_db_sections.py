# coding: utf8
## Create pickle files with the definition of Sections
## C.REGNIER Feb 2016
##
import cPickle
dict_tot={}
dict_sect={}
## Arctique
dict_sect['WOCE A01W']=['Arctic',(-56.4,53),(-49,61.5)]
## Atlantique
dict_sect['OVIDE CLIVAR A25']=['Antarctic',(43.5,60),(-7.8,38)]
dict_sect['Biscay WOCE AR12D']=['Antarctic',(-4.7,48.4),(-8,43.6)]
dict_sect['Atlantique 67W']=['Antarctic',(-67,10),(-67,46)]
dict_sect['Yucatan Strait KANEC']=['Antarctic',(-87.3,21),(-84,22.2)]
dict_sect['Atlantic-Equador']=['Antarctic',(-51,0),(12,0)]
dict_sect['0E WOCEA12 CLIVAR A13']=['Antarctic',(0,6.5),(0,-71)]
dict_sect['Gulf Guinea 6E']=['Antarctic',(6,5.5),(6,-28)]
dict_sect['Cuba-Florida']=['Antarctic',(-80.5,22.5),(-80.5,25.5)]
dict_sect['Drake Passage']=['Antarctic',(-68,-55),(-60,-64)]
## Mediterranée
dict_sect['Mediterranean OE']=['Mediterranean',(0.0,38.75),(0.0,35.36)]
dict_sect['Sete-Tunis']=['Mediterranean',(3,43),(10,37)]
dict_sect['Cretan Passage']=['Mediterranean',(25,31.5),(25,35.05)]
dict_sect['Gulf de Cadiz WOCE AR16D']=['Mediterranean',(-8.7,32,4),(-8.7,37.2)]
## Indien
dict_sect['Indian-Equator']=['Indian',(40,0),(101,0)]
dict_sect['Indian Fremantle-SuLabradorndraStait']=['Indian',(105.7,-6),(115.7,-34.5)]
dict_sect['Indian Moonson Reversal']=['Indian',(80,7),(80,-15)]
dict_sect['Indian-Mada']=['Indian',(39,-5),(49,-13.5)]
## Pacifique
dict_sect['Pacific 137E']=['Pacific',(137,-2.5),(137,37)]
dict_sect['Pacific-Equator']=['Pacific',(120,0),(-78,0)]
dict_sect['Hawaï -NewZealand']=['Pacific',(-156,20),(175,-38)]
dict_sect['Le Cap-Antarctic']=['Pacific',(20,-70),(20,-34)]
dict_sect['Kuroshio']=['Pacific',(132.8,33),(137,26)]
# Antarctique
dict_sect['Hobart-DumontDurville']=['Antarctic',(146,-42.8),(140,-66.4)]
dict_sect['Tasmania-Antarctic']=['Antarctic',(145,-68),(145,-38)]
dict_sect['Cross equatorial Atlantic']=['Antarctic',(-23,60),(-23,-60)]
dict_sect['Aghulas_current']=['Antarctic',(10,-40),(20,-33)]
filename="/home/cregnier/DEV/Docker/statics/Def_section.p"
f = file(filename, 'wb')
cPickle.dump(dict_sect,f,protocol=cPickle.HIGHEST_PROTOCOL)
f.close

print 'Validation'
#Validation 
filename="/home/cregnier/DEV/Docker/statics/Def_section.p"
f = file(filename, 'r')
var=cPickle.load(f)
for item,variable in var.items():
   print [0]
    #for item2,var2 in variable:
   print "----------------------"
   #print item2,var2
#print var.keys()

