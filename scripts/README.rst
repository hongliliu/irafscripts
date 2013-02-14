How to Fit and Remove Distortion
================================
fit_coords uses a catalog of known positions to determine the geometric
transform of an image.  It requires a file with a pretty good (~1") WCS header,
so if you don't have that, try msczero first (or I guess we can write our own).

For my case, at least, there aren't enough stars per frame to measure the
distortion with a single exposure.  So my approach is to run `fit_coords` on a
whole bunch of different dithered images (in different filters, assuming the
filters have identical distortion) to use the stars' changing locations to
derive the true distortion map.

This means that for each star, we need multiple separate maps from measured
pixel coordinate to "correct" pixel coordinate.  This is achieved with
`wcsctran`.

Once we have pixel->pixel solutions for multiple images, we concatenate them
into a single file, then geomap to fit the solution.  e.g., for frame 2, I'd
do::

    cat *_2_pixpixmap.txt > pixpix2_big.txt
    geomap pixpix2_big.txt pixpix2_big.db xmin=-4000 xmax=4000 ymin=-4000 ymax=4000 transforms=frame2

The tricky and hidden bit is that the coordinates are being mapped to the
correct coordinates *in the pixel space of frame 1* (which is set by the
`pixmapextens` keyword argument).

Then (this part is untested) I assume you do something like::

    geotran @files @files//trans pixpix2_big.db transforms=frame2
