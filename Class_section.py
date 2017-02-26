# coding: utf8
import netCDF4
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as col
import datetime
import time
import os, sys,re,math
from mpl_toolkits.basemap import Basemap,shiftgrid
from mpl_toolkits.axes_grid1.inset_locator import inset_axes          
from PIL import Image
import multiprocessing as mp
#from pathos.multiprocessing import ProcessingPool as Pool
print "import pathos"
from pathos import multiprocessing as pathos_mp
##
## Class to compute Trnasect in a 3D grid
## C.REGNIER and M.Tressol January 2015
##
class Tools:

    def lookupNearest(self,x0, y0,lon,lat):
       xi = np.abs(lon-x0).argmin()
       yi = np.abs(lat-y0).argmin()
       return xi,yi


    def get_date(self,date_as_string):
        if date_as_string == None:
                return None

        year = date_as_string[0:4]
        month = date_as_string[4:6]
        day = date_as_string[6:8]
        try:
                date = datetime.datetime(int(year),int(month),int(day))
        except ValueError:
                date = None
        return date

    def AddLogo(self,mfname, lfname, outfname):
        mimage = Image.open(mfname)
        limage = Image.open(lfname)
        box = (0,8)
        mimage.paste(limage, box)
        mimage.save(outfname)

    def FileExists(file_name):
            if os.path.exists(file_name):
                    return True
            else:
                print " "
                print " "
                print " ==== ERROR ====  "
                print " "
                print " File "+ file_name+ " does not exist"
                sys.exit()

class Section(Tools):
    def __init__(self):
        self.dpi=200
        self.dim_titre = 10
        self.dim_coltext= 10 
        self.RT=6378
        self.rr=np.pi/180.0
    def insert_and_process_helper(self,args):
        return self.loop_optim(*args)
    def loop_optim(self,s,latsec,lonsec,X1,N1,N2,lat,lon,latitude,longitude,p,d,cont,offset,plotvar,sectvar) :
           mx=len(longitude)
           my=len(latitude)
           miniT=1000
           # Find closest point (orthrodomic distance)
           rr=self.rr
           RT=self.RT
           ddlat=np.cos(latitude*rr)*np.cos(latsec[s]*rr)+np.sin(latitude*rr)*np.sin(latsec[s]*rr)
           ddlon=np.cos(longitude*rr-lonsec[s]*rr)
           for i in range(mx):
               for j in range(my):
                  if ddlat[j]*ddlon[i] >1.0:
                     dtmp=0.0
                  else:
                     dtmp=RT*np.arccos(ddlat[j]*ddlon[i])
                  if dtmp<miniT :
                     miniT=dtmp
                     iiT=i
                     jjT=j
           # Interpolation des champs
           if lonsec[s]>=longitude[iiT] :
               iinf=iiT
               if (iiT+1)<=mx :
                   isup=iiT+1
               else :
                   isup=1
           else :
               if (iiT-1)>=1 :
                   iinf=iiT-1
               else :
                   iinf=mx
               isup=iiT
           if latsec[s]>=latitude[jjT] :
               jinf=jjT
               jsup=jjT+1
           else :
               jinf=jjT-1
               jsup=jjT
           if iinf>=len(longitude) :
               iinf=iinf-1
           if isup>=len(longitude) :
               isup=isup-1
           loninf=longitude[iinf]
           lonsup=longitude[isup]
           latinf=latitude[jinf]
           latsup=latitude[jsup]
           if lonsup == loninf:
              lonsup = loninf +0.000001
           if latsup == latinf:
              latsup = latinf +0.00000
           a=(lonsec[s]-loninf)/(lonsup-loninf)
           b=(lonsup-lonsec[s])/(lonsup-loninf)
           c=(latsec[s]-latinf)/(latsup-latinf)
           e=(latsup-latsec[s])/(latsup-latinf)
           sectvar[:,:,s]=c*(a*plotvar[:,:,jsup,isup]+b*plotvar[:,:,jsup,iinf])+e*(a*plotvar[:,:,jinf,isup]+b*plotvar[:,:,jinf,iinf])
           #print "END loop %i " %(s)
           #print "---------------"
           return sectvar[:,:,s]
    def sect_compute_optim(self,longitude,latitude,depth,time_counter,plotvar,Nsec,latref,lonref,lon,lat) :
        """ Cette fonction calcule les valeurs le long de la section"""
        tic = time.time()
        # Check data coherence
        if len(lat)-1!=Nsec or len(lon)-1!=Nsec :
            print "Error between section number and lat-lon-nbpoint parameters"
            sys.exit()
        #---- Earth radius in km :
        RT=6378
        rr=np.pi/180.0
        mx=len(longitude)
        my=len(latitude)
        mdepth=len(depth)
        mtime_counter=len(time_counter)
        if Nsec == 1 :
           N=[]
           dist=RT * np.arccos(np.cos(lat[0]*rr)*np.cos(lat[1]*rr)*np.cos(lon[1]*rr-lon[0]*rr)+np.sin(lat[0]*rr)*np.sin(lat[1]*rr)) 
        ##   if dist > 2000 :
        ##     resol= 100
        ##   elif dist < 2000 and dist > 500 : 
        ##     resol=25
        ##   elif dist < 500  :
        ##     resol=10
           if dist > 3000 : 
              resol= 25 
           elif dist < 3000 and dist > 500 :
              resol=15 
           elif dist < 500  :
             resol=5 
           Ntot=int(dist/resol)
           N.append(Ntot)
        else :
           print "Nombre de sections : %i" %(Nsec)
           N=[]
           for sec in range(Nsec) :
             dist=RT * np.arccos(np.cos(lat[sec]*rr)*np.cos(lat[sec+1]*rr)*np.cos(lon[sec+1]*rr-lon[sec]*rr)+np.sin(lat[sec]*rr)*np.sin(lat[sec+1]*rr)) 
             if dist > 2000 :
               resol= 100
             elif dist < 2000 and dist > 500 : 
               resol=25
             elif dist < 500  :
               resol=10
             Ntot=int(dist/resol)
             N.append(Ntot)
        # -------------
        # COMPUTE PART
        # Compute sections length and find associated models points
        Ntot=np.sum(N)
        print "****************** Total number of points   :", Ntot
        # Loop over sections to paste
        N2=0
        # Reference point for section distance (ex : for Ovide 60N 43.25W):compute orthodromic distance
        offset=RT*np.arccos(np.cos(latref*rr)*np.cos(lat[1]*rr)*np.cos((lonref)*rr-lon[1]*rr)+np.sin(latref*rr)*np.sin(lat[1]*rr))
        cont=0
        d=[]
        latsec=[]
        lonsec=[]
        X1=[]
        sectvar=np.nan*np.ma.zeros([mtime_counter,mdepth,Ntot])
        sectvar_new=np.nan*np.ma.zeros([mtime_counter,mdepth,Ntot])
        pool_size = mp.cpu_count()*2 
        for p in np.arange(Nsec):
                N1=N2+1
                N2=N1+N[p]-1
                # Section length in km : compute orthodromic distance
                d.append(RT * np.arccos(np.cos(lat[p]*rr)*np.cos(lat[p+1]*rr)*np.cos(lon[p+1]*rr-lon[p]*rr)+np.sin(lat[p]*rr)*np.sin(lat[p+1]*rr)))
                print "**** Section ",p," = ",d[p], "km"
                print" - from (lat,lon) = (",lat[p],lon[p],") to (",lat[p+1],lon[p+1],")"
                # Section 1 slope in radians/equator (algebric angle)
                if lon[p]!=lon[p+1] :
                    ang=np.arctan((lat[p+1]-lat[p])/(lon[p+1]-lon[p]))
                else :
                    ang=np.pi/2
                print " - angle / equator (deg) = ",ang/rr
                # Coordinates of all sections points in (lon,lat) and in km :
                for s in np.arange(N1-1,N2) :
                    latsec.append((lat[p+1]-lat[p])*float(s-N1+cont)/float(N2-N1+cont)+lat[p])
                    lonsec.append((lon[p+1]-lon[p])*float(s-N1+cont)/float(N2-N1+cont)+lon[p])
                    X1.append(d[p]*float(s-N1+cont)/float(N2-N1+cont)+offset)
                values=[ s for s in np.arange(N1-1,N2)  ]
                list_test=[]
                jobs=[(s,latsec,lonsec,X1,N1,N2,lat,lon,\
                       latitude,longitude,p,d,cont,offset,plotvar,sectvar) for s in np.arange(N1-1,N2)  ]
                #pool=Pool(processes=pool_size,maxtasksperchild=2)
                #pool=Pool(processes=pool_size)
                pool=pathos_mp.Pool(processes=pool_size)
                print "-----------Launch optimization-----------------"
                var=pool.map(self.insert_and_process_helper,jobs)
                #sectvar_new=np.nan*np.ma.zeros([mtime_counter,mdepth,Ntot])
                print Ntot,N1-1,N2
                ind=0
                for s in np.arange(N1-1,N2) :
                   sectvar_new[:,:,s]=var[ind]
                   ind=ind+1
                cont=1
                del (pool)
                del (var)
                del (jobs)
        toc = time.time()
        print '| %6d sec for computation       |' %(toc-tic)
        return X1,lonsec,latsec,sectvar_new
###
    def sect_compute(self,longitude,latitude,depth,time_counter,plotvar,Nsec,latref,lonref,lon,lat) :
        """ Cette fonction calcule les valeurs le long de la section"""
        tic = time.time()
        # Check data coherence
        if len(lat)-1!=Nsec or len(lon)-1!=Nsec :
            print "Error between section number and lat-lon-nbpoint parameters"
            sys.exit()
        #---- Earth radius in km :
        RT=6378
        rr=np.pi/180.0
        mx=len(longitude)
        my=len(latitude)
        mdepth=len(depth)
        mtime_counter=len(time_counter)
        # -------------
        # COMPUTE PART
        # Compute sections length and find associated models points
        # Loop over sections to paste
        N2=0
        # Reference point for section distance (ex : for Ovide 60N 43.25W):compute orthodromic distance
        offset=RT*np.arccos(np.cos(latref*rr)*np.cos(lat[1]*rr)*np.cos((lonref)*rr-lon[1]*rr)+np.sin(latref*rr)*np.sin(lat[1]*rr))
        cont=0
        d=[]
        latsec=[]
        lonsec=[]
        X1=[]
        if Nsec == 1 :
           N=[]
           dist=RT * np.arccos(np.cos(lat[0]*rr)*np.cos(lat[1]*rr)*np.cos(lon[1]*rr-lon[0]*rr)+np.sin(lat[0]*rr)*np.sin(lat[1]*rr)) 
           if dist > 2000 :
             resol= 100
           elif dist < 2000 and dist > 500 : 
             resol=25
           elif dist < 500  :
             resol=10
           Ntot=int(dist/resol)
           N.append(Ntot)
        else :
           N=[]
           for sec in range(Nsec) :
             dist=RT * np.arccos(np.cos(lat[sec]*rr)*np.cos(lat[sec+1]*rr)*np.cos(lon[sec+1]*rr-lon[sec]*rr)+np.sin(lat[sec]*rr)*np.sin(lat[sec+1]*rr)) 
             if dist > 2000 :
               resol= 100
             elif dist < 2000 and dist > 500 : 
               resol=25
             elif dist < 500  :
               resol=10
             Ntot=int(dist/resol)
             N.append(Ntot)
             print N
        Ntot=np.sum(N)
        print Ntot
        sectvar=np.nan*np.ma.zeros([mtime_counter,mdepth,Ntot])
        print "****************** Number of points   :", Ntot
        print "launch loop"
        for p in np.arange(Nsec):
                N1=N2+1
                N2=N1+N[p]-1
                # Section length in km : compute orthodromic distance
                d.append(RT * np.arccos(np.cos(lat[p]*rr)*np.cos(lat[p+1]*rr)*np.cos(lon[p+1]*rr-lon[p]*rr)+np.sin(lat[p]*rr)*np.sin(lat[p+1]*rr)))
                print "**** Section ",p," = ",d[p], "km"
                print" - from (lat,lon) = (",lat[p],lon[p],") to (",lat[p+1],lon[p+1],")"
                # Section 1 slope in radians/equator (algebric angle)
                if lon[p]!=lon[p+1] :
                    ang=np.arctan((lat[p+1]-lat[p])/(lon[p+1]-lon[p]))
                else :
                    ang=np.pi/2
                print " - angle / equator (deg) = ",ang/rr
                # Coordinates of all sections points in (lon,lat) and in km :
                for s in np.arange(N1-1,N2) :
                    print s
                    latsec.append((lat[p+1]-lat[p])*float(s-N1+cont)/float(N2-N1+cont)+lat[p])
                    lonsec.append((lon[p+1]-lon[p])*float(s-N1+cont)/float(N2-N1+cont)+lon[p])
                    X1.append(d[p]*float(s-N1+cont)/float(N2-N1+cont)+offset)
                    miniT=1000
                    # Find closest point (orthrodomic distance)
                    ddlat=np.cos(latitude*rr)*np.cos(latsec[s]*rr)+np.sin(latitude*rr)*np.sin(latsec[s]*rr)
                    ddlon=np.cos(longitude*rr-lonsec[s]*rr)
                    for i in range(mx):
                        for j in range(my):
                           if ddlat[j]*ddlon[i] >1.0:
                              dtmp=0.0
                           else:
                              dtmp=RT*np.arccos(ddlat[j]*ddlon[i])
                           if dtmp<miniT :
                              miniT=dtmp
                              iiT=i
                              jjT=j
                    # Interpolation des champs
                    if lonsec[s]>=longitude[iiT] :
                        iinf=iiT
                        if (iiT+1)<=mx :
                            isup=iiT+1
                        else :
                            isup=1
                    else :
                        if (iiT-1)>=1 :
                            iinf=iiT-1
                        else :
                            iinf=mx
                        isup=iiT
                    if latsec[s]>=latitude[jjT] :
                        jinf=jjT
                        jsup=jjT+1
                    else :
                        jinf=jjT-1
                        jsup=jjT
                    if iinf>=len(longitude) :
                        iinf=iinf-1
                    if isup>=len(longitude) :
                        isup=isup-1
                    loninf=longitude[iinf]
                    lonsup=longitude[isup]
                    latinf=latitude[jinf]
                    latinf=latitude[jinf]
                    latsup=latitude[jsup]
                    if lonsup == loninf:
                       lonsup = loninf +0.000001
                    if latsup == latinf:
                       latsup = latinf +0.000001
		    a=(lonsec[s]-loninf)/(lonsup-loninf)
                    b=(lonsup-lonsec[s])/(lonsup-loninf)
                    c=(latsec[s]-latinf)/(latsup-latinf)
                    e=(latsup-latsec[s])/(latsup-latinf)
                    sectvar[:,:,s]=c*(a*plotvar[:,:,jsup,isup]+b*plotvar[:,:,jsup,iinf])+e*(a*plotvar[:,:,jinf,isup]+b*plotvar[:,:,jinf,iinf])
                cont=1
                print sectvar.shape
                offset=X1[N2-1]
        toc = time.time()
        print sectvar
        print '| %6d sec for computation        |' %(toc-tic)
        return X1,lonsec,latsec,sectvar


    def sectplot(self,X1,lonsec,latsec,depth,sectvar,lgname,unite,nom_reg,echeance_name,nom_abg,date_str,date_run,rep_out,ndpi,dim_titre,dim_coltext,SystName,cmap_banded,list_param):
            """Cette fonction trace les sections"""
            print 'Inside sectplot'
            print list_param
            print "-------------"
            tic = time.time()
            cmap1 = col.LinearSegmentedColormap('cmap_banded',cmap_banded,N=256)
            ave_sectvar=np.mean(sectvar[np.where(np.isnan(sectvar)==False)])
            std_dev=np.std(sectvar[np.where(np.isnan(sectvar)==False)])
            sectvar=np.where(sectvar.mask==True,np.nan,sectvar)
            sectvar=sectvar[0,:,:]
            if list_param :
               print "List param exist" 
               minvalue=np.float(list_param[0])
               maxvalue=np.float(list_param[1])
               stepvalue=np.float(list_param[2])
               print minvalue,maxvalue,stepvalue
               minplotvar=minvalue
               maxplotvar=maxvalue
               numlevsvar=np.arange(minvalue,maxvalue+stepvalue/2.,stepvalue)
            else : 
               print "List param doesn t exist" 
               ave_sectvar=np.mean(sectvar[np.where(np.isnan(sectvar)==False)])
               std_dev=np.std(sectvar[np.where(np.isnan(sectvar)==False)])
               minplotvar=ave_sectvar-2*std_dev
               maxplotvar=ave_sectvar+2*std_dev
               numlevsvar=np.arange(minplotvar,maxplotvar+maxplotvar/2.,(maxplotvar-minplotvar)/10.)
            numlevscol=[ ('%4.2f'%v).rjust(5) for v in numlevsvar]
            # Utilisation de 250 couleurs pour plot
            numlevs=np.linspace(minplotvar,maxplotvar,250)
            # Cherche le dernier niveau avec nan exclusivement
            limzz=len(depth)
            flag_ok=False
            limz=len(depth)-1
            for zz in range(len(depth)) :
                if np.isnan(sectvar[zz,:]).all()==True and flag_ok==False :
                    limz=zz
                    flag_ok=True
            limit_ax1=36
            print limz,limit_ax1
            if limz <= limit_ax1 :
                # Ouverture figure 
                fig = plt.figure()
                width=600.; height=400. ; dpi=75.
              #  width=600.; height=500. ; dpi=300.
                fig.set_size_inches(width/dpi, height/dpi)
                fig.subplots_adjust(bottom=0.2)
                ax = fig.add_subplot(1,1,1)
                cs=ax.contourf(X1,0-depth[0:limz],sectvar[0:limz,:],numlevs,cmap=cmap1,extend="both")
                stride=int(len(X1)/8) #pour huit ticks
                # cas de longitude constante
                if lonsec[0]==lonsec[-1] :
                   cs.ax.set_xticks([X1[0],X1[-1]])
                   cs.ax.set_xticklabels([lonsec[0],lonsec[-1]])
                else:
                   lonlab=['%5.1f'%v for v in lonsec]
                   cs.ax.set_xticks(X1[::stride])
                   cs.ax.set_xticklabels(lonlab[::stride])
                cs.ax.set_ylim([np.floor(0-depth[limz]),0.01])
                cs.ax.tick_params(labelsize=int(dim_coltext)-2)
                cs.ax.set_xlabel("Longitude (${^\circ}$)", fontsize=int(dim_coltext))
                cs.ax.set_ylabel("Depth (m)", fontsize=int(dim_coltext))
                cb = plt.colorbar(cs)
            elif limz > limit_ax1: 
                # Ouverture figure + 2 axes 
                fig,(ax1,ax2) = plt.subplots(2,1,sharex=True)
                width=600.; height=400. ; dpi=75.
                fig.set_size_inches(width/dpi, height/dpi)
                plt.subplots_adjust(hspace = .005)
                cs1=ax1.contourf(X1,0-depth[0:limit_ax1],sectvar[0:limit_ax1,:],numlevs,cmap=cmap1,extend="both")
                cs2=ax2.contourf(X1,0-depth[limit_ax1:limz],sectvar[limit_ax1:limz,:],numlevs,cmap=cmap1,extend="both")
                stride=int(len(X1)/8) #pour huit ticks
                # cas de longitude constante
                if lonsec[0]==lonsec[-1] :
                        cs2.ax.set_xticks([X1[0],X1[-1]])
                        cs2.ax.set_xticklabels([lonsec[0],lonsec[-1]])
                else:
                        lonlab=['%5.1f'%v for v in lonsec]
                        cs2.ax.set_xticks(X1[::stride])
                        cs2.ax.set_xticklabels(lonlab[::stride])
                ax1.set_ylim([np.floor(0-depth[limit_ax1-1]),0.01])
                ax1.xaxis.tick_top()
                ax1.tick_params(labeltop='off', top='off')
                ax1.spines['bottom'].set_visible(False)
                ax2.spines['top'].set_visible(False)
                ax2.xaxis.tick_bottom()
                ax1.tick_params(labelsize=int(dim_coltext)-2)
                ax2.tick_params(labelsize=int(dim_coltext)-2)
                ax2.set_xlabel("Longitude (${^\circ}$)", fontsize=int(dim_coltext))
                plt.text(-0.1,0.0,"Depth (m)",verticalalignment='center',fontsize=int(dim_coltext),rotation='vertical',transform=ax1.transAxes)
                fig.subplots_adjust(right=0.8)
                cbar_ax = fig.add_axes([0.85, 0.1, 0.025, 0.8])
                cb = fig.colorbar(cs1, cax=cbar_ax)
            cb.set_label(lgname+' ('+unite+')',fontsize=int(dim_coltext))
            cb.set_ticks(numlevsvar)
            cb.set_ticklabels(numlevscol)
            cb.ax.tick_params(labelsize=int(dim_coltext)-2)

            if limz <= limit_ax1:
               newax = fig.add_axes(ax.get_position())
            elif limz > limit_ax1:
               newax = fig.add_axes(ax2.get_position())

            newax.spines['top'].set_visible(False)
            newax.xaxis.tick_bottom()
            newax.spines['right'].set_visible(False)
            newax.spines['left'].set_visible(False)

            newax.spines['bottom'].set_position(('outward', 50))
            newax.patch.set_visible(False)
            newax.yaxis.set_visible(False)
            newax.contourf(X1,depth[0:limz],sectvar[0:limz,:]*np.nan)
            if latsec[0]==latsec[-1] :
               newax.set_xticks([X1[0],X1[-1]])
               newax.set_xticklabels([latsec[0],latsec[-1]])
            else: 
               latlab=['%5.1f'%v for v in latsec]
               newax.set_xticks(X1[::stride])
               newax.set_xticklabels(latlab[::stride])
            newax.set_xlabel("Latitude (${^\circ}$)",fontsize=int(dim_coltext))	
            newax.tick_params(labelsize=int(dim_coltext)-2)	

            date_image_english=self.get_date(date_str)
            date_image_english=date_image_english.strftime("%Y-%m-%d")
            print date_image_english
            print date_run
            date_run_english=self.get_date(date_run)
            date_run_english=date_run_english.strftime("%Y-%m-%d")
            print date_image_english,echeance_name,date_run_english,nom_reg
            titre_plt=SystName+"\n"+"Date: "+date_image_english+' '+echeance_name+ " - Run Date: "+date_run_english+"\n"+nom_reg
            #titre_plt=unicode(titre_plt, "utf-8")
            nomvar_plt=lgname+" ("+unite+")"
            if limz <= limit_ax1:	
               plt.title(titre_plt,fontsize=int(dim_titre),horizontalalignment='center',verticalalignment='bottom')
            elif limz > limit_ax1:
               plt.text(0.5,1.05,titre_plt,horizontalalignment='center',fontsize=int(dim_coltext),transform=ax1.transAxes)
            # Insert small map in lower right corner
            lon_min=np.min(lonsec)
            lon_max=np.max(lonsec)
            lat_min=np.min(latsec)
            lat_max=np.max(latsec)
            delta_lon=lon_max-lon_min
            delta_lat=lat_max-lat_min
            if lon_min==lon_max :
               if lon_min>-170 :
                 lon_min=lon_min-10
               if lon_max<170 :
                  lon_max=lon_max+10
            if lat_min==lat_max :
               if lat_min>-80 :
                  lat_min=lat_min-10
               if lat_max<80 :
                  lat_max=lat_max+10
            if limz <= limit_ax1:
               axin = inset_axes(ax, width="20%", height="20%", loc=4, \
                 bbox_to_anchor=(0.22,-0.22,1,1),bbox_transform=ax.transAxes,borderpad=0)
            elif limz > limit_ax1:
               axin = inset_axes(ax2, width="30%", height="30%", loc=4, \
                 bbox_to_anchor=(0.19,-0.40,1,1),bbox_transform=ax2.transAxes,borderpad=0)
            inmap = Basemap(lon_0=(lon_max+lon_min)/2,lat_0=(lat_max+lat_min)/2, \
            projection='ortho', resolution ='l', \
            area_thresh=1000.,ax=axin,anchor='NE')
            inmap.fillcontinents()
            xx,yy=inmap(lonsec,latsec)
            _ = inmap.plot(xx, yy, 'r')
            # On sauvegarde l'image
            nom_image=SystName+'_'+date_str+'_'+nom_abg+"_"+lgname.replace(' ','_').lower()+".png"
            plt.savefig(rep_out+'/'+nom_image,dpi=ndpi,bbox_inches="tight",pad_inches=0.2)
            #self.AddLogo(rep_out+'/'+nom_image,rep_out+"../statics/logo_mercator.png",rep_out+'/'+nom_image)
            plt.show()
            toc = time.time()
            print '| %6d sec for plot       |' %(toc-tic)
            # plt.close()

    def sect_extract(self,x_list,y_list,fileName,variable,nb_flag) :
        """Cette fonction retourne les variables sur la zone geographique qui nous interesse"""
        tic = time.time()
        nsect=len(x_list)-1
        # Flag pour section coupant le meridien 180
        flag_sect=nb_flag
        # Chargement longitude latitude et variable
        #print "Filename %s " %(str(fileName))
        nc_file=netCDF4.Dataset(str(fileName),'r')
        longitude=nc_file.variables['longitude'][:]
        latitude=nc_file.variables['latitude'][:]
        profondeur=nc_file.variables['depth'][:]
        time_counter=nc_file.variables['time_counter'][:]
        #print x_list[0],y_list[0],longitude,latitude
        xi,yi=self.lookupNearest(x_list[0],y_list[0],longitude,latitude)
        lonref=longitude[int(xi)+1]
        latref=latitude[int(yi)+1]
        x_list_new=[]
        y_list_new=[]
        ind=0
        for var in x_list: 
            xi,yi=self.lookupNearest(x_list[ind],y_list[ind],longitude,latitude)
            xi,yi=self.lookupNearest(x_list[ind],y_list[ind],longitude,latitude)
            x_list_new.append(xi)
            y_list_new.append(yi)
            ind=ind+1
        lon_list=[longitude[v] for v in x_list_new]
        lat_list=[latitude[v] for v in y_list_new]
        # Order correctly index and get extracted area
        ind_xmin=min(x_list_new)
        ind_xmax=max(x_list_new)
        ind_ymin=min(y_list_new)
        ind_ymax=max(y_list_new)
        # extand area for interpolation
        if longitude[ind_xmin]>min(longitude)+2:
            ind_xmin=ind_xmin-15
        if longitude[ind_ymin]<max(longitude)-2:
            ind_xmax=ind_xmax+15
        if latitude[ind_ymin]>min(latitude)+2:
            ind_ymin=ind_ymin-15
        if latitude[ind_ymin]<max(latitude)-2:
            ind_ymax=ind_ymax+15
        latitude=latitude[ind_ymin:ind_ymax]
        if flag_sect==1 :
            lon_o=longitude[ind_xmax:]
            lon_e=longitude[0:ind_xmin]
            longitude=np.concatenate((lon_o,lon_e))
            longitude=np.where(longitude<0,longitude+360,longitude)
            if lonref<0 :
                lonref=lonref+360
            for xll in range(len(lon_list)) :
                if (lon_list[xll]<0) :
                    lon_list[xll]=lon_list[xll]+360
        else :
            longitude=longitude[ind_xmin:ind_xmax]
        # Get variable
        unit_plot=[]
        lgname_plot=[]
        # if variable == 'salinity' :
        #   unit_tmp=nc_file.variables[variable].units_long
        # else :   
        unit_tmp=nc_file.variables[variable].unit_long
        lgname_plot.append(nc_file.variables[variable].long_name)
        if flag_sect==1 :
            var_o=nc_file.variables[variable][:,:,ind_ymin:ind_ymax,ind_xmax:]
            var_e=nc_file.variables[variable][:,:,ind_ymin:ind_ymax,0:ind_xmin]
            var_tmp=np.ma.concatenate((var_o,var_e),axis=3)
        else :
            var_tmp=nc_file.variables[variable][:,:,ind_ymin:ind_ymax,ind_xmin:ind_xmax]
        if unit_tmp=="Kelvin" :
            #print "Kelvin"
            unit_plot.append(r"${^\circ}$C")
            plotvar=var_tmp-273.15
        else :
            plotvar=var_tmp
            unit_plot.append(unit_tmp)
        toc = time.time()
        print '| %6d sec for extraction        |' %(toc-tic)
        return lgname_plot,unit_plot,longitude,latitude,profondeur,\
		 time_counter,plotvar,nsect,latref,lonref,lon_list,lat_list
