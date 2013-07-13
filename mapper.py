#!/usr/bin/env python

import sys
import os
import pyfits
import numpy as np
import pandas as pd
import healpy as hp
import exceptions
from glob import glob

base_folder = "/oasis/scratch/zonca/temp_project/"

def load_catalog(key):
    filename = glob(base_folder + "plancktest/COM_PCCS_%03d*fits" % key)[0]
    return np.array(pyfits.open(filename)[1].data)

class Catalogs(object):
    """Lazy load of catalogs"""
    
    data = {}

    def __getitem__(self, key):
        try:
            return self.data[key]
        except:
            self.data[key] = load_catalog(key)
            return self.data[key]
        
catalogs = Catalogs()
width = 10
halfwidth = width/2
nside = 1024

# test
#line = 'plancktest/submaps/030_025_005'
# input comes from STDIN (standard input)
for line in sys.stdin:
# remove leading and trailing whitespace
    line = line.strip()

    freq, theta, phi = map(int, os.path.basename(line).split("_"))

    glat = 90 - theta
    glon = phi

# open input submap
    submap_array = np.load(line + ".npy")
    submap = pd.Series(submap_array["temp"], index=submap_array["pix"])

    sources_lon = catalogs[freq]["GLON"].searchsorted([glon-halfwidth, glon+halfwidth])
    sources = catalogs[freq][sources_lon[0]:sources_lon[1]]
    sources = sources[(sources["GLAT"] > glat - halfwidth) & (sources["GLAT"] < glat + halfwidth)]

    for source in sources:
        src_vec = hp.ang2vec(np.radians(90-source["GLAT"]), np.radians(source["GLON"]))
        pix = hp.query_disc(nside, src_vec, np.radians(10/60.))
        print '%s\t%.5e' % (source["NAME"] + "_10arcminmean", submap[pix].mean())
