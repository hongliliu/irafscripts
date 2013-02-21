#!/usr/bin/env python

import sys
import os
import re
import math
from pyraf import iraf 
import ccxymatch_ref

def daomatch(image, outprefix, wcscatalog, noiselevel=50, datamin=300,
        threshold=10, datamax=30000, **kwargs):
    # these unfortunately bring up menus...
    # iraf.noao.digiphot.apphot.findpars(threshold=10,)
    # iraf.noao.digiphot.apphot.datapars(scale=1, fwhmpsf=2.5, sigma=50,
    #         datamin=300, datamax=30000)
    iraf.noao.digiphot.apphot.datapars.sigma=noiselevel
    iraf.noao.digiphot.apphot.datapars.datamin=datamin
    iraf.noao.digiphot.apphot.datapars.datamax=datamax
    iraf.noao.digiphot.apphot.findpars.threshold = threshold
    iraf.noao.digiphot.apphot.daofind(image, output=outprefix+".coo",
            starmap=outprefix+".star", skymap=outprefix+".sky",
            verify=False, update=False, verbose=True, interactive=False)
    ccxymatch_ref.ccxymatch_ref(image, outprefix+".coo", wcscatalog, **kwargs)
