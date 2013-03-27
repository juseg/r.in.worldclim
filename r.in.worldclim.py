#!/usr/bin/env python

############################################################################
#
# MODULE:      r.in.worldclim
#
# AUTHOR(S):   Julien Seguinot
#
# PURPOSE:     Import multiple WorldClim current [1] global climate data.
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

#%Module
#% description: Import multiple WorldClim current global climate data.
#% keywords: raster import worldclim
#%End
#%option
#% key: res
#% type: string
#% description: Resolution(s) to import
#% options: 30s,2-5m,5m,10m
#% required: yes
#% multiple: yes
#%end
#%option
#% key: fields
#% type: string
#% description: Fields(s) to import (use tmin for all tmin* fields etc)
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
#% description: Prefix for imported raster layers (default: wc)
#% required: no
#% answer: wc
#%end

import os # NOTE for GRASS 7: becomes unnecessary
from zipfile import ZipFile
from grass.script import core as grass

def import_file(archive, filename, output, rows, cols):
		"""Import WorldClim binary file as raster map

		@param archive archive where to find the input file
		@param filename input file to import
		@param output name of output raster map
		@param rows number of rows
		@param cols number of columns
		"""

		# test if the file exists
		try:
			a = ZipFile(archive + '.zip', 'r')
		except:
			grass.error('could not open ' + archive + '.zip')
			return

		# create a grass tempdir
		tempdir = grass.tempfile()
		grass.try_remove(tempdir)
		os.mkdir(tempdir)

			# NOTE for GRASS 7: use grass.tempdir() instead
			#tempdir = grass.tempdir()

		# extract the layer there
		grass.message('inflating ' + filename + '.bil...')
		a.extract(filename + '.bil', tempdir)
		a.close()

			# NOTE for Python 2.7: use a with statement instead
			#with ZipFile(archive + '.zip', 'r') as a:
			#	a.extract(file + '.bil', tempfile)

		# import the layer into GRASS
		grass.message('importing ' + output + '...')
		grass.run_command('r.in.bin',	flags='s', overwrite=True,
			input=tempdir + '/' + filename + '.bil', output=output ,
			north=90  , south=-60  , east=180,  west=-180,
			bytes=2   , anull=-9999, rows=rows, cols=cols)

		# remove the inflated file and tempdir
		grass.try_remove(tempdir + '/' + filename + '.bil')
		grass.try_rmdir(tempdir)

def main(): # main function, called at execution time
		# parse arguments (unfortunately GRASS parser seem not to return lists)
		allres   = options['res'].split(',')    # required
		fields   = options['fields'].split(',') # required
		inputdir = options['inputdir']          # optional
		try:    layers = map(int, options['layers'].split(','))
		except: layers = []                     # optional
		prefix   = options['prefix']            # optional

		# store numbers of rows in a dictionary
		rowsdict = {
			'10m' : 900,
			'5m'  : 1800,
			'2-5m': 3600,
			'30s' : 18000}

		# store numbers of cols in a dictionary
		colsdict = {
			'10m' : 2160,
			'5m'  : 4320,
			'2-5m': 8640,
			'30s' : 43200}

		# for each of the requested resolutions
		for res in allres:
			resprefix = prefix + '_' + res + '_'
			rows      = rowsdict[res]
			cols      = colsdict[res]

			# for each of the requested fields
			for field in fields:

				# alt is a special case since there is only one layer
				if field == 'alt': import_file(
					inputdir + 'alt_' + res + '_bil',
					'alt',
					resprefix + 'alt',
					rows, cols)

				# bio is a little bit of a special case too
				elif field == 'bio':

					# for each of the requested or all 18 layers
					for layer in ( layers if layers else range(1,19) ):

						# the 30s resolution is packed in two files with different naming
						if res == '30s':
							if layer <= 9 : import_file(
								inputdir + 'bio1-9_30s_bil',
								'bio_' + str(layer),
								resprefix + 'bio' + str(layer),
								rows, cols)
							if layer >= 10: import_file(
								inputdir + 'bio10-19_30s_bil',
								'bio_' + str(layer),
								resprefix + 'bio' + str(layer),
								rows, cols)

						# the rest is named on the regular basis
						else: import_file(inputdir + 'bio_' + res + '_bil',
							'bio' + str(layer),
							resprefix + 'bio' + str(layer),
							rows, cols)

				# now the other fields are all similar
				else:

					# for each of the requested or all 12 layers
					for layer in ( layers if layers else range(1,13) ):
						filename = field + str(layer)

						# emit a warning if layer is out of range (can't happen for bio)
						if int(layer) > 12: grass.warning(filename + ' : no such layer')

						# else import it
						else: import_file(
							inputdir + field + '_' + res + '_bil',
							filename,
							resprefix + filename,
							rows, cols)

if __name__ == "__main__":
    options, flags = grass.parser()
    main()

# Links
# [1] http://www.worldclim.org/current

