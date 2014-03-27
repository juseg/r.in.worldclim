r.in.worldclim
==============

**Requires:** `GRASS GIS`_.

**r.in.worldclim** is a Python script for `GRASS GIS`_ to import multiple files from the `WorldClim current`_ climate dataset. The data can be imported by tiles with ``tiles=...`` or globally with ``res=...``. The script inflates requested files from their original archives before importing them as raster maps into GRASS. In GRASS, type ``r.in.worldclim.py --help`` for a more complete list of options.

Examples
--------

Import global mean temperature at 10 arc-min resolution::

    r.in.worldclim.py fields=tmean res=10m

Import temperature and precipitation data for tile 16 (central Europe)::

    r.in.worldclim.py fields=tmean,prec tiles=16

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

