

class SimViz(object):
  """
  A class which knows how and when to display itself on a surface
  inside of a Simulation.
  """
  
  def drawToSurface(self,simtime,surf,getXY):
    """
    Draws this viz on the supplied surface.
    This should be implemented by subclasses.
    """
    raise Exception, "UNIMPLEMENTED"



class BusStopViz(SimViz):
  """Draws a small square at a bus stop location"""
  def __init__(self,location,label,color,width=5):
    self.label = label;
    self.loc = location;
    self.color = color;
    self.width = width

  def drawToSurface(self,simtime,surf,getXY):
    x,y = getXY(self.loc[0],self.loc[1]);
    width=self.width
    surf.fill(self.color,pygame.Rect(x-width/2,y-width/2,width,width));

class BusArrivalViz(SimViz):
  """Draws a circle around a bus when it arrives at a stop"""
  def __init__(self,matchup,color,width=3,diameter=20,duration=10):
    """matchup should be a GPSBusSchedule object"""
    self.matchup = matchup
    self.color = color
    self.width = width
    self.duration = duration
    self.diam = diameter

  def drawToSurface(self,simtime,surf,getXY):
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
          pygame.draw.circle(surf,self.color,getXY(*ll),
                             self.diam/2,self.width);
      elif arrived: #we stopped arriving places
        break

class BusMatchupViz(SimViz):
  """Draws a line between two bustracks whenever they both exist"""
  def __init__(self,bt1,bt2,color,width=3):
    self.bt1 = bt1;
    self.bt2 = bt2;
    self.color = color;
    self.width=width

  def drawToSurface(self,simtime,surf,getXY):
    t1,t2,c = self.bt1,self.bt2,self.color
    ll1=t1.getLocationAtTime(simtime)
    if ll1 is None: return
    ll2 = t2.getLocationAtTime(simtime)
    if ll2 is None: return
    x1,y1=getXY(*ll1)
    x2,y2=getXY(*ll2)
    pygame.draw.line(surf,c,(x1,y1),(x2,y2),self.width);


class BusTrackViz(object):
  """
  A transparent wrapper around a BusTrack object. Easy way to specify 
  a label and an image to display.
  """
  def __init__(self,bustrack,label,image):
    """
    Given bustrack a BusTrack object, label a string, and image a
    filename, creates a BusTrackViz wrapper around bustrack with
    the given label and image for visualization.
    """
    self.track = bustrack;
    self.label = label;
    self.image = pygame.image.load(image);

  def __eq__(self,other):
    return (self.track == other.track);

  def __hash__(self):
    return hash(self.track)

  def __getattr__(self,attr):
    """This does the wrapping around the bustrack"""
    return self.track.__getattribute__(attr);


## !FIXME! for past-midnight error
class Simulation(object):
  """
  A collection of BusTrackViz's and a timer, of sorts. This lets the 
  visualizer say "Give me coordinates of each bus at time T". A run()
  method is provided which displays the simulation in a pygame window.
  """
  
  def __init__(self, bustrackvizs, simvizs, initTime = 0):
    """
    Given a set of BusTrackViz objects and a list of generiv SimViz objects, 
    and optionally an initial time, creates a Simulation object.
    """
    self.tracks = bustrackvizs;
    self.other_vizs = simvizs;
    self.__findBoundingBox();
    self.__findTimeWindow();
    #self.__sortTracks();

    self.time = 10000
    self.setTime(initTime);

  def __findBoundingBox(self):
    """Finds the latlon box bounding all objects"""
    init_box = (1e6,-1e6,1e6,-1e6);
    def helper(left,right):
      right = right.getBoundingBox();
      return (min(left[0],right[0]),
              max(left[1],right[1]),
              min(left[2],right[2]),
              max(left[3],right[3]));
    self.bounding_box = reduce( helper, self.tracks, init_box );

  def __findTimeWindow(self):
    """Finds the min and max times over all routes"""
    init_window = (1e6,-1e6);
    def helper(left,right):
      right = right.getRouteTimeInterval();
      return (min(left[0],right[0]),
              max(left[1],right[1]));
    self.time_window = reduce( helper, self.tracks, init_window );


  def __sortTracks(self):
    """Sorts tracked objects in order of increasing start time"""
    def tcmp(t1,t2):
      return cmp(t1.getRouteTimeInterval()[0],
                 t2.getRouteTimeInterval()[0]);
    self.tracks.sort(cmp=tcmp);

  def setTime(self,time):
    """
    Moves all bus tracks to the given time.
    """
    if time < self.time:
      for t in self.tracks: t.getLocationAtTime(time);
    self.time = min( max(time, self.time_window[0] ), self.time_window[1] );
    # Sets all the tracks to the correct location

  def printTime(self):
    hours = int(self.time/3600)
    minutes = int( (self.time % 3600) / 60 )
    seconds = int( (self.time % 60) )
    print "%02d:%02d:%02d" % (hours,minutes,seconds)

  def getXY(self,lat,lon,bounds,ssize):
    """
    Given coordinates in lon,lat, and a screen size,
    returns the corresponding (x,y) pixel coordinates.
    """
    x_ratio = ( (lon - bounds[0]) /
                (bounds[1]-bounds[0]) )
    y_ratio = 1.0 - ( (lat - bounds[2]) / 
                      (bounds[3]-bounds[2]) )
    x,y = int(x_ratio*ssize[0]), int(y_ratio*ssize[1])
    return x,y

  def run(self, speed=0.0, windowsize=(1280,800), refresh_rate = 1.0):
    """
    Pops up a window and displays the simulation on it.
    Speed is advancement of sim in seconds/second.
    Refresh rate is pause in seconds between frames.
    Windowsize is the desired (width,height) of the display window.
    """
    pygame.init()
    green = pygame.Color(80,255,80);
    black = pygame.Color(0,0,0);
    notec = pygame.Color(200,200,80);
    fnt = pygame.font.Font("/Library/Frameworks/Python.framework/Versions/2.5/lib/python2.5/site-packages/pygame/freesansbold.ttf",10);
    

    osm = OSMManager();
    bg_big, new_bounds = osm.createOSMImage(*self.bounding_box);
    w_h_ratio = float(bg_big.get_width()) / bg_big.get_height();
    # Make the window smaller to keep proportions
    newwidth = int(windowsize[1]*w_h_ratio)
    newheight= int(windowsize[0]/w_h_ratio)
    if newwidth > windowsize[0]:
      windowsize = windowsize[0],newheight
    elif newheight > windowsize[1]:
      windowsize = newwidth, windowsize[1]

    screen = pygame.display.set_mode(windowsize);

    bg_small = pygame.transform.smoothscale(bg_big,windowsize);
    del bg_big;

    lastTime = self.time;
    getXY = lambda lat,lon: self.getXY(lat,lon,new_bounds,windowsize);

    exit = False
    while not exit:
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          exit = True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
          speed = max( (speed + 1) * 1.4 , (speed / 1.4) + 1 )
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
          speed = min( (speed / 1.4) - 1 , (speed - 1) * 1.4 )
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
          speed = 0.0
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
          self.time = self.time_window[0];
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
          self.time = self.time_window[1];
      mousex,mousey = pygame.mouse.get_pos();
      selected=None;
          
      if self.time != lastTime:
        self.printTime();

      lastTime = self.time;


      ## Draw the background
      screen.blit(bg_small, (0,0));


      ## Draw the tracked objects

      # track viz's
      for t in self.tracks:
        ll = t.getLocationAtTime(self.time);
        if ll is None:
          continue
        lat,lon = ll
        x,y = getXY(lat,lon)
        img = t.image;
        w,h=img.get_rect().width,img.get_rect().height
        if abs(x-mousex)<w/2 and abs(y-mousey)<h/2:
          selected=t
        x = x - w/2
        y = y - h/2

        screen.blit(img, (x,y))
       
      # generic viz's
      for sviz in self.other_vizs:
        sviz.drawToSurface(self.time,screen,getXY);        
      

      if selected:
        #pygame.draw.rect(screen,notec,pygame.Rect(mousex,mousey,200,80));
        text = fnt.render(selected.label, True,black,notec)
        screen.blit(text, (mousex,mousey-10))
        del text
        
      pygame.display.flip()

      time.sleep(refresh_rate);
      self.setTime(self.time + speed*refresh_rate);
      
    del bg_small
    pygame.display.quit()
