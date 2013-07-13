import numpy as np
import healpy as hp
import pandas as pd
from glob import glob

freq = 30
m=hp.read_map(glob("plancktest/*SkyMap_%03d_*nominal.fits" % freq)[0])
nside = hp.npix2nside(len(m))

width = 10
poles_margin = 0.1
halfwidth = width/2

for theta in range(halfwidth, 180, width):
    for phi in range(halfwidth, 360, width):

        filename = "plancktest/submaps/%03d_%03d_%03d" % (freq, theta, phi)
        print filename

        vertex_angles = np.radians(
                        [[theta-halfwidth, phi-halfwidth],
                         [theta+halfwidth, phi-halfwidth],
                         [theta+halfwidth, phi+halfwidth],
                         [theta-halfwidth, phi+halfwidth]])
        
        if theta - halfwidth == 0:
            vertex_angles[0,0] = np.radians(poles_margin)
            vertex_angles[3,0] = np.radians(poles_margin)

        if theta + halfwidth == 180:
            vertex_angles[1,0] = np.radians(180-poles_margin)
            vertex_angles[2,0] = np.radians(180-poles_margin)

        pix=hp.query_polygon(nside, hp.ang2vec(vertex_angles[:,0], vertex_angles[:,1]), np.radians(13))
        submap = np.zeros(len(pix), dtype=[("pix",np.int64), ("temp", np.float64)])
        submap["pix"] = pix
        submap["temp"] = m[pix]
        np.save(filename, submap)
