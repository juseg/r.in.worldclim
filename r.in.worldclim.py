#!/usr/bin/env python

############################################################################
#
# MODULE:      r.in.worldclim
#
# AUTHOR(S):   Julien Seguinot
#
# PURPOSE:     Import multiple WorldClim current [1] climate data.
#
# COPYRIGHT:   (c) 2011 Julien Seguinot
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

# Todo:
# * warn for overriding
# * import single files
# * interactive download
# * support for past data

# Version history:
# * 30/06/2011
#  - corrected a bug in global 30s file naming
# * 25/05/2011 (0.2)
#  - support for tiled data
#  - use os.path.join() for portability
#  - parse the script in functions for readability
# * 16/05/2011 (0.1)
#  - first version, import current global data only

#%Module
#% description: Import multiple WorldClim current climate data.
#% keywords: raster import worldclim
#%End

#%option
#% key: fields
#% type: string
#% description: Fields(s) to import
#% options: tmin,tmax,tmean,prec,bio,alt
#% required: yes
#% multiple: yes
#%end
#%option
#% key: inputdir
#% type: string
#% gisprompt: old,file,input
#% description: Directory containing input files (default: current)
#% required: no
#%end
#%option
#% key: res
#% type: string
#% description: Global set resolution(s) to import
#% options: 30s,2.5m,5m,10m
#% required: no
#% multiple: yes
#%end
#%option
#% key: tiles
#% type: integer
#% description: 30 arc-minutes tiles(s) to import
#% options: 00,01,02,03,04,05,06,07,08,09,010,011,10,11,12,13,14,15,16,17,18,19,111,111,20,21,22,23,24,25,26,27,28,29,212,211,30,31,32,33,34,35,36,37,38,39,313,311,40,41,42,43,44,45,46,47,48,49,414,411
#% required: no
#% multiple: yes
#%end
#%option
#% key: layers
#% type: integer
#% description: Layer(s) to import (default: all)
#% options: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18
#% required: no
#% multiple: yes
#%end
#%option
#% key: prefix
#% type: string
#% description: Prefix for imported raster layers
#% required: no
#% answer: wc_
#%end

import os
from zipfile import ZipFile
from grass.script import core as grass

### GRASS parser output processing ###

def grass_int_list(option):
		"""Return a list of integers from grass parsed option"""
		if option:
			return map(int, grass_str_list(option))
		else:
			return []

def grass_str_list(option):
		"""Return a list of strings from grass parsed option"""
		return option.split(',')

### Import functions ###

def import_layer(field, region, res=None, tile=None, layer=None):
		"""Wrapper to the import_file() function"""

		# pass arguments to the import file function via naming funcions
		import_file(
			file_name(field, layer=layer, res=res, tile=tile),
			archive_name(field, layer=layer, res=res, tile=tile),
			output_name(field, layer=layer, res=res, tile=tile),
			region)

def import_file(filename, archive, output, region):
		"""Extracts one binary file from its archive and import it"""

		# test if the file exists
		try:
			a = ZipFile(archive, 'r')
		except:
			grass.error('could not open ' + archive)
			return

		# create a grass tempdir
		tempdir = grass.tempfile()
		grass.try_remove(tempdir)
		os.mkdir(tempdir)

			# NOTE for GRASS 7: use grass.tempdir() instead
			#tempdir = grass.tempdir()

		# extract the layer there
		grass.message('inflating ' + filename + '...')
		a.extract(filename, tempdir)
		a.close()
		tempfile = os.path.join(tempdir, filename)

			# NOTE for Python 2.7: use a with statement instead
			#with ZipFile(archive + '.zip', 'r') as a:
			#	a.extract(file + '.bil', tempfile)

		# import the layer into GRASS
		grass.message('importing ' + filename + ' as ' + output + '...')
		grass.run_command('r.in.bin',	flags='s', overwrite=True, input=tempfile, output=output, bytes=2, anull=-9999, **region)

		# remove the inflated file and tempdir
		grass.try_remove(tempfile)
		grass.try_rmdir(tempdir)

def import_fields(res=None, tile=None):
		"""Import requested fields for a given tile or resolution"""

		# parse needed options
		inputdir = options['inputdir']
		fields   = grass_str_list(options['fields'])
		layers   = grass_int_list(options['layers'])

		# compute region extents
		region = region_extents(res=res, tile=tile)

		# for each of the requested fields
		for field in fields:

			# alt is a special case since there is only one layer
			if field == 'alt':
				import_layer('alt', region, res=res, tile=tile)

			# bio is a bit of a special case too since there are 18 layers
			elif field == 'bio':
				for layer in ( layers if layers else range(1,19) ):
					import_layer(field, region, layer=layer, res=res, tile=tile)

			# other fields have 12 layers
			else:
				for layer in ( layers if layers else range(1,13) ):
					if layer > 12:
						grass.error(field + str(layer) + ': no such layer')
					else:
					 import_layer(field, region, layer=layer, res=res, tile=tile)

### Input and output name and region conventions ###

def archive_name(field, res=None, tile=None, layer=None):
		"""Return the name of the corresponding zip archive"""

		# for global data (the bio 30s data is packed in two files)
		if res:
			if field == 'bio' and res == '30s':
				if layer <= 9 :
					archive = 'bio1-9_30s_bil.zip'
				if layer >= 10:
					archive = 'bio10-19_30s_bil.zip'
			else:
				archive = field + '_' + res.replace('.','-') + '_bil.zip'

		# for tiled data
		elif tile:
			archive = field + '_' + str(tile) + '.zip'

		# return full path
		return os.path.join(options['inputdir'], archive)

def file_name(field, res=None, tile=None, layer=None):
		"""Return the name of the conrresponding binary file"""

		# convert layer to a string or empty string if None
		if layer: layerstr = str(layer)
		else    : layerstr = ''

		# for global data (the 30s data has different naming)
		if res:
			if field <> 'alt' and res == '30s':
				return field + '_' + layerstr + '.bil'
			else:
				return field + layerstr + '.bil'

		# for tiled data
		elif tile:
			return field + layerstr + '_' + str(tile) + '.bil'

def output_name(field, res=None, tile=None, layer=None):
		"""Return an output name for the resulting raster map"""

		# convert layer to a string or empty string if None
		if layer: layerstr = str(layer)
		else    : layerstr = ''

		# for global data
		if res:
			name = res + '_' + field + layerstr

		# for tiled data
		elif tile:
			name = 't' + str(tile) + '_' + field + layerstr

		# return full name with prefix
		return options['prefix'] + name

def region_extents(res=None, tile=None):
		"""Return region extents for a given resolution or tile"""

		# for global data
		if res:
			if   res == '10m' : rows =   900; cols =  2160 
			elif res == '5m'  : rows =  1800; cols =  4320
			elif res == '2.5m': rows =  3600; cols =  8640
			elif res == '30s' : rows = 18000; cols = 43200
			return {
				'north':   90, 'south':  -60,
				'west' : -180, 'east' :  180,
				'rows' : rows, 'cols' : cols}

		# for tiled data
		elif tile:
			tilerow = int(tile/10)
			tilecol = tile-10*tilerow
			return {
				'north': 30*(3-tilerow), 'south': 30*(2-tilerow),
				'west' : 30*(tilecol-6), 'east' : 30*(tilecol-5),
				'rows' : 3600          , 'cols' : 3600}

### Main function ###

def main():
		"""Main function, called at execution time"""

		# parse requested resolutions and tiles
		allres = grass_str_list(options['res'])
		tiles  = grass_int_list(options['tiles'])

		# warm for data overriding

		# import global datasets
		if allres <> ['']:
			for res in allres:
				import_fields(res=res)

		# import requested tiles
		for tile in tiles:
			import_fields(tile=tile)

### Main program ###

if __name__ == "__main__":
		options, flags = grass.parser()
		main()

# Links
# [1] http://www.worldclim.org/current

