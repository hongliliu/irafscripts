#!/usr/bin/env python

import sys
import os
import re
import math
from pyraf import iraf 
import match_cats

# Things that will be helpful:
# This task needs to overwrite some files:
# set clobber=yes
# You also want to see the full frame when you display things:
# set stdimage=imt2048

# fit the coordinats in file "file", with output text files prefixed with "prefix", e.g.:
# s69_1_ is the prefix for S20130131S0069.fits[1]
def fit_coords(infile, prefix="fc_", catalog="muench.txt", ptolerance=20,
        tolerance=1, pixmapfile="", pixmapextension="2", interactive=True,
        update=False, lngunits='hours', latunits='degrees', 
        refra=None, refdec=None, verbose=True,):
    """ Note that order in fit_coords.par matters """

    if (pixmapfile == ""):
        pmf = infile
    else:
        pmf = pixmapfile

    if "[" in pmf and "]" in pmf:
        if pixmapextension != "":
            pmf = re.sub("\[[a-zA-Z0-9]*]","[%s]" % pixmapextension,pmf)
    else:
        pmf = "%s[%s]" % (pmf, pixmapextension)

    iraf.imcoords.wcsctran(catalog, prefix+"transformed.txt", infile, inwcs="world", outwcs="logical",
                      columns="1 2 3", units=lngunits)
    if (interactive):
        iraf.images.tv.display(infile, frame=1, zscale=False, ocolors='green', ztrans='log')
        iraf.images.tv.tvmark(frame=1, coords=prefix+"transformed.txt",
                mark="circle", radii=20, lengths=3, color=205, label=True,
                txsize=3)
        iraf.images.tv.imexam(infile, logfile=prefix+"imexam.log", frame=1,
                wcs="world", xformat="%h", yformat="%H", keeplog=True,
                 display="display(image='$1', frame='1', zscale=no,ocolors='green',ztrans='log')")

    iraf.images.imutil.imgets(infile,'CRPIX1')
    xref = iraf.images.imutil.imgets.value
    iraf.images.imutil.imgets(infile,'CRPIX2')
    yref = iraf.images.imutil.imgets.value
    iraf.images.imutil.imgets(infile,'CRVAL1')
    if (lngunits=="hours"):
        lngref = float(iraf.images.imutil.imgets.value) / 15.
    else:
        lngref = float(iraf.images.imutil.imgets.value)
    iraf.images.imutil.imgets(infile,'CRVAL2')
    latref = iraf.images.imutil.imgets.value

    iraf.images.imutil.imgets(infile,'CD2_1')
    cd21 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(infile,'CD1_2')
    cd12 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(infile,'CD1_1')
    cd11 = float(iraf.images.imutil.imgets.value) * 3600
    iraf.images.imutil.imgets(infile,'CD2_2')
    cd22 = float(iraf.images.imutil.imgets.value) * 3600

    xmag = (cd11**2+cd12**2)**0.5
    ymag = (cd22**2+cd21**2)**0.5
    xrot = math.atan2(cd12,cd11) *180/math.pi
    yrot = math.atan2(-cd21,cd22) *180/math.pi

    if verbose:
        print "CD: ",cd11,cd12,cd21,cd22
        print "File and header: %s %s %s %f %s %f %f %f %f" % (pmf,xref,yref,lngref,latref,xmag,ymag,xrot,yrot)
    
    inds1,inds2,dist = match_cats.match_cats(prefix+"imexam.log",
        prefix+"transformed.txt", tol=ptolerance, savetxt=prefix+"match.txt",
        extracolcat=catalog)
    iraf.images.imcoords.ccmap(prefix+"match.txt", database=prefix+"match.db", images=infile,
                               results=prefix+"ccmap.db", xcolumn=1,
                               ycolumn=2, lngcolumn=5, latcolumn=6,
                               update=update, interactive=interactive,
                               lngunits=lngunits, latunits=latunits,
                               lngrefunits=lngunits, latrefunits=latunits)

    if verbose:
        print "Aligning pixel coordinates to header of %s" % pmf

    if refra is not None and refdec is not None:
        iraf.stsdas.toolbox.imgtools.rd2xy(pmf,refra,refdec,hour=False) 
        x = iraf.stsdas.toolbox.imgtools.rd2xy.x
        y = iraf.stsdas.toolbox.imgtools.rd2xy.y
        iraf.images.imutil.hedit(pmf,fields="CRPIX1",value=x,verify=False)
        iraf.images.imutil.hedit(pmf,fields="CRPIX2",value=y,verify=False)
        iraf.images.imutil.hedit(pmf,fields="CRVAL1",value=refra,verify=False)
        iraf.images.imutil.hedit(pmf,fields="CRVAL2",value=refdec,verify=False)
        print "x,y %f,%f to ra,dec %f,%f" % (x,y,refra,refdec)

    iraf.images.imcoords.wcsctran(prefix+"ccmap.db",
            "tmp_"+prefix+"pixpixmap.txt", pmf, inwcs="world",
            outwcs="physical", columns="3 4 1 2 5 6 7 8", units="hours")
    ppf = open(prefix+"pixpixmap.txt",'w')
    for line in file("tmp_"+prefix+"pixpixmap.txt"):
        if line[0] != "#":
            data = line.strip().split()
            if len(data)>=4:
                data[0],data[1],data[2],data[3] = data[2],data[3],data[0],data[1]
                ppf.write(" ".join(["%13s" % d for d in data]))
                ppf.write("\n")
        else:
            ppf.write(line)
    ppf.close()
    os.remove("tmp_"+prefix+"pixpixmap.txt")

curpath = os.path.dirname( os.path.abspath(__file__) )
parfile = iraf.osfn(curpath+"/fit_coords.par") 
t = iraf.IrafTaskFactory(taskname="fit_coords", value=parfile, 
            function=fit_coords) 
    
