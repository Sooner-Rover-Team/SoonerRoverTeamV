# Rover Map Tile Generator

Generates slippy map tiles, compatible with leaflet, from a really hi-res sattelite image and the image's lat/lon range.

We needed this to generate an offline slippy map that we could plot
rover paths on. Map services that serve compatible tiles tend to (I think all of them?) have
clauses in their ToC about not being able to proxy or save tiles on the server-side.
This is almost certainly not targeted at us, but it's still a ToC violation,
so we needed another solution.

We used the [USGS Earth Explorer](https://earthexplorer.usgs.gov/) to obtain a super high-res .tif file
of a satellite image over our region of interest ([The Mars Desert Research Station](http://mdrs.marssociety.org/)).
If you're on the rover team and happened to have lost the source image,
the image is from the NAIP dataset, entity id `m_3811034_se_12_1_20160707`.
(scroll down to search criteria, hit the 'decimal' button just below the polygon/circle/predefined area buttons, to switch to decimal coordinate input.
Enter 38.3750 for lat, and  -110.8125 for lon. Go to data sets and search for NAIP and enable it. Go to additional criteria,
select the NAIP data set from the dropdown, expand the entity id field, paste in `m_3811034_se_12_1_20160707`, go to results.
You should see only one entry. Click the download options button, select full resolution, and wait for a long time.
It could take 10 minutes or more to load. It won't really look like it's doing anything - just be patient. Wait and wait and wait. Eventually, the file will start downloading.)

It should be one large image named `m_3811034_se_12_1_20160707.tif`, the .txt file it comes with will have coordinate info to pass to the CLI.

## Dependencies

You'll need opencv and numpy installed - I used version 4.5.5 of opencv and version 1.22.3 of numpy.

(To run the dev server to serve those tiles, you'll need to just run `npm install`.
The dev server will display a map centered on the map region for the rover team, if you want to see a different region
you can just change the coordinates in `index.html`.)

**For the rover team - don't use this devserver.js, use server.py in the `RoverMap` directory**

## Usage

The CLI needs a source image to pull tiles from and it needs to know where that source image comes from on the globe.

`python generate_tiles.py [imagename] [southLatitude] [northLatitude] [westLongitude] [eastLongitude]`.

If you're on the rover team, you want to invoke it with
`python generate_tiles.py m_3811034_se_12_1_20160707.tif 38.3750 38.4375 -110.8125 -110.7500`

The tiles will be output to `./tiles/`, of the format "z{z}, x{x}, y{y}.jpg", so you can serve the tiles as static content.
You'll point your leaflet tile layer url template to some route on your server like "/tiles/z/x/y", pick off those values of z, y, x, and look for a file named with those values. Check the example in devserver.js and index.html to see it in action.

If you're on the rover team, the tiles directory needs to go one level above, in `Mission Control/RoverMap/tiles`, not here.

For example, say you have some tile named `z11, x393, y786.jpg`, stored in some tiles folder somewhere.
When the user pans leaflet over that tile, leaflet will make a request to "/tiles/11/393/786" on your server,
you'll pick off those values, read in the file `z11, x393, y786.jpg`, and send that off.


## How tiles are generated

A slippy map tile is defined by a zoom level and an x, y position. All tiles are 256x256 pixels.
So zoom level 0 encompasses the entire planet's map in one 256x256 image tile. Zoom level 1 doubles your zoom, so the world will now be comprised of 4 256x256 tiles.
The [OSM Wiki Entry](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames) on this is a good resource.

The program assumes an arbitrary zoom value of 10 to begin, and goes all the way to 19. You can pass in an optional last argument to change this.
The `-b` flag changes the base value, and `-m` changes the max zoom. `python generate_tiles.py filename bunch_of_latlonstuff -b 5 -m 22`
will start at zoom level 5, and go all the way to 22.

The program begins by generating a single tile at the base zoom level, and it will only generate
subdivisions of this tile. You can keep increasing the value you set as the base value if it cuts off your map.

Make sure that you set your client's leaflet map to
be at the right zoom level by default - just set it to whatever base zoom level you pass in with the b flag.
If you didn't change it, set it to 10.
If there's no tile for some zoom level, the leaflet map will display nothing,
so it'll look like there are no tiles until you zoom in to a zoom
level which you generated tiles for. You could just generate
starting at level 0, that way you'd always be able to find the area
you generated tiles for, or set the leaflet map to have a max zoom
equal to whatever base zoom level you used.

The program will figure out what tiles need to be generated, and then will find where the map image should intersect these tiles,
pick off that subimage, and correctly scale and place it. It won't generate tiles that do not intersect with the map region.

Untangling the transformations between (lat, lon) representing (vert, horiz) where right and up are positive,
(x, y) representing (horiz, vert) where right and down are positive, and np array indicies where (row, col) represent (vert, horiz), and tile (x, y)'s representing (horiz, vert) where (I think?) right and down are positive,
was an absolute mess, but it works.
I must have seen every possible combination of ways in which these coordinates could be confused, and all of the
weird space-warping maps resulted from them.
