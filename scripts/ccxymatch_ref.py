#!/usr/bin/env python

import sys
import os
import re
import math
from pyraf import iraf 

# Things that will be helpful:
# This task needs to overwrite some files:
# set clobber=yes
# You also want to see the full frame when you display things:
# set stdimage=imt2048

# fit the coordinats in file "file", with output text files prefixed with "prefix", e.g.:
# s69_1_ is the prefix for S20130131S0069.fits[1]
def ccxymatch_ref(reffile, pixcoordfile, wcscoordfile, prefix="fc_",
        ptolerance=20, tolerance=1, lngunits='hours', latunits='degrees',
        verbose=True, doccmap=False, update=False):

    iraf.images.imutil.imgets(reffile,'CRPIX1')
    xref = iraf.images.imutil.imgets.value
    iraf.images.imutil.imgets(reffile,'CRPIX2')
    yref = iraf.images.imutil.imgets.value
    iraf.images.imutil.imgets(reffile,'CRVAL1')
    if (lngunits=="hours"):
        lngref = float(iraf.images.imutil.imgets.value) / 15.
    else:
        lngref = float(iraf.images.imutil.imgets.value)
    iraf.images.imutil.imgets(reffile,'CRVAL2')
    latref = iraf.images.imutil.imgets.value

    iraf.images.imutil.imgets(reffile,'CD2_1')
    cd21 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(reffile,'CD1_2')
    cd12 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(reffile,'CD1_1')
    cd11 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(reffile,'CD2_2')
    cd22 = float(iraf.images.imutil.imgets.value) * 3600

    xmag = (cd11**2+cd12**2)**0.5
    ymag = (cd22**2+cd21**2)**0.5
    xrot = math.atan2(cd12,cd11) *180/math.pi
    yrot = math.atan2(-cd21,cd22) *180/math.pi

    if verbose:
        print "CD: ",cd11,cd12,cd21,cd22
        print "File and header: %s %s %f %s %f %f %f %f" % (xref,yref,lngref,latref,xmag,ymag,xrot,yrot)

    iraf.images.imcoords.ccxymatch(pixcoordfile, wcscoordfile,
            prefix+"match.txt", tolerance=tolerance, ptolerance=ptolerance,
            xrotation=xrot, yrotation=yrot, xin=xref, yin=yref, xmag=xmag, ymag=ymag,
            lngref=lngref, latref=latref, matching='tolerance',
            lngunits=lngunits, latunits=latunits)
    
    if doccmap:
        iraf.images.imcoords.ccmap(prefix+"match.txt", database=prefix+"match.db",
                images=reffile, results=prefix+"ccmap.db", xcolumn=3, ycolumn=4,
                lngcolumn=1, latcolumn=2, update=update, interactive=doccmap,
                lngrefunits=lngunits, latrefunits=latunits)

curpath = os.path.dirname( os.path.abspath(__file__) )
parfile = iraf.osfn(curpath+"/ccxymatch_ref.par") 
t = iraf.IrafTaskFactory(taskname="ccxymatch_ref", value=parfile, 
            function=ccxymatch_ref) 
    
