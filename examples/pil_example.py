"""
This example demonstrates how to create and show a PIL image
of OSM tiles patched together.
"""

from osmviz.manager import PILImageManager, OSMManager
import PIL.Image as Image

imgr = PILImageManager('RGB')
osm = OSMManager(image_manager=imgr)
image,bnds = osm.createOSMImage( (30,35,-117,-112), 9 )
wh_ratio = float(image.size[0]) / image.size[1]
image2 = image.resize( (int(800*wh_ratio),800), Image.ANTIALIAS )
del image
image2.show()
