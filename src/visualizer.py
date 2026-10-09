from matplotlib.patches import Circle, Rectangle
import matplotlib.pyplot as plt
import numpy as np
import imageio_ffmpeg
from matplotlib import animation
import os


Colors = ['orange', 'blue', 'green']


class Animation:
  def __init__(self, map_size, start_timestep : int, final_timestep : int, 
               walls, obstacles, schedule, charging_loc, delivery_loc, agent_id, 
               agent_statuses=None, agent_goal_locations=None, 
               agent_sku_carrying : list = None, num_skus : int = 0, 
               sku_locations_per_timestep : list = None, all_paths : list = None,
               agent_goal_locations_per_timestep : list = None):
    
    self.schedule = schedule
    
    self.map = map_size
    
    self.all_paths = all_paths
    self.num_agents = len(self.all_paths)
    
    self.start_timestep = start_timestep
    
    self.combined_schedule = schedule
    self.agent_statuses = agent_statuses
    self.agent_goal_locations = agent_goal_locations
    self.agent_sku_carrying = agent_sku_carrying
    self.num_skus = num_skus
    self.sku_locations_per_timestep = sku_locations_per_timestep
    self.agent_goal_locations_per_timestep = agent_goal_locations_per_timestep
    
    self.fig = plt.figure(frameon=False, figsize=(14, 9), dpi=1920/16)
    self.ax = self.fig.add_subplot(111, aspect='equal')
    self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)
    # self.ax.set_frame_on(False)

    self.patches = []
    self.artists = []
    self.agents = dict()
    self.agent_names = dict()
    self.packages = dict()  # Store package rectangles for each agent
    self.goals = dict()  # Store goal rectangles for each agent
    self.goal_texts = dict()  # Store goal text labels for each agent
    self.sku_rects = dict()
    # create boundary patch
    xmin = -0.5
    ymin = -0.5
    xmax = map_size[1] - 0.5
    ymax = map_size[0] - 0.5

    print(f"xmin: {xmin}, xmax: {xmax}, ymin: {ymin}, ymax: {ymax}")

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
    for o in obstacles:
      x, y = o[0], o[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='gray', edgecolor='gray'))
      sku_block = Rectangle((y - 0.4, x - 0.4), 0.8, 0.8, alpha=0.6, facecolor='black', edgecolor='gray', visible=False)
      self.sku_rects[(x, y)] = sku_block
      self.patches.append(sku_block)

    for c in charging_loc:
      x, y = c[0], c[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='green', edgecolor='green'))

    for d in delivery_loc:
      x, y = d[0], d[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='pink', edgecolor='pink'))
      
    for b in walls: 
      x, y = b[0], b[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='black', edgecolor='black'))

    # create agents:
    self.T = 0
    # draw goals first
    # for d, i in zip(map["agents"], range(0, len(map["agents"]))):
    #   self.patches.append(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black', alpha=0.5))
    
    ag_vis = [3, 35, 19]
    
    for i, agent in enumerate(schedule):
      # if i not in ag_vis:
      #   continue
      name = agent
      if agent_id == i:
        self.agents[name] = Circle((schedule[agent][0]['x'], schedule[agent][0]['y']), 0.3, facecolor='black', edgecolor='black')
        self.agents[name].original_face_color = 'black'
      else:
        self.agents[name] = Circle((schedule[agent][0]['x'], schedule[agent][0]['y']), 0.3, facecolor='black', edgecolor='black')
        self.agents[name].original_face_color = 'black'
      self.patches.append(self.agents[name])
      self.T = max(self.T, schedule[name][-1]['t'])
      self.agent_names[name] = self.ax.text(schedule[agent][0]['x'], schedule[agent][0]['y'], name.replace('agent', ''), color='white')
      self.agent_names[name].set_horizontalalignment('center')
      self.agent_names[name].set_verticalalignment('center')
      self.artists.append(self.agent_names[name])
      
      # Create package rectangle for this agent (initially invisible)
      package = Rectangle((schedule[agent][0]['x'] - 0.2, schedule[agent][0]['y'] + 0.4), 0.4, 0.3, 
                         facecolor='brown', edgecolor='brown', alpha=0.8, visible=False)
      self.packages[name] = package
      self.patches.append(package)
      
      # Create goal rectangle for this agent (initially invisible)
      goal = Rectangle((schedule[agent][0]['x'] - 0.25, schedule[agent][0]['y'] - 0.25), 0.6, 0.6, 
                      facecolor='green', edgecolor='green', alpha=0.6, visible=False)
      self.goals[name] = goal
      self.patches.append(goal)
      
      # Create goal text label for this agent (initially invisible)
      goal_text = self.ax.text(schedule[agent][0]['x'], schedule[agent][0]['y'], name.replace('agent', ''), 
                              color='black', fontweight='bold', visible=False)
      goal_text.set_horizontalalignment('center')
      goal_text.set_verticalalignment('center')
      self.goal_texts[name] = goal_text
      self.artists.append(goal_text)

    self.anim = animation.FuncAnimation(self.fig, self.animate_func,
                               init_func=self.init_func,
                               frames=int(self.T+1) * 10,
                               interval=100,
                               blit=True)

  def save(self, file_name, speed):
    # A bare file name lands in the output folder, the same way input data is
    # read from the data folder; an explicit path is left alone.
    if not os.path.dirname(file_name):
      file_name = os.path.join('output', file_name)
    os.makedirs(os.path.dirname(file_name), exist_ok=True)

    # The imageio-ffmpeg package bundles an ffmpeg binary, so there is nothing
    # to install by hand (no ./exe/ffmpeg.exe, no system ffmpeg).
    plt.rcParams['animation.ffmpeg_path'] = imageio_ffmpeg.get_ffmpeg_exe()
    FFwriter = animation.FFMpegWriter(fps=10,
                                      extra_args=['-vcodec', 'libx264',
                                                  '-pix_fmt', 'yuv420p'])
    self.anim.save(file_name, writer=FFwriter)
    print(f"Saved video to {file_name}")

  def show(self):
    plt.show()

  def init_func(self):
    for p in self.patches:
      self.ax.add_patch(p)
    for a in self.artists:
      self.ax.add_artist(a)
    return self.patches + self.artists

  def animate_func(self, i):
    current_time = int(i / 10)  # Convert frame to timestep
    current_timestep = self.start_timestep + current_time
    
    print(f"current timestep {current_timestep} and current frame {i}")
    
    ag_vis = [3, 35, 19]
    
    for agent_id in range(self.num_agents):
      # if agent_id not in ag_vis:
      #   continue
      # Update agent state
      p = self.getState2(current_timestep, i, agent_id)
      key = 'agent' + str(agent_id)
      self.agents[key].center = p
      self.agent_names[key].set_position(p) 
      
      # Update agent package (placement, color, and if it is holding one or not)
      package = self.packages[key]
      package.set_xy((p[0]-0.2, p[1] + 0.4))
      sku = self.agent_sku_carrying[current_timestep][agent_id]
      if sku ==[] or sku is None:
        package.set_visible(False)
        package.set_facecolor('white')
        package.set_edgecolor('white')
      else:
        sku = sku[0]
        package.set_visible(True)
        color_val = sku/max(1, self.num_skus) if self.num_skus > 1 else 0
        cm = plt.get_cmap('Pastel2')
        package.set_facecolor(cm(color_val))
        package.set_edgecolor(cm(color_val))
      
      # Update goal location
      goal_loc = self.agent_goal_locations_per_timestep[current_timestep - 1][agent_id]
      
      if goal_loc is None:
        self.goal_texts[key].set_visible(False)
      else:
        self.goal_texts[key].set_visible(True)
        p = (goal_loc[1] + 1, self.map[0] - goal_loc[0] - 1)
        self.goal_texts[key].set_position(p)
            
    # Update SKU locations
    sku_locations = self.sku_locations_per_timestep[current_timestep - 1]
    
    # Set all sku locations to be invisible at first
    for sku_loc in self.sku_rects.values():
      sku_loc.set_visible(False)
    
    sku_vis = [0, 1, 2]
    
    # Iterate over locations 
    for sku_id, sku_locs in enumerate(sku_locations):
      # if sku_id not in sku_vis:
      #   continue
      # print(f"Sku id {sku_id} has {len(sku_locs)}: {sku_locs}")
      for loc in sku_locs:
        # x = loc[0]
        # y = loc[1] + 1
        # loc = (x, y)
        loc = ((self.map[0] - loc[0] - 1), loc[1] + 1)
        # try:
        #   print(f"====================HERE=======================")
        #   loc = ((self.map[0] - loc[0] - 1), loc[1] + 1)
        # except:
        #   continue
          
        
        if loc not in self.sku_rects.keys():
          continue
        self.sku_rects[loc].set_visible(True)
        color_val = sku_id/max(1, self.num_skus) if self.num_skus > 1 else 0
        cm = plt.get_cmap('Pastel2')
        self.sku_rects[loc].set_facecolor(cm(color_val))
        self.sku_rects[loc].set_edgecolor(cm(color_val))

    # check drive-drive collisions
    agents_array = [agent for _,agent in self.agents.items()]
    for i in range(0, len(agents_array)):
      for j in range(i+1, len(agents_array)):
        d1 = agents_array[i]
        d2 = agents_array[j]
        pos1 = np.array(d1.center)
        pos2 = np.array(d2.center)
        if np.linalg.norm(pos1 - pos2) < 0.7:
          d1.set_facecolor('red')
          d2.set_facecolor('red')
          print("COLLISION! (agent-agent) ({}, {})".format(i, j))

    return self.patches + self.artists


  def getState(self, t, d):
    idx = 0
    while idx < len(d) and d[idx]["t"] < t:
      idx += 1
    if idx == 0:
      return np.array([float(d[0]["x"]), float(d[0]["y"])])
    elif idx < len(d):
      posLast = np.array([float(d[idx-1]["x"]), float(d[idx-1]["y"])])
      posNext = np.array([float(d[idx]["x"]), float(d[idx]["y"])])
    else:
      return np.array([float(d[-1]["x"]), float(d[-1]["y"])])
    dt = d[idx]["t"] - d[idx-1]["t"]
    t = (t - d[idx-1]["t"]) / dt
    pos = (posNext - posLast) * t + posLast
    return pos
  
  
  def getState2(self, timestep : int, frame : int, agent_id : int):
    if frame % 10 == 0:
      loc = self.all_paths[agent_id][timestep]
      p = (loc[1], self.map[0] - loc[0] - 1)
      return p
    else:
      loc1 = self.all_paths[agent_id][timestep]
      loc2 = self.all_paths[agent_id][timestep + 1]
      frame = frame%10
      
      dt = frame/10
      dx = 0
      dy = 0
      
      x_dif = loc2[1] - loc1[1]
      y_dif = (self.map[0] - loc2[0] - 1) - (self.map[0] - loc1[0] - 1)

      
      if x_dif == 0:
        dx = 0
      elif x_dif < 0:
        dx = -1*dt
      else:
        dx = dt
      
      if y_dif == 0:
        dy = 0
      elif y_dif < 0:
        dy = -1*dt
      else:
        dy = dt
      
      p = (loc1[1] + dx, (self.map[0] - loc1[0] - 1) + dy)
      return p


def visualize(map_dimensions : tuple, all_paths : list, start_timestep : int, final_timestep : int, walls : list, obstacles : list, schedule : list, 
              charging_loc : list, delivery_loc : list, agent_id : int, video : str = None, num_skus : int = 0, speed : int = 1, 
              agent_statuses : list = None, agent_goal_locations : list = None, agent_sku_carrying : list = None, 
              sku_locations_per_timestep : list = None, agent_goal_locations_per_timestep : list = None):
  
  combined_schedule = {}
   
  for robot_num, sequence in enumerate(schedule):
    robot_path = []
    for i, step in enumerate(sequence):
      robot_path.append({'t':i, 'x':step[0], 'y':step[1]})
    combined_schedule['agent'+str(robot_num)] = robot_path
  
  animation = Animation(map_dimensions, start_timestep, final_timestep, walls, obstacles, 
                        combined_schedule, charging_loc, delivery_loc, agent_id, agent_statuses, 
                        agent_goal_locations, agent_sku_carrying, num_skus, sku_locations_per_timestep, all_paths,
                        agent_goal_locations_per_timestep=agent_goal_locations_per_timestep)
  

  if video:
    animation.save(video, speed)
  else:
    animation.show()
