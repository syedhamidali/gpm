
"""

Einlesen und darstellen von GPM und Radolan Dateien

Radolanpfad:

"""


import h5py
import numpy as np
import matplotlib.pyplot as plt
import wradlib
import glob
import wradlib as wrl
from osgeo import osr



ipoli = [wradlib.ipol.Idw, wradlib.ipol.Linear, wradlib.ipol.Nearest, wradlib.ipol.OrdinaryKriging]
TH_ka, TH_ku = 0.2, 0.5

#DAS BESP'20141007023500'

# Zeitstempel nach YYYYMMDDhhmmss

#ZP = '20160805055000'; gpm_time = '2016-08-05 T: 054700 UTC'
#ZP = '20160607155500'; gpm_time = '2016-06-07 T: 155500 UTC'
#ZP = '20160405174500'; gpm_time = '2016-04-05 T: 174500 UTC'
ZP = '20141007023500'; gpm_time = '2014-10-07, 02:36 UTC'
#ZP = '20170113001000'; gpm_time = '2017-01-13, 00:12 UTC'

#'20160904134500'#'20161001060000'#'20161024232500'
# #'20140609132500'#'20160917102000'#'20160917102000'#'20160805054500'
# #'20161024232500'#'20150427223500' #'20141007023500'#
year, m, d, ht, mt, st = ZP[0:4], ZP[4:6], ZP[6:8], ZP[8:10], ZP[10:12], ZP[12:14]
ye = ZP[2:4]

## Read RADOLAN GK Koordinaten
## ----------------------------

pfad = ('/automount/radar/dwd/rx/'+str(year)+'/'+str(year)+'-'+str(m)+
        '/'+str(year)+'-'+str(m)+'-'+str(d)+'/raa01-rx_10000-'+str(ye)+
        str(m)+str(d)+str(ht)+str(mt)+'-dwd---bin.gz')

pfad_radolan = pfad[:-3]

####### pfad

rw_filename = wradlib.util.get_wradlib_data_file(pfad_radolan)
rwdata, rwattrs = wradlib.io.read_RADOLAN_composite(rw_filename)

rwdata = np.ma.masked_equal(rwdata, -9999) / 2 - 32.5

radolan_grid_xy = wradlib.georef.get_radolan_grid(900,900)
x = radolan_grid_xy[:,:,0]
y = radolan_grid_xy[:,:,1]
#Z = wradlib.trafo.idecibel(rwdata)
#rwdata = wradlib.zr.z2r(Z, a=200., b=1.6)




## Read GPM
## ------------
pfad2 = ('/home/velibor/shkgpm/data/'+str(year)+str(m)+str(d)+'/dpr/*.HDF5')
pfad_gprof = glob.glob(pfad2)
print pfad_gprof
pfad_gprof_g = pfad_gprof[0]


gpmdprs = h5py.File(pfad_gprof_g, 'r')
print gpmdprs
gprof_lat=np.array(gpmdprs['NS']['Latitude'])			#(7934, 24)
gprof_lon=np.array(gpmdprs['NS']['Longitude'])

#(7934, 24)
#gprof_pp=np.array(gpmdprs['NS']['SLV']['precipRateNearSurface'])

#gprof_pp=np.array(gpmdprs['NS']['SLV']['precipRate'])
#gprof_pp=np.array(gpmdprs['NS']['DSD']['phase'],dtype=float)
#print type(gprof_pp[1,2,0])
#gprof_pp = np.float(gprof_pp)
#gprof_pp= gprof_pp[:,:,:,0]
#gprof_pp=np.array(gpmdprs['NS']['DSD']['phase'])
##############################################Bei Regen
RR, ZZ = 'precipRate', 'zFactorCorrected' #precipRateNearSurface
gprof_pp=np.array(gpmdprs['NS']['SLV']['precipRateNearSurface'])

print gprof_pp.shape

gprof_pp[gprof_pp==-9999.9]= np.NaN


parameter3 = gpmdprs['NS']['DSD']['binNode']
Node = np.array(parameter3, dtype=float)
Node[Node<-1]= np.nan



##############################Bei Phase
#parameter2 = gpmdprs['NS']['cloudLiqWaterCont']
#parameter2 = gpmdprs['NS']['cloudIceWaterCont']

#parameter2 = gpmdprs['NS']['precipTotPSDparamHigh']
#parameter2 = gpmdprs['NS']['precipTotWaterCont']
#parameter2 = gpmdprs['NS']['correctedReflectFactor']
para_name = 'zFactorCorrected'#'precipRate'
parameter2 = gpmdprs['NS']['SLV'][para_name]

dpr = np.array(parameter2, dtype=float)
dpr[dpr<-9998]=np.nan
#dpr[dpr<100]=dpr[dpr<100]-100
#dpr[dpr>=200]=dpr[dpr>=200]-200
#dpr[dpr==125]=0
#dpr[dpr==175]=0
#dpr[dpr==100]=0
#dpr[dpr==150]=0

print 'CloudIcemaxmin:', np.nanmin(dpr), np.nanmax(dpr)

######################################## Bei Dropsize
#parameter2 = gpmdprs['NS']['SLV']['paramDSD']
#dpr = np.array(parameter2, dtype=float)
#dpr = dpr[:,:,:,1]
#dpr[dpr<-9998]=np.nan


#gpm_time = '2016-08-05 T: 054600 UTC'
#gpm_time = '2016-10-24 T: 232200 UTC'
#gpm_time = '2015-04-27 T: 223800 UTC'
#gpm_time = '2016-09-17 T: 101900 UTC'
#gpm_time = '2016-09-04 T: 134600 UTC'
############################################################### read Boxpol RHI
from mpl_toolkits.axisartist.grid_finder import FixedLocator, DictFormatter
# reading in GAMIC hdf5 file
filename = wrl.util.get_wradlib_data_file('/automount/radar-archiv/scans/2014'
                                          '/2014-10/2014-10-07/n_rhi_lacros'
                                          '/2014-10-07--02:37:44,00.mvol')
data, metadata = wrl.io.read_GAMIC_hdf5(filename)
data = data['SCAN0']['ZH']['data']
r = metadata['SCAN0']['r']
th = metadata['SCAN0']['el']
mask_ind = np.where(data <= np.nanmin(data))
data[mask_ind] = np.nan
ma = np.ma.array(data, mask=np.isnan(data))

############################################################Parameter bestimmen
ip = 0
PV_vmin = [0.1,-15]
PV_vmax = [10,40]
PV_name = ['Rainrate (mm/h)','Z (dBZ)']


# Swath ueber Deutschland
from pcc import cut_the_swath
blon, blat, gprof_pp_b = cut_the_swath(gprof_lon,gprof_lat,gprof_pp)
ablon, ablat, dpr3 = cut_the_swath(gprof_lon,gprof_lat,dpr)

nblon, nblat, node = cut_the_swath(gprof_lon,gprof_lat, Node)
node = node[:,:,1:4:2]

dpr4 = np.copy(dpr3)


print('Shape: ', dpr3.shape)
#dpr3 = gprof_pp_b
#gprof_pp_b = gprof_pp_b[:,:,80]

#gprof_pp_b[gprof_pp_b==-9999.9]=np.nan

print 'gprof min max:' + str(np.nanmin(gprof_pp_b)), str(np.nanmax(gprof_pp_b)), gprof_pp_b.shape
## GPM lon/lat in GK

proj_stereo = wrl.georef.create_osr("dwd-radolan")
proj_wgs = osr.SpatialReference()
proj_wgs.ImportFromEPSG(4326)

gpm_x, gpm_y = wradlib.georef.reproject(blon, blat, projection_target=proj_stereo , projection_source=proj_wgs)
grid_xy = np.vstack((gpm_x.ravel(), gpm_y.ravel())).transpose()



## Landgrenzenfunktion
## -------------------
from pcc import boxpol_pos
bonn_pos = boxpol_pos()
bx, by = bonn_pos['gkx_ppi'], bonn_pos['gky_ppi']
boxlat, boxlon = bonn_pos['lat_ppi'], bonn_pos['lon_ppi']

from pcc import plot_borders, plot_ocean

dataset1, inLayer1 = wradlib.io.open_shape('/automount/db01/python/data/ADM/germany/vg250_0101.gk3.shape.ebenen/vg250_ebenen/vg250_l.shp')

import matplotlib.cm as cm
my_cmap = cm.get_cmap('jet',40)
my_cmap.set_under('lightgrey')
my_cmap.set_over('darkred')


##################################################################INTERLOLATION
gk3 = wradlib.georef.epsg_to_osr(31467)

grid_gpm_xy = np.vstack((gpm_x.ravel(), gpm_y.ravel())).transpose() # GPM Grid erschaffen

xy = np.vstack((x.ravel(), y.ravel())).transpose()

mask = ~np.isnan(rwdata)

result = wrl.ipol.interpolate(xy, grid_gpm_xy, rwdata[mask].reshape(900*900,1), wrl.ipol.Idw, nnearest=4)  #Idw

result = np.ma.masked_invalid(result)

rrr = result.reshape(gpm_x.shape)



Z = wradlib.trafo.idecibel(rwdata)
rwdata = wradlib.zr.z2r(Z, a=200., b=1.6)


Zr = wradlib.trafo.idecibel(rrr)
rrr = wradlib.zr.z2r(Zr, a=200., b=1.6)
#rrr[rrr<=TH_ka]=np.NaN
#rrr[rrr==-9999.0]=np.nan



from pcc import plot_radar

from pcc import get_miub_cmap
my_cmap2 = get_miub_cmap()

######################################################################### PLOT
###########################################################################----
m = 176#176
mm = 0.125#0.125
h = np.arange(m,0,-1)*mm # Bei 88 500m und bei 176 ist es 250m


cut = 22 #22 bei bon201410 NS
node[:,cut]
nn = (m -node[:,cut]) * mm


fig = plt.figure(figsize=(12,12))

fft = 15.0
#figtextpositionen
xl = 0.06
xr = 0.56
yo = 0.965
yu = 0.47
#plt.ylim(0,100)
#'''

#####____________________AX1____________________#####
ax2 = fig.add_subplot(222, aspect='auto')
pm2 = plt.pcolormesh(gpm_x, gpm_y,np.ma.masked_invalid(gprof_pp_b),
                     cmap=my_cmap,
                     vmin=PV_vmin[ip],
                     vmax=PV_vmax[ip],
                     zorder=2)

plt.plot(gpm_x[:,cut],gpm_y[:,cut], color='red',lw=1)
cb = plt.colorbar(shrink=0.8,extend='max')
cb.set_label(PV_name[ip],fontsize=fft)
cb.ax.tick_params(labelsize=fft)
#plt.xlabel("x [km] ",fontsize=0)
#plt.ylabel("y [km]  ",fontsize=0)
plt.figtext(xr,yo,'b) GPM DPR: '+ gpm_time ,fontsize=fft)
plot_borders(ax2)
plot_radar(boxlon, boxlat, ax2, reproject=True)
plt.grid(color='r')
plt.tight_layout()
plt.xlim(-420,390)
plt.ylim(-4700, -3700)
#plt.xticks(fontsize=0)
#plt.yticks(fontsize=0)
plt.tick_params(
    axis='both',
    which='both',
    bottom='off',
    top='off',
    labelbottom='off',
    right='off',
    left='off',
    labelleft='off')


#### ____________________AX3____________________ #####
ax3 = fig.add_subplot(221, aspect='auto')
pm3 = plt.pcolormesh(gpm_x, gpm_y,rrr,
                     cmap=my_cmap,
                     vmin=0.1,
                     vmax=10,
                     zorder=2)

cb = plt.colorbar(pm3, shrink=0.8,extend='max')
cb.set_label("Rainrate (mm/h)",fontsize=fft)
cb.ax.tick_params(labelsize=fft)
#plt.xlabel("x [km] ",fontsize=ff)
#plt.ylabel("y [km]  ",fontsize=ff)
plt.figtext(xl,yo,'a) RADOLAN: '+'20' + str(pfad_radolan[-20:-18])+'-'+str(pfad_radolan[-18:-16])+'-'+str(pfad_radolan[-16:-14])+
       ', '+str(pfad_radolan[-14:-12])+':'+str(pfad_radolan[-12:-10]) + ' UTC',fontsize=fft) #RW Product Polar Stereo
plot_borders(ax3)
plot_radar(boxlon, boxlat, ax3, reproject=True)

plt.xlim(-420,390)
plt.ylim(-4700, -3700)
plt.grid(color='r')
plt.tight_layout()
#plt.xticks(fontsize=fft)
#plt.yticks(fontsize=0)
plt.tick_params(
    axis='both',
    which='both',
    bottom='off',
    top='off',
    labelbottom='off',
    right='off',
    left='off',
    labelleft='off')



##### ____________________AX3____________________ ####

ax4 = fig.add_subplot(224, aspect='auto')
#level1 = np.arange(np.nanmin(dpr4[:,cut,:]),np.nanmax(dpr4[:,cut,:]),0.1)

#level1 = np.arange(np.round(np.nanmin(dpr4[:,cut,:]),0),np.round(np.nanmax(dpr4[:,cut,:]),0),1)
level1 = np.arange(np.round(np.nanmin(ma),0),np.round(np.nanmax(ma),0),1)


print '-----------------'
print 'Boxpol:  ',np.round(np.nanmin(ma),0), np.round(np.nanmax(ma))
print 'DPR:  ',np.nanmin(dpr4[:,cut,:]),np.nanmax(dpr4[:,cut,:])
print '-----------------'



ax5 = plt.contourf(gpm_x[:,cut],h,dpr4[:,cut,:].transpose(),
             #vmin=0.101,
             #vmax=10,
             cmap=my_cmap2,
             levels=level1,
             extend='both')#max
plt.plot(gpm_x[:,cut], nn, '-k')

cb = plt.colorbar(shrink=0.8)#,ticks=t_level)
cb.set_label('Z (dBZ)',fontsize=fft)
cb.ax.tick_params(labelsize=fft)
#plt.gca().invert_xaxis()

plt.xlabel("x (km) ",fontsize=fft)
plt.ylabel("z (km)  ",fontsize=fft)
plt.xticks(fontsize=fft)
plt.yticks(fontsize=fft)
plt.figtext(xr,yu,'d) GPM DPR : \n'+ gpm_time,fontsize=fft)
#plt.xlim(-420,390)
plt.ylim(0,7)
#plt.xlim(-300,-80)
plt.xlim(bx-50,bx)
plt.xticks(ax4.get_xticks().tolist(),['60','50','40','30','20','10','0'])
print ax4.get_xticks().tolist()

plt.grid(True)

#ax4a = ax4.get_xticks().tolist()


##### ____________________AX4____________________ ####
import pcc as pcc
cgax, caax, paax, pm, xxx, yyy = pcc.pcc_plot_cg_rhi(ma, r=r, th=th, rf=1e3, cmap=my_cmap2, subplot=223,autoext=True)
cgax.set_ylim(0,7)
cbar = plt.gcf().colorbar(pm,shrink=0.8,extend='both')#, pad=0.05)
plt.gca().invert_xaxis()
cbar.set_label('Z (dBZ)',fontsize=fft)
caax.set_xlabel('x (km)',fontsize=fft)
caax.set_ylabel('z (km)',fontsize=fft)

cbar.ax.tick_params(labelsize=fft)

caax.tick_params(labelsize=fft)

plt.figtext(xl,yu,'c) BoXPol RHI \n 2014-10-07, 02:37 UTC',fontsize=fft)


gh = cgax.get_grid_helper()
locs = [0.]
gh.grid_finder.grid_locator1 = FixedLocator(locs)
gh.grid_finder.tick_formatter1 = DictFormatter(dict([(i, r"${0:.0f}^\circ$".format(i)) for i in locs]))
plt.yticks(fontsize=fft)
plt.xticks(fontsize=fft)

plt.tight_layout()
plt.show()


'''
grid_gpm_xy2 = np.vstack((gpm_x[:,cut].ravel(), gpm_y.ravel())).transpose() # GPM Grid erschaffen

xxxyyy = np.vstack((xxx[0:-1,0:-1].ravel(), yyy[0:-1,0:-1].ravel())).transpose()

mask1 = ~np.isnan(ma)

result2 = wrl.ipol.interpolate(xxxyyy, grid_gpm_xy2, ma[mask1].reshape(ma.shape[0]*ma.shape[1],1), wrl.ipol.Idw, nnearest=4)  #Idw

result2 = np.ma.masked_invalid(result2)

rrr2 = result2.reshape(gpm_x.shape)'''