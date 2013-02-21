#!/usr/bin/env python

import sys
import os
import re
import math
from pyraf import iraf 
import ccxymatch_ref
import numpy as np

def daomatch(image, outprefix, wcscatalog, noiselevel=50, datamin=300,
        threshold=25, datamax=90000, fwhm=4, roundlo=-0.5, roundhi=0.5,
        sharplo=0.2, sharphi=0.5, interactive=True, lngunits='hours',
        latunits='degrees', update=False, **kwargs):
    # these unfortunately bring up menus...
    # iraf.noao.digiphot.apphot.findpars(threshold=10,)
    # iraf.noao.digiphot.apphot.datapars(scale=1, fwhmpsf=2.5, sigma=50,
    #         datamin=300, datamax=30000)
    iraf.noao.digiphot.apphot.datapars.fwhmpsf=fwhm
    iraf.noao.digiphot.apphot.datapars.sigma=noiselevel
    iraf.noao.digiphot.apphot.datapars.datamin=datamin
    iraf.noao.digiphot.apphot.datapars.datamax=datamax
    iraf.noao.digiphot.apphot.findpars.threshold = threshold
    iraf.noao.digiphot.apphot.findpars.roundlo = roundlo
    iraf.noao.digiphot.apphot.findpars.roundhi = roundhi
    iraf.noao.digiphot.apphot.findpars.sharphi = sharphi
    iraf.noao.digiphot.apphot.findpars.sharplo = sharplo
    iraf.noao.digiphot.apphot.daofind(image, output=outprefix+".coo",
            starmap=outprefix+".star", skymap=outprefix+".sky",
            verify=False, update=False, verbose=True, interactive=False)
    ccxymatch_ref.ccxymatch_ref(image, outprefix+".coo", wcscatalog,
            prefix=outprefix+"_", **kwargs)

    pixcoords = np.loadtxt(outprefix+".coo",usecols=[0,1])
    with open(outprefix+"_pix.reg",'w') as f:
        print >>f,"image"
        for x,y in pixcoords:
            print >>f,"point(%f,%f) # point=cross color=cyan" % (x,y)

    iraf.images.imcoords.ccmap(outprefix+"_match.txt", database=outprefix+"_match.db",
            images=image, results=outprefix+"_ccmap.db", xcolumn=3, ycolumn=4,
            lngcolumn=1, latcolumn=2, update=update, interactive=interactive,
            lngrefunits=lngunits, latrefunits=latunits)

    pixcoords_match = np.loadtxt(outprefix+"_match.txt",usecols=[2,3])
    with open(outprefix+"_matchpix.reg",'w') as f:
        print >>f,"image"
        for x,y in pixcoords_match:
            print >>f,"point(%f,%f) # point=x color=red" % (x,y)

