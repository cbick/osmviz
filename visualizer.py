import pygame
import math
import time





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
  sim.run(speed=0,refresh_rate=0.1);

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
                 where gr.route_short_name in ('19','10') --and
                   --27000 <= first_arrival and first_arrival <= 29000
              """
              );
  segids = [r['gps_segment_id'] for r in cur];
  cur.close();
  test_matched_GPS(segids);
  #test_matched_GPS(map(lambda i:str(i+1), range(500)))
  #test_matched_GPS(("35",))
  #test_matched_GPS(("1","2"))


