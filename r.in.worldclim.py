#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MODULE:     r.in.worldclim

AUTHOR(S):  Julien Seguinot <seguinot@vaw.baug.ethz.ch> (original author)
            Paulo van Breugel <pvb@ecodiv.earth>

PURPOSE:    Import multiple WorldClim current [1] climate data.

COPYRIGHT:  (c) 2011-2016 Julien Seguinot

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

#%Module
#% description: Import multiple WorldClim current climate data.
#% keywords: raster import worldclim
#%end

#%option G_OPT_M_DIR
#% key: inputdir
#% description: Directory containing input files (default: current)
#% required: no
#% guisection: import
#%end

#%option
#% key: variables
#% type: string
#% description: Variable(s) to import
#% options: tmin,tmax,tmean,prec,bioclim,alt
#% required: yes
#% multiple: yes
#% guisection: import
#%end

#%option
#% key: tiles
#% type: string
#% description: 30 arc-minutes tiles(s) to import
#% required: no
#% multiple: yes
#% guisection: import
#%end

#%option
#% key: res
#% type: string
#% description: Global set resolution(s) to import
#% options: 30s,2.5m,5m,10m
#% required: no
#% multiple: yes
#% guisection: import
#%end

#%option
#% key: bioclim
#% type: integer
#% description: Bioclim variable(s) to import (default: all)
#% required: no
#% multiple: yes
#%end

#%option
#% key: months
#% type: integer
#% description: Month(s) for which to import climate data (default: all)
#% required: no
#% multiple: yes
#%end

#%option G_OPT_R_BASENAME_OUTPUT
#% key: prefix
#% type: string
#% description: Prefix for imported raster layers
#% required: no
#% answer: wc_
#% guisection: output
#%end

#%flag
#%  key: c
#%  description: Convert tmin, tmax, tmean to degree Celcius
#% guisection: output
#%end

#%flag
#%  key: k
#%  description: Convert tmin, tmax, tmean to Kelvin
#% guisection: output
#%end

#%flag
#%  key: y
#%  description: Convert precipitation to meter per year
#% guisection: output
#%end

#%flag
#%  key: f
#%  description: Convert to floating-point
#% guisection: output
#%end

#%flag
#%  key: p
#%  description: do not patch imported tiles
#% guisection: output
#%end

#%rules
#% required: res, tiles
#%end

#%rules
#% exclusive: res, tiles
#%end

#%rules
#% requires: -p,tiles
#%end

import os
import sys
from zipfile import ZipFile
import grass.script as grass
import uuid


# Import functions
def import_layer(variable, region, res=None, tile=None, layer=None):
    """Wrapper to the import_file() and convert_map() functions."""

    # get archive, file and output name
    outputmap = output_name(variable, res, tile, layer)
    filename = file_name(variable, layer=layer, res=res, tile=tile)
    archivename = archive_name(variable, layer=layer, res=res, tile=tile)

    # pass arguments to the import file function via naming funcions
    import_file(filename, archivename, outputmap, region)

    # call convert_map for unit and format conversion
    convert_map(outputmap, variable)

    # return name of output layer
    return(outputmap)


def import_file(filename, archive, output, region):
    """Extracts one binary file from its archive and import it."""

    # open the archive
    with ZipFile(archive, 'r') as a:

        # create temporary file and directory
        tempdir = grass.tempdir()
        tempfile = os.path.join(tempdir, filename)

        # try to inflate and import the layer

        if os.path.isfile(archive):
            try:
                grass.message("Inflating {} ...".format(filename))
                a.extract(filename, tempdir)
                grass.message("Importing {} as {} ..."
                              .format(filename, output))
                grass.run_command('r.in.bin',  flags='s', input=tempfile,
                                  output=output, bytes=2, anull=-9999,
                                  **region)

            # if file is not present in the archive
            except KeyError:
                grass.warning("Could not find {} in {}. Skipping"
                              .format(filename, archive))

            # make sure temporary files are cleaned
            finally:
                grass.try_remove(tempfile)
                grass.try_rmdir(tempdir)
        else:
            grass.warning("Could not find file {}. Skipping"
                          .format(archive))


def import_variables(variables, bioclim, months, res=None, tile=None):
    """Import requested variables for a given tile or resolution."""

    # compute region extents
    region = region_extents(res=res, tile=tile)

    # for each of the requested variables
    for variable in variables:

        # alt is a special case since there is only one layer
        if variable == 'alt':
            import_layer('alt', region, res=res, tile=tile)

        # bio is a bit of a special case too since there are 19 layers
        elif variable == 'bio':
            for layer in bioclim:
                import_layer(variable, region, layer=layer, res=res, tile=tile)

        # other variables have 12 layers
        else:
            for layer in months:
                import_layer(variable, region, layer=layer, res=res, tile=tile)


def convert_map(output, variable):
    """Convert imported raster map unit and format."""

    # prepare for unit conversion
    if flags['c'] and variable in ['tmin', 'tmax', 'tmean']:
        grass.message("Converting {} to degree Celcius...".format(output))
        a = 0.1
        b = 0
    elif flags['k'] and variable in ['tmin', 'tmax', 'tmean']:
        grass.message("Converting {} to Kelvin...".format(output))
        a = 0.1
        b = 273.15
    elif flags['y'] and variable == 'prec':
        grass.message("Converting {} to meter per year...".format(output))
        a = 0.012
        b = 0
    elif flags['f']:
        grass.message("Converting {} to floating-point...".format(output))
        a = 1
        b = 0
    else:
        a = None
        b = None

    # convert unit and format
    if a or b:
        grass.use_temp_region()
        grass.run_command('g.region', rast=output)
        grass.mapcalc('$output=float($output*$a+$b)', a=a, b=b, output=output,
                      overwrite=True)
        grass.del_temp_region()


# Input and output name and region conventions
def archive_name(variable, res=None, tile=None, layer=None):
    """Return the name of the corresponding zip archive."""

    # for global data (the bio 30s data is packed in two files)
    if res:
        if variable == 'bio' and res == '30s':
            if layer <= 9:
                archive = 'bio1-9_30s_bil.zip'
            if layer >= 10:
                archive = 'bio10-19_30s_bil.zip'
        else:
            archive = variable + '_' + res.replace('.', '-') + '_bil.zip'

    # for tiled data
    else:
        archive = variable + '_' + str(tile) + '.zip'

    # return full path
    return os.path.join(options['inputdir'], archive)


def file_name(variable, res=None, tile=None, layer=None):
    """Return the name of the corresponding binary file."""

    # convert layer to a string or empty string if None
    layerstr = (str(layer) if layer else '')

    # for global data (the 30s data has different naming)
    if res:
        if variable != 'alt' and res == '30s':
            return variable + '_' + layerstr + '.bil'
        else:
            return variable + layerstr + '.bil'

    # for tiled data
    else:
        return variable + layerstr + '_' + str(tile) + '.bil'


def output_name(variable, res=None, tile=None, layer=None):
    """Return an output name for the resulting raster map."""

    # convert layer to a string or empty string if None
    layerstr = "{:02d}".format(layer) if layer else ''

    # for global data layers
    if res:
        name = res + '_' + variable + layerstr

    # for tiled data
    else:
        name = 't' + str(tile) + '_' + variable + layerstr

    # return full name with prefix
    return options['prefix'] + name


def region_extents(res=None, tile=None):
    """Return region extents for a given resolution or tile."""

    # for global data
    if res:
        if res == '10m':
            rows = 900
            cols = 2160
        elif res == '5m':
            rows = 1800
            cols = 4320
        elif res == '2.5m':
            rows = 3600
            cols = 8640
        elif res == '30s':
            rows = 18000
            cols = 43200
        return {'north': 90, 'south': -60,
                'west': -180, 'east':  180,
                'rows': rows, 'cols': cols}

    # for tiled data
    elif tile:
        tilerow = int(tile[0])
        tilecol = int(tile[1:])
        return {'north': 30*(3-tilerow), 'south': 30*(2-tilerow),
                'west': 30*(tilecol-6), 'east': 30*(tilecol-5),
                'rows': 3600, 'cols': 3600}


def patch_tiles(mt, out, vari, bc=None, mnth=None):
    """Set region to tiles, and run r.patch"""

    bc = (str(bc) if bc else '')
    mnth = (str(mnth) if mnth else '')
    grass.message(_("Patching the tiles for {}{}{} to {}"
                    .format(vari, bc, mnth, out)))
    if len(mt) > 1:
        grass.use_temp_region()
        grass.run_command("g.region", raster=mt)
        grass.run_command("r.patch", input=mt, output=out)
        grass.run_command("g.remove", type="raster", name=mt, flags="f",
                          quiet=True)
        grass.del_temp_region()
    else:
        # simply rename if there is only one tile
        grass.run_command("g.rename", raster=[mt, out])


def merge_tiles(variables, tiles, bioclim, months):
    """Run patch_tiles for each of the combinations of variables"""

    prefix = options['prefix']
    for variable in variables:
        if variable == 'alt':
            mt = ['{}t{}_alt'.format(prefix, x) for x in tiles]
            out = "{}alt".format(prefix)
            patch_tiles(mt=mt, out=out, vari=variable)
        elif variable == 'bioclim':
            for i in bioclim:
                mt = ['{}t{}_bio{:02d}'.format(prefix, x, int(i))
                      for x in tiles]
                out = "{}bio{:02d}".format(prefix, int(i))
                patch_tiles(mt=mt, out=out, vari=variable, bc=i)
        else:
            for i in months:
                mt = ['{}t{}_{}{:02d}'.format(prefix, x, variable, int(i))
                      for x in tiles]
                out = "{}{}{:02d}".format(prefix, variable, int(i))
                patch_tiles(mt=mt, out=out, vari=variable, mnth=i)


# Main function
def main():
    """Main function, called at execution time."""

    # parse needed options
    variables = options['variables'].split(',')
    if options['bioclim']:
        bioclim = map(int, options['bioclim'].split(','))
        if not all(1 <= x <= 19 for x in bioclim):
            grass.warning("Values for 'bioclim' need to be within the range"
                          " 1-19. Ignoring values outside this range")
    else:
        bioclim = range(1, 20)

    if options['months']:
        months = map(int, options['months'].split(','))
        if not all(1 <= x <= 12 for x in bioclim):
            grass.warning("Values for 'months' need to be within the range"
                          " 1-12. Ignoring values outside this range")
    else:
        months = range(1, 13)

    allres = options['res'].split(',')

    # import tiles
    if options['tiles']:
        tiles = options['tiles'].split(',')
        legaltiles = [str(j)+str(i) for j in range(5) for i in range(12)]
        for t in tiles:
            if t not in legaltiles:
                grass.error("Tile {} is not a valid WorldClim tile, see "
                            "http://www.worldclim.org/tiles.php".format(t))
        for tile in tiles:
            import_variables(tile=tile, variables=variables, bioclim=bioclim,
                             months=months)

        # Merge tiles
        if not flags['p']:
            merge_tiles(variables, tiles, bioclim, months)

    # import global datasets
    if allres != ['']:
        for res in allres:
            import_variables(res=res, variables=variables, bioclim=bioclim,
                             months=months)

# Main program
if __name__ == "__main__":
    options, flags = grass.parser()
    main()
