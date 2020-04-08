#lightcurves_sh rewritten to use starry instead of SPIDERMAN
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import pickle
import starry
if starry.__version__ >= '1.0':
    starry.config.lazy = False
    starry.config.quiet = True
from pca_eig import princomp
import pdb

# def minmax(x):
#      return np.amin(x),np.amax(x),np.nanmin(x),np.nanmax(x)


def make_lc(star,planet,time):
	if starry.__version__ >='1.0':
		system = starry.System(star, planet)
		flux_star, lightcurve = system.flux(time, total=False)
	else:
		# Create starry system with star and planet
		system = starry.kepler.System(star, planet)
		system.compute(time)
		lightcurve = system.lightcurve / system.lightcurve[0]
	return lightcurve

def sh_lcs(t0=0,per=2.21857567,inc=85.71,ecc=0.0,w=90,rp=0.155313,a=8.863,ntimes=500,degree=3):
	# initialize star and planet parameters
	if starry.__version__ >= '1.0':
		star = starry.Primary(starry.Map(ydeg=0,udeg=0,amp=1.0), m=1.0, r=1.0, prot=1.0)

		planet = starry.kepler.Secondary(
		    starry.Map(ydeg=int(degree-1), amp=1.),  # surface map, amp is luminosity relative to star (normalization is Y00)
			#m=0.0009543,  # mass in solar masses
			r=rp,  # radius in solar radii
			porb=per,  # orbital period in days
			prot=per,  # rotation period in days
			inc=inc,   # inclination of orbit in degrees
			a=a,	#a/rstar
			ecc=ecc,  # eccentricity
			w=w,  # longitude of pericenter in degrees
			t0=t0,  # time of transit in days
		)
	else:
		## Star
		star = starry.kepler.Primary()#nwav=Nlamlo)
		# Create starry planet
		planet = starry.kepler.Secondary(lmax=int(degree-1))#,nwav=Nlamlo)
		
		# HD189 parameters
		planet.r = rp
		L = 0.00344
		planet.L = L #* np.ones(Nlamlo)
		planet.inc = inc
		planet.a = a
		planet.prot = per
		planet.porb = per
		planet.tref = 0.0#-per/2.0
		planet.ecc = ecc
		planet.w = w

	# arrays of time and fluxes for secondary eclipse curves:
	if np.size(ntimes) == 1:
		time = t0+np.linspace(0,per,ntimes)
	else:
		time = ntimes
		ntimes = time.size

	# calculate set of spherical harmonic curves, up to lmax=3 (excluding Y00)
	# include positive and negative versions of each component
	# 16 coefficients (incl. Y00); 30 SH curves

	numcurves=int(2*((degree)**2.-1)+1)
	SHcurves = np.zeros((numcurves,ntimes))
	#pdb.set_trace()
	shi=0
	#planet.map[0,0]=1.0
	
	SHcurves[shi,:] = make_lc(star,planet,time)
	
	shi+=1
	#planet.map[0,0]=0.0
	for l in range(1,degree):
		for m in range(-1*l,l+1):
	        #print(shi,l,m)
	                
	        # calculate negative version of SH component:
			if starry.__version__ >= '1.0':
				planet.map[l,m]=-1.0
			else:
				planet[l,m]=-1000.0
			
			SHcurves[shi,:] = make_lc(star,planet,time)
			
			#flux_star, temp = system.flux(time, total=False)
			#SHcurves[shi,:] = temp-SHcurves[0,:] #subtract off the zeroth degree thing
			shi+=1

	        # calculate positive version of SH component:
			if starry.__version__ >= '1.0':
				planet.map[l,m]=1.0
			else:
				planet[l,m] = 1000.0
			
			SHcurves[shi,:] = make_lc(star,planet,time)
			#flux_star, temp = system.flux(time, total=False)
			#SHcurves[shi,:] = temp-SHcurves[0,:] #subtract off the zeroth degree thing
			shi+=1

	        # reset coefficient to zero
			if starry.__version__ >= '1.0':
				planet.map[l,m]=0
			else:
				planet.reset()
			
			
	#pdb.set_trace()
	return SHcurves,time



