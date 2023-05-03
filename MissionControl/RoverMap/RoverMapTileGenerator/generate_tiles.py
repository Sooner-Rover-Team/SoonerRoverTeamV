import numpy as np
import cv2 as cv
import argparse
import math

# from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
def deg2num(lat_deg, lon_deg, zoom):
  lat_rad = math.radians(lat_deg)
  n = 2.0 ** zoom
  xtile = int((lon_deg + 180.0) / 360.0 * n)
  ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
  return (xtile, ytile)

# also from https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames
def num2deg(xtile, ytile, zoom):
  n = 2.0 ** zoom
  lon_deg = xtile / n * 360.0 - 180.0
  lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
  lat_deg = math.degrees(lat_rad)
  return (lat_deg, lon_deg)


#
# We represent lat/lon regions as intervals, where interval[0] <= interval[1].
# This is useful to figure out where the lat/lon bounds of a tile
# intersect the map. 
#

def intersectIntervals(int1, int2):
    adjusted1 = (min(int1), max(int1))
    adjusted2 = (min(int2), max(int2))
    return (max((adjusted1[0], adjusted2[0])), min(adjusted1[1], adjusted2[1]))

def isValueWithinInterval(value, interval):
    return value >= interval[0] and value <= interval[1] 

def isIntervalNonempty(interval):
    return interval[0] <= interval[1]

def isIntervalWithinThisOtherInterval(innerInterval, outerInterval):
    return innerInterval[0] >= outerInterval[0] and outerInterval[1] >= innerInterval[1]


# These latlons are the corner coordinates of the image map.
# The base zoom value is some arbitrary zoom value to start at.
# you could approximate this by following the table at https://wiki.openstreetmap.org/wiki/Zoom_levels
# tiles will be generated up to the maxZoomValue
def generateTiles(image_name, northWestLatLon, southEastLatLon, baseZoomValue, maxZoomValue):

    mapLatBounds = [southEastLatLon[0], northWestLatLon[0]]
    mapLonBounds = [northWestLatLon[1], southEastLatLon[1]]


    # The goal here is to get the one tile of the baseZoomValue that fully encompasses the map image.
    # We just find the tile that contains the top left corner and assume that the baseZoomValue encompasses the whole map. 
    # You should decrease your baseZoomValue in case this cuts off your map
    baseTile = deg2num(*northWestLatLon, baseZoomValue)
    # Why do we run deg2num and pipe it straight to num2deg?
    # to get the lat/lon of the top left corner of the biggest tile that we'll generate.
    # We'll use that lat/lon, but increase the zoom value,
    # to compute what index we should start at for lower zoom levels.
    tileBaseLatLon = num2deg(*baseTile, baseZoomValue)


    mapImage = cv.imread(image_name)

    mapImageHeight = mapImage.shape[0]
    mapImageWidth = mapImage.shape[1]


    # From a lat/lon in world space, convert it to a pixel location
    # on the mapImage. This may be negative or outside the bounds of the image,
    # representing that the map doesn't contain that point.
    def latLonToPixels(lat, lon):
        # latitude maps to y values
        # longitude maps to x values

        # the idea is that we find what percent we are along
        # our latitude/longitude ranges on the map,
        # and find that percentage along the horiz/vertical
        # axes of the map image.

        longitudeRange = southEastLatLon[1] - northWestLatLon[1]
        latitudeRange = southEastLatLon[0] - northWestLatLon[0]

        xValue = mapImageWidth * (lon - northWestLatLon[1]) / longitudeRange
        yValue = mapImageHeight * (lat -  northWestLatLon[0]) / latitudeRange

        return (round(xValue), round(yValue)) 


    for zoomInFactor in range(0, maxZoomValue - baseZoomValue + 1):
        # the zoomInFactor is the number of divisons
        # by 2 of the base tile size.
        numTilesToCreate = 2**zoomInFactor


        # the true zoom value of a tile
        z = baseZoomValue + zoomInFactor
        print(f"Generating tiles for zoom level {z}/{19}", flush=True)

        # the index of the north western most (minimum x and y)
        # tile that we generate in this step.
        # we'll move to the right and down to fill out the grid for this step.
        tileNumRoot = deg2num(*tileBaseLatLon, z)

        for tileDx in range(0, numTilesToCreate):
            for tileDy in range(0, numTilesToCreate):
                tileX = tileNumRoot[0] + tileDx
                tileY = tileNumRoot[1] + tileDy
                # figure out what our lat/lon bounds are
                tileTopLeftLatLon = num2deg(tileX, tileY, z)
                tileBottomRightLatLon = num2deg(tileX+1, tileY+1, z)

                tileLatBounds = [min(tileTopLeftLatLon[0], tileBottomRightLatLon[0]), max(tileTopLeftLatLon[0], tileBottomRightLatLon[0])]
                tileLonBounds = [min(tileTopLeftLatLon[1], tileBottomRightLatLon[1]), max(tileTopLeftLatLon[1], tileBottomRightLatLon[1])]


                # figure out what region of lat and lon from our tile intersects the map
                latRangeToDraw = intersectIntervals(tileLatBounds, mapLatBounds)
                lonRangeToDraw = intersectIntervals(tileLonBounds, mapLonBounds)



                # if we have a meaningful intersection in both axes, we need to draw
                # some section of the map!                
                if isIntervalNonempty(latRangeToDraw) and isIntervalNonempty(lonRangeToDraw):
                    # This is the base of the tile. We'll draw the intersected map region on it.
                    blankImage = np.zeros((256, 256, 3), np.uint8)


                    ## These pixel ranges are on the tile, not the mapImage
                    yPixelRange = (
                        round(256 * ((lonRangeToDraw[0] - tileLonBounds[0]) / (tileLonBounds[1] - tileLonBounds[0]))),
                        round(256 * ((lonRangeToDraw[1] - tileLonBounds[0]) / (tileLonBounds[1] - tileLonBounds[0])))
                    )

                    # Some insane coordinate axis garbling.
                    # transposed and inverted arguments, which I discovered
                    # by literally bruteforcing all 8 possible combinations
                    # of inversions and transpositions until it worked.
                    xPixelRange = (
                        256 - round(256 * (latRangeToDraw[1] - tileLatBounds[0]) / (tileLatBounds[1] - tileLatBounds[0])),
                        256 - round(256 * (latRangeToDraw[0] - tileLatBounds[0]) / (tileLatBounds[1] - tileLatBounds[0])),
                    )

                    pixelRangeWidth = xPixelRange[1] - xPixelRange[0]
                    pixelRangeHeight = yPixelRange[1] - yPixelRange[0]
                    
                    # no need to draw a tile with no section of the map.
                    if pixelRangeWidth == 0 or pixelRangeHeight == 0:
                        continue

                    # Figure out what region of the mapImage to pull off,
                    # resize it, and stick it into the tile image.
                    imageTopLeft = latLonToPixels(latRangeToDraw[1], lonRangeToDraw[0])
                    imageBottomRight = latLonToPixels(latRangeToDraw[0], lonRangeToDraw[1])
                    mapSeg = mapImage[
                        imageTopLeft[1]:imageBottomRight[1],
                        imageTopLeft[0]:imageBottomRight[0], 
                    ]
                    blankImage[xPixelRange[0]:xPixelRange[1], yPixelRange[0]:yPixelRange[1]] = cv.resize(mapSeg, (yPixelRange[1] - yPixelRange[0], xPixelRange[1] - xPixelRange[0]))


                    cv.imwrite("tiles/z{}, x{}, y{}.jpg".format(z, tileX, tileY), blankImage)
                else:
                    continue



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generates slippy map tiles from a very hir-res map image')
    parser.add_argument("image_name", help="The large map image to take tiles from")
    parser.add_argument("southLatitude", help="The latitude of the south edge of the map region in the image", type=float)
    parser.add_argument("northLatitude", help="The latitude of the north edge of the map region in the image", type=float)
    parser.add_argument("westLongitude", help="The longitude of the west edge of the map region in the image", type=float)
    parser.add_argument("eastLongitude", help="The longitude of the east edge of the map region in the image", type=float)
    parser.add_argument("-b", "--baseZoomValue", help="What zoom level the entire map represents. As far as I can tell, you can set this to any arbitrary reasonable value. Default is 10.", type=int, required=False, default=10)
    parser.add_argument("-m", "--maxZoomValue", help="The maximum zoom level of tile to be generated. Default is 19.", type=int, required=False, default=19)

    args = parser.parse_args()

    
    generateTiles(args.image_name, [args.northLatitude, args.westLongitude], [args.southLatitude, args.eastLongitude], args.baseZoomValue, args.maxZoomValue)
