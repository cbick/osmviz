"""
This example demonstrates how to subclass the SimViz class
in order to create your own custom visualizations. This is
if you want to do something besides just show icons moving
on the map.
"""

from osmviz.animation import SimViz, TrackingViz, Simulation
import pygame

## Our goal is to show a train lassoed to denver, running around it.

red = pygame.Color("red")

class LassoViz(SimViz):
  """
  LassoViz draws a line between two (optionally moving) locations.
  """
  
  def __init__(self, getLocAtTime1, getLocAtTime2, 
               linecolor=red, linewidth=3,
               drawingOrder=0):
    """
    getLocAtTime 1 and 2 represent the location of the 1st and 2nd
    endpoint of this lasso, respectively. They should take a single 
    argument (time) and return the (lat,lon) of that endpoint.
    """
    SimViz.__init__(self, drawingOrder);
    self.xy1 = None
    self.xy2 = None
    self.linecolor = linecolor
    self.linewidth = linewidth
    self.getLoc1 = getLocAtTime1
    self.getLoc2 = getLocAtTime2
    
  def setState(self, simtime, getXY):
    self.xy1 = getXY(*self.getLoc1(simtime))
    self.xy2 = getXY(*self.getLoc2(simtime))
    
  def drawToSurface(self, surf):
    pygame.draw.line(surf, self.linecolor, self.xy1, self.xy2, 
                     self.linewidth)

  ## So long as we are passing LassoViz's in as part of the scene_viz
  ## list to a Simulation, we don't need to implement the getLabel,
  ## getBoundingBox, or mouseIntersect methods.


class TiedTrain(TrackingViz):  
  """
  TiedTrain shows a train tied to a certain location, running around
  it at a specified distance and frequency.
  This is partly meant to demonstrate that it's ok to override 
  the TrackingViz class, too (in fact it's usually easier).
  """
  
  def __init__(self, tiepost, lat_dist, lon_dist, frequency, time_window,
               label, drawing_order=0, image="images/train.png"):
    self.clat,self.clon = tiepost
    self.lat_dist = lat_dist
    self.lon_dist = lon_dist
    self.frequency = int(frequency)

    TrackingViz.__init__(self,label,image,self.getLocAtTime,time_window,
                         (self.clat-self.lat_dist, self.clat+self.lat_dist,
                          self.clon-self.lon_dist, self.clon+self.lon_dist),
                         drawing_order)


  def getLocAtTime(self,time):
    phase = float(time % self.frequency) / self.frequency
    if phase < 0.25:
      blat = self.clat - self.lat_dist
      elat = self.clat + self.lat_dist
      blon = elon = self.clon - self.lon_dist
      frac = phase/0.25
    elif phase < 0.5:
      blat = elat = self.clat + self.lat_dist
      blon = self.clon - self.lon_dist
      elon = self.clon + self.lon_dist
      frac = (phase-0.25)/0.25
    elif phase < 0.75:
      blat = self.clat + self.lat_dist
      elat = self.clat - self.lat_dist
      blon = elon = self.clon + self.lon_dist
      frac = (phase-0.5)/0.25
    else:
      blat = elat = self.clat - self.lat_dist
      blon = self.clon + self.lon_dist
      elon = self.clon - self.lon_dist
      frac = (phase-0.75)/0.25
    return blat + frac*(elat-blat), blon + frac*(elon-blon)



denver = 39.756111, -104.994167
train = TiedTrain(denver, 5.0, 5.0, 60, (0, 600), "Denver Bound")
lasso = LassoViz(train.getLocAtTime,
                 lambda t: denver)

sim = Simulation( [train,], [lasso,], 0)
sim.run(refresh_rate = 0.01, speed = 1, osmzoom = 7)
