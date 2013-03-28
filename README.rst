r.in.worldclim
==============

**Requires:** `GRASS GIS`_.

**r.in.worldclim** is a Python script for `GRASS GIS`_ to import multiple files from the `WorldClim current`_ climate dataset. The data can be imported by tiles with ``tiles=...`` or globally with ``res=...``. The script does the job of inflating the requested files from their original archives before importing them as raster maps into GRASS. In GRASS, type ``r.in.worldclim.py --help`` for a more complete list of options.

.. links

.. _GRASS GIS: http://grass.osgeo.org
.. _WorldClim current: http://www.worldclim.org/current/

