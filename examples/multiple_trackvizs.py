"""
This example demonstrates the animation of multiple icons
on a map using TrackingViz objects.
"""

from osmviz.animation import TrackingViz, Simulation

## The goal is to show 10 trains racing eastward across the US.

right_lon = -(68+39.0/60)
left_lon = -(118+15.0/60)
top_lat = 45+46.0/60
bottom_lat = 30+3.0/60

begin_time = 0
end_time = 60

image_f = "images/train.png"
zoom=6
num_trains = 10

trackvizs = []

def makeInterpolator(begin_ll, end_ll, begin_t, end_t):
  def ret(t):
    if t<begin_t:
      return begin_ll
    elif t>end_t:
      return end_ll
    else:
      blat,blon = begin_ll
      elat,elon = end_ll
      frac = float(t)/(end_t-begin_t)
      return ( blat + frac*(elat-blat) , blon + frac*(elon-blon) )
  return ret

for i in range(num_trains):
  lat = bottom_lat + i * (top_lat-bottom_lat) / (num_trains-1)
  
  locAtTime = makeInterpolator( (lat, left_lon),
                                (lat, right_lon), 
                                begin_time, end_time )

  tviz = TrackingViz( "Train %d" %(i+1,), image_f, locAtTime, 
                   (begin_time,end_time),
                   (30,46,-119,-68.5),
                   1) #drawing order doesn't really matter here

  trackvizs.append(tviz)


sim = Simulation( trackvizs, [], 0 )
sim.run(speed=1,refresh_rate=0.1,osmzoom=zoom)
