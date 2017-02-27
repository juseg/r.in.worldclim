r.in.worldclim*
==============

**Requires:** `GRASS GIS`_.

**r.in.worldclim** is a Python script for `GRASS GIS`_ to import multiple files from the `WorldClim current`_ climate dataset. The data can be imported by tiles with ``tiles=...`` or globally with ``res=...``. The script inflates requested files from their original archives before importing them as raster maps into GRASS. In GRASS, type ``r.in.worldclim.py --help`` for a more complete list of options.

**r.in.worldclim.tiles** is a Python script for `GRASS GIS`_ to import to find tiles from the `WorldClim current`_ climate dataset, get the list of tiles that cover an user-defined region of interest, and optionally downloads the tiles. 

Examples
--------

Import global mean temperature at 10 arc-min resolution::

    r.in.worldclim variables=tmean res=10m

Import temperature and precipitation data for Nepal using the vector layer 'nepal' to define the region of interest. r.in.worldclim will download the tiles covering Nepal (tile 18,28) to the current directory. r.in.worldclim will import the layers in the zipfile in the GRASS GIS database, and patch for each variable the two imported tiles to create one layer per variable::

    r.in.worldclim.tiles variables=tmean,prec vector=central_europe
    r.in.worldclim variables=tmean,prec tiles=18,28

References
----------

Hijmans, R.J., S.E. Cameron, J.L. Parra, P.G. Jones and A. Jarvis (2005).
Very high resolution interpolated climate surfaces for global land areas.
International Journal of Climatology 25, 1965-1978
doi:`10.1002/joc.1276 <http://dx.doi.org/10.1002/joc.1276>`_.

J. Seguinot, C. Khroulev, I. Rogozhina, Q. Zhang, and A. Stroeven (2013).
The effect of climate forcing on numerical simulations of the Cordilleran Ice Sheet at the last Glacial Maximum.
The Cryosphere Discussions, 7, 1-42,
doi:`10.5194/tcd-7-6171-2013 <http://dx.doi.org/10.5194/tcd-7-6171-2013>`_.

.. links

.. _GRASS GIS: http://grass.osgeo.org
.. _WorldClim current: http://www.worldclim.org/current/
.. _WorldCLim tiles: http://wwww.worldclim.org/tiles.php

