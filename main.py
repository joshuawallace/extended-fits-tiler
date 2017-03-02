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

# Print number of HDU's
print "Number of HDU's: " + str(len(hdulist))

# Define a temporary file to hold information about the hdulist
hdulist_info_filename = 'hdulist_info.txt'

# Read the hdulist information to the file
with open(hdulist_info_filename,'w') as output_f:
    hdulist.info(output=output_f)

# Open the file and read in the information
with open(hdulist_info_filename,'r') as f:
    info = f.readlines()

# Strip off the newline characters at the end
for i in range(len(info)):
    info[i] = info[i].strip('\n')

print ""
print "The HDU's: are"
print ""

# Get the description of the different columns and print it out
info_column_description = info[1]
print info_column_description

# Redefine the info list to be only the relevant information,
# not any of the extraneous information hdulist.info prints out
info = info[2:]

# Print out the various HDU's
for line in info:
    print line
print ""

# Get list of which HDU's are image HDU's, print out their number
list_of_image_hdus = [i for i in range(len(info)) if "ImageHDU" in info[i] ]
print "Number of specifically ImageHDU's: " + str(len(list_of_image_hdus))
