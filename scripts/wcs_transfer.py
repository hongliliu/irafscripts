#!/usr/bin/env python
"""
Transfer the WCS from one header to another
"""

import os
from pyraf import iraf 

WCS_keywords = ['CD1_1', 'CD1_2', 'CD2_1', 'CD2_2', 'CRPIX1', 'CRPIX2',
    'CRVAL1', 'CRVAL2', 'CDELT1', 'CDELT2', 'CUNIT1', 'CUNIT2', 'CTYPE1', 'CTYPE2']

def wcs_transfer(file1,file2,extensions="1,2,3,4"):

    if type(extensions) is str:
        extensions = [int(x) for x in extensions.split(',')]

    template = "%s[%i]" 

    for ext in extensions:
        for kw in WCS_keywords:
            iraf.images.imutil.imgets(template % (file1,ext),kw)
            var = iraf.images.imutil.imgets.value
            if var != '0':
                iraf.hedit(template % (file2,ext), fields=kw, value=var,
                        add=True, verify=False, update=True, show=True)

curpath = os.path.dirname( os.path.abspath(__file__) )
parfile = iraf.osfn(curpath+"/wcs_transfer.par") 
t = iraf.IrafTaskFactory(taskname="wcs_transfer", value=parfile, 
            function=wcs_transfer) 
    
