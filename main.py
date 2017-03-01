##################
## Created March 1 2017 by JJW
## Takes an extended fits image and plots all the 
## images together into a single fits image
##
## Intended for Python 2.7
##
## Distributed under GNU GENERAL PUBLIC LICENSE Ver. 3
## License included in github repo and must be distributed
## with all copies of this code


from astropy.io import fits
import sys

# Make sure we have at least one command line argument
if len(sys.argv) !=2:
    raise RuntimeError("I was expecting a command line argument: the name of the fits file to stitch together")

# Open the fits file
hdulist = fits.open(sys.argv[1])

# Print and get information about the HDU's
print "Number of HDU's: " + str(len(hdulist))
hdulist_info_filename = 'hdulist_info.txt'
with open(hdulist_info_filename,'w') as output_f:
    hdulist.info(output=output_f)

with open(hdulist_info_filename,'r') as f:
    info = f.readlines()

print "Available HDU's:"
info_column_description = info[1]
print info_column_description
info = info[2:]

for line in info:
    print line

# Get list of which HDU's are image HDU's.
list_of_image_hdus = [i for i in range(len(info)) if "ImageHDU" in info[i] ]
print ""
print "Number of ImageHDU's: " + str(len(list_of_image_hdus))
