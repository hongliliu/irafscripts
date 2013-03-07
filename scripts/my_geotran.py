#!/usr/bin/env python
from pyraf import iraf 
import numpy as np
import os
import pyfits

def my_geotran(input_file, output_file, extensions=[1,2,3,4],
        dbtemplate="pixpix%iboth.db", transforms="frame%i",
        blocksize=2048, bad_kws=["CCDSEC","DATASEC"]):
    """
    Stupid, simple version of gamosaic - but it works.
    """
    for ii in extensions:
        iraf.images.geotran(input_file+"[%i]" % ii,
                "%itmp_%s" % (ii,output_file),
                database=dbtemplate % ii,
               transforms=transforms % ii, boundary="constant",
               nxblock=blocksize, nyblock=blocksize, verbose=True,
               fluxconserve=False, constant=0)
        for kw in bad_kws:
            iraf.images.hedit("%itmp_%s" % (ii,output_file), kw, delete=True, verify=False)
    iraf.images.immatch.imcombine(
            ",".join(["%itmp_%s" % (ii,output_file) for ii in extensions]),
            output_file, combine="sum", offsets="none")

    print "Setting 0 to nan in output file"
    f = pyfits.open(output_file)
    f[0].data[f[0].data==0] = np.nan
    f.writeto(output_file,clobber=True)

    for ii in extensions:
        iraf.images.imutil.imdel(
                "%itmp_%s" % (ii,output_file),
                verify=False)


curpath = os.path.dirname( os.path.abspath(__file__) )
parfile = iraf.osfn(curpath+"/my_geotran.par") 
t = iraf.IrafTaskFactory(taskname="my_geotran", value=parfile, 
            function=my_geotran) 
    
