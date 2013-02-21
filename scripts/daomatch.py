#!/usr/bin/env python

import sys
import os
import re
import math
from pyraf import iraf 

def daomatch(image,outprefix):
    iraf.noao.digiphot.apphot.datapars(scale=1,fwhmpsf=2.5,sigma=50,datamin=300,datamax=30000)
    iraf.noao.digiphot.apphot.daofind(image, output=outprefix+".coo",
            starmap=outprefix+".star", skymap=outprefix+".sky")
