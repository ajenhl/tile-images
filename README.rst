tile-images
===========

tile-images is a script to generate a PDF from a series of images. It
performs two main functions beyond simple PDF generation:

* Tile the images to fit a specified paper size, cutting up the images
  as needed.

* Interleave pairs of images so that when printed double-sided, each
  side tiles to form one whole image.

A consequence of this is that the program must be passed an even
number of images, and the images must be of the same size (though
images will be rotated if necessary). Strictly speaking only each pair
of images need be the same size, for the desired output, but the
program is not that clever.
