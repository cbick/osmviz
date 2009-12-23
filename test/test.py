from animation import SimViz, TrackingViz, Simulation
import pygame

Inf = float('inf')

def find_bounds(route):
    min_time=Inf
    max_time=-Inf
    min_lat=min_lon=Inf
    max_lat=max_lon=-Inf

    for lat,lon,time in route:
        min_time = min(min_time,time)
        max_time = max(max_time,time)
        min_lat = min(min_lat,lat)
        min_lon = min(min_lon,lon)
        max_lat = max(max_lat,lat)
        max_lon = max(max_lon,lon)

    return (min_time,max_time),(min_lat,max_lat,min_lon,max_lon)


def test_sim( route, zoom, image="images/train.png" ):
    time_window,bbox = find_bounds(route)
    
    def getLL(time):
        if time <= time_window[0]:
            return route[0][:2]
        elif time > time_window[1]:
            return route[-1][:2]

        for (lat1,lon1,time1),(lat2,lon2,time2) in zip(route[:-1],route[1:]):
            if time1 < time <= time2:
                break

        frac = (time-time1) / (time2-time1)
        lat = lat1 + frac * (lat2-lat1)
        lon = lon1 + frac * (lon2-lon1)
        return lat,lon

    viz = TrackingViz("Test Train",
                      image,
                      getLL,
                      time_window,
                      bbox,
                      1);
    sim = Simulation([viz],[],0)
    sim.run(speed=0,refresh_rate=0.1,osmzoom=zoom)

def test_one():
    begin_ll = 45+46.0/60 , -(68+39.0/60)
    end_ll = 30+3.0/60 , -(118+15.0/60)

    route = [ begin_ll+(0,),
              end_ll+(100,) ]
    test_sim(route,6)





if __name__ == '__main__':
    test_one()

    
