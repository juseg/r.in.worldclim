#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MODULE:     r.in.worldclim.tiles

AUTHOR(S):  Paulo van Breugel <pvb@ecodiv.earth>

PURPOSE:    Find worldclim tiles that cover the region of interest

COPYRIGHT: (C) 1997-2017 by the GRASS Development Team

            This program is free software under the GNU General Public
            License (>=v3). Read the file COPYING that comes with GRASS
            for details.
"""

#%Module
#% description: Find wordclim tiles that cover region of interest
#% keywords: raster import worldclim tiles
#%end

#%option G_OPT_M_REGION
#% key: region
#% description: Region for which to find tiles
#% required: no
#% guisection: ROI
#%end

#%option G_OPT_V_INPUT
#% key: vector
#% description: Vector to determine region for which to find tiles
#% required: no
#% guisection: ROI
#%end

#%option G_OPT_R_INPUT
#% key: raster
#% description: Raster determining the region for which to find tiles
#% required: no
#% guisection: ROI
#%end

#%option
#% key: variables
#% type: string
#% description: Variable(s) to import
#% options: tmin,tmax,tmean,prec,bio,alt
#% required: no
#% multiple: yes
#% guisection: Download
#%end

#%option G_OPT_M_DIR
#% key: dir
#% description: Directory for saving the zip files (default: current directory)
#% required: no
#% guisection: Download
#%end

#%flag
#%  key: g
#%  description: Print region info in shell script style
#% guisection: Print
#%end

#%rules
#% required: vector, raster, region
#%end

import os
import sys
import grass.script as grass
import math


def download_files(variables, tiles, path):
    """Download files. The download routine is from
    http://stackoverflow.com/questions/22676/
    how-do-i-download-a-file-over-http-using-python"""

    import urllib2
    bs = "http://biogeo.ucdavis.edu/data/climate/worldclim/1_4/tiles/cur/"
    murl = ["{}{}_{}.zip"
            .format(bs, x, y) for x in variables for y in tiles]
    for url in murl:
        file_name = url.split('/')[-1]
        file_path = "{}{}".format(path, file_name)
        if not os.path.isfile(file_path):
            grass.info("\n")
            u = urllib2.urlopen(url)
            f = open(file_path, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            grass.info("Downloading: {} ({:4.1f} Mb)"
                       .format(file_name, file_size/1000000.))
            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = (r"Downloaded: {:3.2f}%"
                          .format(file_size_dl * 100. / file_size))
                status = status + chr(8)*(len(status)+1)
                print status,

            f.close()


# Main function
def main(options, flags):
    """Determine which tiles the user needs to download to cover the region
    of interest as determined by region, vector layer and/or raster layer"""

    variables = options['variables'].split(',')
    region = options['region']
    vector = options['vector']
    raster = options['raster']
    path = options['dir']
    if path:
        path = r"{}/".format(path)
    flag_g = flags['g']

    n, s, w, e = ([] for i in range(4))

    if region:
        reg = grass.parse_command("r.info", flags="g", map=region)
        n.append(float(reg['north']))
        s.append(float(reg['south']))
        w.append(float(reg['west']))
        e.append(float(reg['east']))

    if vector:
        vec = grass.parse_command("v.info", flags="g", map=vector)
        n.append(float(vec['north']))
        s.append(float(vec['south']))
        w.append(float(vec['west']))
        e.append(float(vec['east']))

    if raster:
        ras = grass.parse_command("r.info", flags="g", map=raster)
        n.append(float(ras['north']))
        s.append(float(ras['south']))
        w.append(float(ras['west']))
        e.append(float(ras['east']))

    nbound = max(n)
    sbound = min(s)
    wbound = min(w)
    ebound = max(e)

    ru = int(3 - math.ceil(nbound / 30))
    rd = int(2 - math.floor(sbound / 30))
    cl = int(math.floor(wbound / 30) + 6)
    cr = int(math.ceil(ebound / 30 + 5))
    rows = [ru] if ru == rd else range(ru, rd + 1)
    cols = [cl] if cr == cl else range(cl, cr + 1)
    tiles = [str(x)+str(y) for x in rows for y in cols]

    if len(tiles) > 1:
        M = ', '.join(tiles[:-1]) + ' & ' + tiles[-1]
    elif len(tiles) == 1:
        M = tiles[0]

    if not options['variables']:
        if flag_g:
            print(','.join(tiles))
        else:
            grass.info("To cover your region or interest\n "
                       "download the tiles {}".format(M))
    else:
        download_files(variables, tiles, path)


if __name__ == "__main__":
    sys.exit(main(*grass.parser()))
