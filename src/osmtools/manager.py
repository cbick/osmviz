"""
OpenStreetMap Management Tool:
  - Provides simple interface to retrieve and tile OSM images
  - Can use pygame or PIL (to generate pygame Surfaces or PIL images)

Basic idea:
  1. Choose an ImageManager class and construct an instance.
     - Pygame and PIL implementations available
     - To make your own custom ImageManager, override the ImageManager
       class.
  2. Construct an OSMManager object.
     - Can provide custom OSM server URL, etc.
  3. Use the OSMManager to retrieve individual tiles and do as you please
     or patch tiles together into a larger image for you.
"""

import math
import urllib
import os.path as path


class ImageManager(object):
  """
  Simple abstract interface for creating and manipulating images, to be used
  by an OSMManager object.
  """

  def __init__(self):
    self.image = None
  
  ### TO BE OVERRIDDEN ###

  def paste_image(self,img,xy):
    """
    To be overridden.
    Given an already-loaded file, paste it into the internal image
    at the specified top-left coordinate.
    """
    raise Exception, "UNIMPLEMENTED"

  def load_image_file(self,imagef):
    """
    To be overridden.
    Loads specified image file into image object and returns it.
    """
    raise Exception, "UNIMPLEMENTED"

  def create_image(self,width,height):
    """
    To be overridden.
    Create and return image with specified dimensions
    """
    raise Exception, "UNIMPLEMENTED"

  ### END OF TO BE OVERRIDDEN ###

  def prepare_image(self,width,height):
    """
    Create and internally store an image whose dimensions
    are those specified by width and height.
    """
    if self.image:
      raise Exception, "Image already prepared."
    self.image = self.create_image(width,height)

  def destroy_image(self):
    """
    Destroys internal representation of the image, if it was
    ever created.
    """
    if self.image:
      del self.image
    self.image = None

  def paste_image_file(self,imagef,xy):
    """
    Given the filename of an image, and the x,y coordinates of the 
    location at which to place the top left corner of the contents
    of that image, pastes the image into this object's internal image.
    """
    if not self.image:
      raise Exception, "Image not prepared"

    try:
      img = self.load_image_file(imagef)
    except Exception, e:
      raise Exception, "Could not load image "+str(imagef)+"\n"+str(e)

    self.paste_image(img,xy)
    del img

  def getImage(self):
    """
    Returns some representation of the internal image. The returned value 
    is not for use by the OSMManager.
    """
    return self.image
    


class PygameImageManager(ImageManager):
  """
  An ImageManager which works with Pygame images.
  """
  
  def __init__(self):
    ImageManager.__init__(self)
    try: import pygame
    except: raise Exception, "Pygame could not be imported!"
    self.pygame = pygame

  def create_image(self,width,height):
    return self.pygame.Surface( (width,height) )

  def load_image_file(self,imagef):
    return self.pygame.image.load(imagef);

  def paste_image(self,img,xy):
    self.getImage().blit( img,xy )



class PILImageManager(ImageManager):
  """
  An ImageManager which works with PIL images.
  """

  def __init__(self,mode):
    """
    Constructs a PIL Image Manager.
    Arguments:
      mode - the PIL mode in which to create the image.
    """
    ImageManager.__init__(self);
    self.mode = mode
    try: import PIL.Image
    except: raise Exception, "PIL could not be imported!"
    self.PILImage = PIL.Image

  def create_image(self,width,height):
    return self.PILImage.new(self.mode,(width,height))

  def load_image_file(self,imagef):
    return self.PILImage.open(imagef);    
  
  def paste_image(self,img,xy):
    self.getImage().paste( img,xy )



class OSMManager(object):
  """
  An OSMManager manages the retrieval and storage of Open Street Map
  images. The basic utility is the createOSMImage() method which
  automatically gets all the images needed, and tiles them together 
  into one big image.
  """
  def __init__(self, **kwargs):
    """
    Creates an OSMManager.
    Arguments:

    cache - path (relative or absolute) to directory where tiles downloaded
            from OSM server should be saved. Default "/tmp".
           
    server - URL of OSM server from which to retrieve OSM tiles. This
             should be fully qualified, including the protocol.
             Default "http://tile.openstreetmap.org"

    image_manager - ImageManager instance which will be used to do all
                    image manipulation. You must provide this.
    """
    cache = kwargs.get('cache')
    server = kwargs.get('server')
    mgr = kwargs.get('image_manager')
    
    if cache: self.cache = cache
    else:     self.cache = "/tmp"
      
    if server: self.server = server
    else:      self.server = "http://tile.openstreetmap.org"

    self.manager = mgr


  def getTileCoord(self, lon_deg, lat_deg, zoom):
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

  def getTileURL(self, tile_coord, zoom):
    """
    Given x,y coord of the tile to download, and the zoom level,
    returns the URL from which to download the image.
    """
    params = (zoom,tile_coord[0],tile_coord[1])
    return self.server+"/%d/%d/%d.png" % params

  def getLocalTileFilename(self, tile_coord, zoom):
    """
    Given x,y coord of the tile, and the zoom level,
    returns the filename to which the file would be saved
    if it was downloaded. That way we don't have to kill
    the osm server every time the thing runs.
    """
    params = (zoom,tile_coord[0],tile_coord[1]);
    return self.cache + "/%d_%d_%d.png" % params

  def retrieveTileImage(self,tile_coord,zoom):
    """
    Given x,y coord of the tile, and the zoom level,
    retrieves the file to disk if necessary and 
    returns the local filename.
    """
    filename = self.getLocalTileFilename(tile_coord,zoom)
    if not path.isfile(filename):
      url = self.getTileURL(tile_coord,zoom)
      try:
        urllib.urlretrieve(url, filename=filename);
      except Exception,e:
        raise Exception, "Unable to retrieve URL: "+url+"\n"+str(e)
    return filename

  def tileNWLatlon(self,tile_coord,zoom):
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


  def createOSMImage(self, (minlat, maxlat, minlon, maxlon), zoom):
    """
    Given bounding latlons (in degrees), and an OSM zoom level,
    creates an image constructed from OSM tiles.
    Returns (img,bounds) where img is the constructed image (as returned
    by the image manager's "getImage()" method),
    and bounds is the (latmin,latmax,lonmin,lonmax) bounding box
    which the tiles cover.
    """
    if not self.manager:
      raise Exception, "No ImageManager was specified, cannot create image."

    topleft = minX, minY = self.getTileCoord(minlon, maxlat, zoom);
    bottomright = maxX, maxY = self.getTileCoord(maxlon, minlat, zoom);
    new_maxlat, new_minlon = self.tileNWLatlon( topleft, zoom )
    new_minlat, new_maxlon = self.tileNWLatlon( (maxX+1,maxY+1), zoom )
    # tiles are 256x256
    pix_width = (maxX-minX+1)*256
    pix_height = (maxY-minY+1)*256
    self.manager.prepare_image( pix_width, pix_height )
    print "Retrieving %d tiles..." % ( (1+maxX-minX)*(1+maxY-minY) ,)

    for x in range(minX,maxX+1):
      for y in range(minY,maxY+1):
        fname = self.retrieveTileImage((x,y),zoom)
        x_off = 256*(x-minX)
        y_off = 256*(y-minY)
        self.manager.paste_image_file( fname, (x_off,y_off) )
    print "... done."
    return (self.manager.getImage(), 
            (new_minlat, new_maxlat, new_minlon, new_maxlon))



class _useragenthack(urllib.FancyURLopener):
  def __init__(self,*args):
    urllib.FancyURLopener.__init__(self,*args)
    for i,(header,val) in enumerate(self.addheaders):
      if header == "User-Agent":
        del self.addheaders[i]
        break
    self.addheader('User-Agent',
                   'OSMTools/1.0 +http://cbick.github.com/osmtools')

#import httplib
#httplib.HTTPConnection.debuglevel = 1
urllib._urlopener = _useragenthack()
