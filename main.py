##################
## Created March 1 2017 by JJW
## Takes an extended fits image and plots all the 
## images together into a single fits image
##
## Currently does not include a header to the single fits image
##
## Intended for Python 2.7
##
## Distributed under GNU GENERAL PUBLIC LICENSE Ver. 3
## License included in github repo and must be distributed
## with all copies of this code


from astropy.io import fits
import sys
import numpy as np

# Make sure we have at least one command line argument
if len(sys.argv) !=2 and len(sys.argv) != 3:
    raise RuntimeError("I was expecting at least one command line argument:\n the name of the fits file to stitch together\n the name of the output file (optional)")

# Open the fits file
hdulist = fits.open(sys.argv[1])

# Print number of HDU's
print "Number of HDU's: " + str(len(hdulist))

# Get info on the HDU's and print out
info = hdulist.info(output=False)
print ""
print "The HDU's are:"
print ""
print "# " + 'No.  Name       Type     Cards    Dimensions    Format'
for line in info:
    print line
print ""

# Check for primary HDU's; fail if there are none or more than one
primary_hdu = [hdulist[i] for i in range(len(hdulist)) if "PrimaryHDU" in info[i] ]
if len(primary_hdu) == 0:
    raise RuntimeError("There's no PrimaryHDU")
elif len(primary_hdu) > 1:
    raise RuntimeError("There is more than one PrimaryHDU!")
primary_hdu = primary_hdu[0]

# Print out the primary HDU
#print "PrimaryHDU header:"
#print primary_hdu.header

# Get list of which HDU's are image HDU's, print out their number
list_of_image_hdus = [hdulist[i] for i in range(len(hdulist)) if "ImageHDU" in info[i] ]
print "Number of specifically ImageHDU's: " + str(len(list_of_image_hdus))

#Define various empty lists for collecting useful info
naxis12 = []
npixeslusedxy = []
gapsize = []
locationinarray = []

for i in range(len(list_of_image_hdus)):
    # The number of axes of each individual set of data
    naxis12.append( (int(list_of_image_hdus[i].header['NAXIS1']), 
                     int(list_of_image_hdus[i].header['NAXIS2'])) )
    # The number of pixels in each individual set of data
    npixeslusedxy.append( (int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP NX']), 
                           int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP NY'])) )
    # The size of the gap between data images
    gapsize.append( (float(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP XGAP']), 
                     float(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP YGAP'])) )
    # The location of the image inside the larger array of images
    locationinarray.append( (int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP X']), 
                             int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP Y'])) )

# Figure out which x and y positions in the array of image there are
x_positions = []
y_positions = []
for i in range(len(list_of_image_hdus)):
    x_positions.append(locationinarray[i][0])
    y_positions.append(locationinarray[i][1])

# Remove duplicate values from the list
x_positions = list(set(x_positions))
y_positions = list(set(y_positions))

# Figure out dimensions of array of individual images
x_size = max(x_positions)
y_size = max(y_positions)

if len(x_positions) != x_size:
    raise RuntimeError("The maximum position coordinate is different than the number of x positions")
if len(y_positions) != y_size:
    raise RuntimeError("The maximum position coordinate is different than the number of y positions")

# Figure out which image belongs where in the array
list_of_positions = []
indices_of_positions = []
for i in range(1,y_size+1):
    row = [] # For collecting images along a given row
    row_indices = [] # For collecting indices of images along a given row
    for j in range(1,x_size+1):
        for k in range(len(list_of_image_hdus)):
             if locationinarray[k][0] == j and locationinarray[k][1] == i: # If the image belongs in this position in the array
                row.append(list_of_image_hdus[k])
                row_indices.append(k)
                break
    list_of_positions.append(row) # Append the row values, move on to next column
    indices_of_positions.append(row_indices) # Append the row values, move on to next column

# Print out the 2-d arrangement of the images
print indices_of_positions

# Figure out the dimensions in pixels of the array of images
x_pixel_size = y_pixel_size = 0
for i in range(len(indices_of_positions)): # Figure out y pixel size
    index = indices_of_positions[i][0]
    y_pixel_size += naxis12[index][1] + int(gapsize[index][1])

for i in range(len(indices_of_positions[0])): # Figure out x pixel size
    index = indices_of_positions[0][i]
    x_pixel_size += naxis12[index][0] + int(gapsize[index][0])

# Print out the pixel size
print "X pixel size of final image: " + str(x_pixel_size)
print "Y pixel size of final image: " + str(y_pixel_size)

# Declare the image array
image_array = np.zeros( (x_pixel_size, y_pixel_size) )

y_start = 0 # Used to keep track of column number
for i in range(y_size):
    x_start = 0 # Used to keep track of row number
    for j in range(x_size):
        index = indices_of_positions[i][j] # Get index of the image
        image_array[x_start: x_start + naxis12[index][0], y_start: y_start + naxis12[index][1] ] = np.array(list_of_image_hdus[index].data).T # Add image to overall image array
        x_start += naxis12[index][0] # Move x_start for the next image
        
    y_start += naxis12[indices_of_positions[i][0]][1] # Move y_start for the next image

# Write the data to an HDU
#output_hdu = fits.PrimaryHDU(data=image_array, header=primary_hdu) #for some reason it doesn't work for me to just read in primar_hdu, don't know why
output_hdu = fits.PrimaryHDU(data=image_array)

# Check if an output file name was given as command line argument.  If not, use a default name
if len(sys.argv) == 3:
    output_file = sys.argv[2]
else:
    output_file = "output.fits"

# Save the fits file
output_hdu.writeto(output_file)
