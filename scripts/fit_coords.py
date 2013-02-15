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
def fit_coords(file, prefix="fc_", catalog="muench.txt", ptolerance=20,
        tolerance=1, pixmapfile="", pixmapextension="1", interactive=True,
        update=False, lngunits='hours', latunits='degrees', verbose=True):

    if (pixmapfile == ""):
        pmf = file
    else:
        pmf = pixmapfile

    if "[" in pmf and "]" in pmf:
        if pixmapextension != "":
            pmf = re.sub("\[[a-zA-Z0-9]*]","[%s]" % pixmapextension,pmf)
    else:
        pmf = "%s[%s]" % (pmf, pixmapextension)

    iraf.imcoords.wcsctran(catalog, prefix+"transformed.txt", file, inwcs="world", outwcs="logical",
                      columns="1 2 3", units=lngunits)
    if (interactive):
        iraf.images.tv.display(file, frame=1, zscale=False, ocolors='green', ztrans='log')
        iraf.images.tv.tvmark(frame=1, coords=prefix+"transformed.txt",
                mark="circle", radii=20, lengths=3, color=205, label=True,
                txsize=3)
        iraf.images.tv.imexam(file, logfile=prefix+"imexam.log", frame=1,
                wcs="world", xformat="%h", yformat="%H", keeplog=True,
                 display="display(image='$1', frame='1', zscale=no,ocolors='green',ztrans='log')")

    iraf.images.imutil.imgets(file,'CRPIX1')
    xref = iraf.images.imutil.imgets.value
    iraf.images.imutil.imgets(file,'CRPIX2')
    yref = iraf.images.imutil.imgets.value
    iraf.images.imutil.imgets(file,'CRVAL1')
    if (lngunits=="hours"):
        lngref = float(iraf.images.imutil.imgets.value) / 15.
    else:
        lngref = float(iraf.images.imutil.imgets.value)
    iraf.images.imutil.imgets(file,'CRVAL2')
    latref = iraf.images.imutil.imgets.value

    iraf.images.imutil.imgets(file,'CD2_1')
    cd21 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(file,'CD1_2')
    cd12 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(file,'CD1_1')
    cd11 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(file,'CD2_2')
    cd22 = float(iraf.images.imutil.imgets.value) * 3600

    xmag = (cd11**2+cd12**2)**0.5
    ymag = (cd22**2+cd21**2)**0.5
    xrot = math.atan(cd12/cd11) *180/math.pi
    yrot = math.atan(cd21/cd22) *180/math.pi

    if verbose:
        print "File and header: %s %s %s %f %s %f %f" % (pmf,xref,yref,lngref,latref,xmag,ymag)

    iraf.images.imcoords.ccxymatch(prefix+"imexam.log", catalog,
            prefix+"match.txt", tolerance=tolerance, ptolerance=ptolerance,
            xrotation=xrot, yrotation=yrot, xin=xref, yin=yref, xmag=xmag, ymag=ymag,
            lngref=lngref, latref=latref, matching='tolerance',
            lngunits=lngunits, latunits=latunits)
    iraf.images.imcoords.ccmap(prefix+"match.txt", database=prefix+"match.db", images=file,
                               results=prefix+"ccmap.db", xcolumn=3,
                               ycolumn=4, lngcolumn=1, latcolumn=2,
                               update=update, interactive=interactive,
                               lngrefunits=lngunits, latrefunits=latunits)

    if verbose:
        print "Aligning pixel coordinates to header of %s" % pmf

    iraf.images.imcoords.wcsctran(prefix+"ccmap.db",prefix+"pixpixmap.txt",pmf,inwcs="world",outwcs="physical",
            columns="3 4 1 2 5 6 7 8", units="hours")

curpath = os.path.dirname( os.path.abspath(__file__) )
parfile = iraf.osfn(curpath+"/fit_coords.par") 
t = iraf.IrafTaskFactory(taskname="fit_coords", value=parfile, 
            function=fit_coords) 
    
