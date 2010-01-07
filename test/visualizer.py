from osmtools.animation import SimViz, TrackingViz, Simulation
import pygame

class BusStopViz(SimViz):
  """Draws a small square at a bus stop location"""
  def __init__(self,location,label,color,width=5,
               drawing_order=0):
    SimViz.__init__(self,drawing_order)
    self.label = label;
    self.loc = location;
    self.color = color;
    self.width = width

  def setState(self,simtime,getXY):
    self.x,self.y = getXY(self.loc[0],self.loc[1]);
    
  def drawToSurface(self,surf):
    width=self.width
    surf.fill(self.color,pygame.Rect(self.x-width/2,self.y-width/2,
                                     width,width));

class BusArrivalViz(SimViz):
  """Draws a circle around a bus when it arrives at a stop"""
  def __init__(self,matchup,color,width=3,diameter=20,duration=10,
               drawing_order=10):
    """matchup should be a GPSBusSchedule object"""
    SimViz.__init__(self,drawing_order)
    self.matchup = matchup
    self.color = color
    self.width = width
    self.duration = duration
    self.diam = diameter
    self.xys = []

  def setState(self,simtime,getXY):
    self.xys = []
    arrived=False
    bt = self.matchup.bustrack
    for s in self.matchup.arrival_schedule:
      arrivetime=s['actual_arrival_time_seconds']
      if arrivetime is None: continue;
      if abs(arrivetime-simtime) <= self.duration:
        arrived=True
        ll = bt.getLocationAtTime(simtime);
        if ll is None:
          if (arrivetime < bt.min_time or arrivetime > bt.max_time):
            print "WARNING: Bus arrived when it doesn't exist"
        else:
          self.xys.append(getXY(*ll))
      elif arrived: #we stopped arriving places
        break    

  def drawToSurface(self,surf):
    for xy in self.xys:
      pygame.draw.circle(surf,self.color,xy,self.diam/2,self.width)


class BusMatchupViz(SimViz):
  """Draws a line between two bustracks whenever they both exist"""
  def __init__(self,bt1,bt2,color,width=3,
               drawing_order = 5):
    SimViz.__init__(self,drawing_order)
    self.bt1 = bt1;
    self.bt2 = bt2;
    self.color = color;
    self.width=width

  def setState(self,simtime,getXY):
    self.xy1 = self.xy2 = None
    t1,t2 = self.bt1,self.bt2
    ll1=t1.getLocationAtTime(simtime)
    if ll1 is None: return
    ll2 = t2.getLocationAtTime(simtime)
    if ll2 is None: return
    self.xy1=getXY(*ll1)
    self.xy2=getXY(*ll2)

  def drawToSurface(self,surf):
    if self.xy1 and self.xy2:
      pygame.draw.line(surf,self.color,self.xy1,self.xy2,self.width);



  
class BusTrackViz(TrackingViz):
  """
  A transparent wrapper around a BusTrack object. Easy way to specify 
  a label and an image to display.
  """
  def __init__(self,bustrack,label,image,
               drawing_order=10):
    """
    Given bustrack a BusTrack object, label a string, and image a
    filename, creates a BusTrackViz wrapper around bustrack with
    the given label and image for visualization.
    """
    self.track = bustrack;
    time_window = bustrack.getRouteTimeInterval()
    bounding_box = bustrack.getBoundingBox()

    TrackingViz.__init__(self,label,image,
                         bustrack.getLocationAtTime,
                         time_window,bounding_box,
                         drawing_order)


  def __eq__(self,other):
    return (self.track == other.track);

  def __hash__(self):
    return hash(self.track)

  def __getattr__(self,attr):
    """This does the wrapping around the bustrack"""
    return self.track.__getattribute__(attr);

  
  




def test_GTFS(tids=range(2912979-9,2912979+1)):
  import GTFSBusTrack as tracker
  import sys
  btvs=[]
  print "Loading GTFS data for %d routes..." % (len(tids),)
  ix=0
  for tid in tids:
    ix+=1
    bt = tracker.GTFSBusTrack(tid);
    btv = BusTrackViz(bt,'test',"images/bus_small.png");
    if bt.__dict__.get('interpolation') is not None:
      btvs.append(btv);
      print "+",ix
    else:
      print "-",ix
    sys.stdout.flush()
  print "...done. Begining simulation..."
  sim = Simulation(btvs);
  sim.run(speed=0,refresh_rate=0.02);


def test_GPS(route_short_name,rte=None,num=None):
  import GPSBusTrack as gps
  import GTFSBusTrack as gtfs
  if rte is None:
    rte = gps.Route(route_short_name);
  segs = [s for s in rte.segments(True)];
  btsegs=[]

  for i,seg in enumerate(segs):
    if num and i>=num: break
    bt = gps.GPSBusTrack(seg);
    btv = BusTrackViz(bt,'test',"images/bus_small.png");
    gtfs_trip_id,offset,error=bt.getMatchingGTFSTripID()
    bt2 = gtfs.GTFSBusTrack(gtfs_trip_id);
    print "BEST MATCHING TRIP ID: %s (error: %d)"%(bt2.trip_id,error)
    btv2 = BusTrackViz(bt2,'test',"images/bus.png");
    btsegs.extend([btv,btv2]);
  sim = Simulation(btsegs)
  sim.run(speed=0,refresh_rate=0.1);


def test_matched_GPS(segment_ids):
  import GPSBusTrack as gps
  gtfs_tracks = {}
  gps_tracks = []
  vizs = []
  stops = set()
  for i,segid in enumerate(segment_ids):
    print "Loading segment %s (%d/%d)..." %(segid,i+1,len(segment_ids))
    bus = gps.GPSBusSchedule(segid);
    gps_track = bus.getGPSBusTrack();
    gtfs_schedule = bus.getGTFSSchedule();
    service_id = gtfs_schedule.service_id;

    viz1 = BusTrackViz(gps_track,'tracked:'+str(segid),
                       "images/bus_small.png");
    
    gps_tracks.append(viz1);

    gtfs_key = (gtfs_schedule.trip_id,gtfs_schedule.offset)
    if not gtfs_tracks.has_key( gtfs_key ):
      gtfs_track = bus.getGTFSBusTrack();
      viz2 = BusTrackViz(gtfs_track,'scheduled:'+str(gtfs_track.trip_id),
                         "images/bus.png");
      gtfs_tracks[gtfs_key] = viz2
    else:
      viz2 = gtfs_tracks[gtfs_key]

    mviz = BusMatchupViz(viz1,viz2,service_colors[service_id]);
    arriv_viz = BusArrivalViz(bus,service_colors[service_id],duration=5);
    for stop in bus.getGPSSchedule():
      stops.add( (stop['stop_lat'],stop['stop_lon']) )
    vizs.append(mviz);
    vizs.append(arriv_viz);

    print "ok"

  print "Loading stops..."
  for stop in stops:
    vizs.append(BusStopViz(stop,'asdf',pygame.Color(0,0,0),5))
  print "ok"
  sim = Simulation(gtfs_tracks.values()+gps_tracks,vizs);
  sim.run(speed=0,refresh_rate=0.1,windowsize=(600,600));

service_colors = {
  '1':pygame.Color(255,80,80),
  '2':pygame.Color(80,255,80),
  '3':pygame.Color(80,80,255)
}

if __name__ == "__main__":
  import dbutils as db
  #test_tids = db.get_all_trip_ids_for_times('1','20000','21000');
  #test_tids = db.get_all_trip_ids_for_times('1','24000','30000');
  #test_GTFS(test_tids)
  #test_GPS('18',num=None);
  cur = db.get_cursor();
  cur.execute("""select gps_segment_id from gps_segments tr 
                   inner join gtf_trips gt on gt.trip_id=tr.trip_id 
                   inner join gtf_routes gr on gt.route_id = gr.route_id
                   inner join gtf_trip_information gti on gti.trip_id=gt.trip_id
                 where gr.route_short_name in ('5') and
                   27000 <= first_arrival and first_arrival <= 29000
              """
              );
  segids = [r['gps_segment_id'] for r in cur];
  cur.close();
  test_matched_GPS(segids);
  #test_matched_GPS(map(lambda i:str(i+1), range(500)))
  #test_matched_GPS(("35",))
  #test_matched_GPS(("1","2"))


