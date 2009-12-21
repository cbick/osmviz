


class OSMManager(object):
  """
  An OSMManager manages the retrieval and storage of Open Street Map
  images. The basic utility is the createOSMImage() method which
  automatically gets all the images needed, and tiles them together 
  into one big image.
  """
  def __init__(self):
    pass

  def getTileCoord(self, lon_deg, lat_deg, zoom=14):
    """
    Given lon,lat coords in DEGREES, and a zoom level,
    returns the (x,y) coordinate of the corresponding tile #.
    (http://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python)
    """
    lat_rad = lat_deg * math.pi / 180.0
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 
                                (1 / math.cos(lat_rad))) 
                 / math.pi) / 2.0 * n)
    return(xtile, ytile)

  def getTileURL(self, tile_coord, zoom=14):
    """
    Given x,y coord of the tile to download, and the zoom level,
    returns the URL from which to download the image.
    """
    params = (zoom,tile_coord[0],tile_coord[1])
    return "http://tile.openstreetmap.org/%d/%d/%d.png" % params

  def getLocalTileFilename(self, tile_coord, zoom=14):
    """
    Given x,y coord of the tile, and the zoom level,
    returns the filename to which the file would be saved
    if it was downloaded. That way we don't have to kill
    the osm server every time the thing runs.
    """
    params = (zoom,tile_coord[0],tile_coord[1]);
    return "maptiles/%d_%d_%d.png" % params

  def retrieveTileImage(self,tile_coord,zoom=14):
    """
    Given x,y coord of the tile, and the zoom level,
    retrieves the file to disk if necessary and 
    returns the local filename.
    """
    import urllib
    import os.path as path
    filename = self.getLocalTileFilename(tile_coord,zoom)
    if not path.isfile(filename):
      url = self.getTileURL(tile_coord,zoom)
      urllib.urlretrieve(url, filename=filename);
    return filename

  def tileNWLatlon(self,tile_coord,zoom=14):
    """
    Given x,y coord of the tile, and the zoom level,
    returns the (lat,lon) coordinates of the upper
    left corner of the tile.
    """
    xtile,ytile = tile_coord
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = lat_rad * 180.0 / math.pi
    return(lat_deg, lon_deg)


  def createOSMImage(self, minlon, maxlon, minlat, maxlat,zoom=14):
    """
    Given bounding latlons (in degrees), and an OSM zoom level,
    creates a pygame image constructed from OSM tiles.
    Returns (img,bounds) where img is the constructed pygame image,
    and bounds is the (lonmin,lonmax,latmin,latmax) bounding box
    which the tiles cover.
    """
    topleft = minX, minY = self.getTileCoord(minlon, maxlat);
    bottomright = maxX, maxY = self.getTileCoord(maxlon, minlat);
    new_maxlat, new_minlon = self.tileNWLatlon( topleft, zoom )
    new_minlat, new_maxlon = self.tileNWLatlon( (maxX+1,maxY+1), zoom )
    # tiles are 256x256
    pix_width = (maxX-minX+1)*256
    pix_height = (maxY-minY+1)*256
    surf = pygame.Surface( (pix_width,pix_height) )
    print "Retrieving %d tiles..." % ( (1+maxX-minX)*(1+maxY-minY) ,)

    for x in range(minX,maxX+1):
      for y in range(minY,maxY+1):
        fname = self.retrieveTileImage((x,y),zoom)
        img = pygame.image.load(fname);
        x_off = 256*(x-minX)
        y_off = 256*(y-minY)
        surf.blit( img, (x_off,y_off) );
        del img
    print "... done."
    return surf, (new_minlon, new_maxlon, new_minlat, new_maxlat)

