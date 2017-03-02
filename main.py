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
import numpy as np

# Make sure we have at least one command line argument
if len(sys.argv) !=2:
    raise RuntimeError("I was expecting a command line argument: the name of the fits file to stitch together")

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


#print list_of_image_hdus[5].header

naxis12 = []
npixeslusedxy = []
gapsize = []
locationinarray = []
for i in range(len(list_of_image_hdus)):
    naxis12.append( (int(list_of_image_hdus[i].header['NAXIS1']), 
                     int(list_of_image_hdus[i].header['NAXIS2'])) )
    npixeslusedxy.append( (int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP NX']), 
                           int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP NY'])) )
    gapsize.append( (float(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP XGAP']), 
                     float(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP YGAP'])) )
    locationinarray.append( (int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP X']), 
                             int(list_of_image_hdus[i].header['HIERARCH ESO DET CHIP Y'])) )

x_positions = []
y_positions = []
for i in range(len(list_of_image_hdus)):
    x_positions.append(locationinarray[i][0])
    y_positions.append(locationinarray[i][1])

# Remove duplicate values from the list
x_positions = list(set(x_positions))
y_positions = list(set(y_positions))

x_size = max(x_positions)
y_size = max(y_positions)

if len(x_positions) != x_size:
    raise RuntimeError("The maximum position coordinate is different than the number of x positions")
if len(y_positions) != y_size:
    raise RuntimeError("The maximum position coordinate is different than the number of y positions")

list_of_positions = []
indices_of_positions = []

for i in range(1,y_size+1):
    column = []
    column_indices = []
    for j in range(1,x_size+1):
        for k in range(len(list_of_image_hdus)):
             if locationinarray[k][0] == j and locationinarray[k][1] == i:
                column.append(list_of_image_hdus[k])
                column_indices.append(k)
                break
    list_of_positions.append(column)
    indices_of_positions.append(column_indices)

print indices_of_positions

x_pixel_size = y_pixel_size = 0
for i in range(len(indices_of_positions)):
    index = indices_of_positions[i][0]
    y_pixel_size += naxis12[index][1] + int(gapsize[index][1])

for i in range(len(indices_of_positions[0])):
    index = indices_of_positions[0][i]
    x_pixel_size += naxis12[index][0] + int(gapsize[index][0])

print "X size of final image: " + str(x_pixel_size)
print "Y size of final image: " + str(y_pixel_size)

image_array = np.zeros( (x_pixel_size, y_pixel_size) )

y_start = 0
for i in range(y_size):
    x_start = 0
    for j in range(x_size):
        print i, j
        index = indices_of_positions[i][j] #- 1
        print index
        image_array[x_start: x_start + naxis12[index][0], y_start: y_start + naxis12[index][1] ] = np.array(list_of_image_hdus[index].data).T
        x_start += naxis12[index][0]
        
    y_start += naxis12[indices_of_positions[i][0]][1]
