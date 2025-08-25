from matplotlib.patches import Circle, Rectangle
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation


Colors = ['orange', 'blue', 'green']


class Animation:
  def __init__(self, map_size, obstacles, schedule, charging_loc, delivery_loc, agent_id, agent_statuses=None, agent_goal_locations=None):
    self.schedule = schedule
    self.combined_schedule = schedule
    self.agent_statuses = agent_statuses
    self.agent_goal_locations = agent_goal_locations
    
    self.fig = plt.figure(frameon=False, figsize=(16, 9), dpi=1920/16)
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
    # create boundary patch
    xmin = -0.5
    ymin = -0.5
    xmax = map_size[1] + 1.5
    ymax = map_size[0] - 0.5

    print(f"xmin: {xmin}, xmax: {xmax}, ymin: {ymin}, ymax: {ymax}")

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    self.patches.append(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='none', edgecolor='red'))
    for o in obstacles:
      x, y = o[0], o[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='gray', edgecolor='gray'))

    for c in charging_loc:
      x, y = c[0], c[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='green', edgecolor='green'))

    for d in delivery_loc:
      x, y = d[0], d[1]
      self.patches.append(Rectangle((y - 0.5, x - 0.5), 1, 1, facecolor='pink', edgecolor='pink'))

    # create agents:
    self.T = 0
    # draw goals first
    # for d, i in zip(map["agents"], range(0, len(map["agents"]))):
    #   self.patches.append(Rectangle((d["goal"][0] - 0.25, d["goal"][1] - 0.25), 0.5, 0.5, facecolor=Colors[0], edgecolor='black', alpha=0.5))
    
    for i, agent in enumerate(schedule):
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
      goal = Rectangle((schedule[agent][0]['x'] - 0.25, schedule[agent][0]['y'] - 0.25), 0.5, 0.5, 
                      facecolor='green', edgecolor='green', alpha=0.6, visible=False)
      self.goals[name] = goal
      self.patches.append(goal)
      
      # Create goal text label for this agent (initially invisible)
      goal_text = self.ax.text(schedule[agent][0]['x'], schedule[agent][0]['y'], name.replace('agent', ''), 
                              color='white', fontweight='bold', visible=False)
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
    plt.rcParams['animation.ffmpeg_path'] ='./exe/ffmpeg.exe'
    FFwriter=animation.FFMpegWriter(fps=10, extra_args=['-vcodec', 'libx264'])
    self.anim.save(file_name, writer=FFwriter),
      # savefig_kwargs={"pad_inches": 0, "bbox_inches": "tight"})

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
    
    for agent_name, agent in self.combined_schedule.items():
      pos = self.getState(i / 10, agent)
      p = (pos[1], pos[0])
      self.agents[agent_name].center = p
      self.agent_names[agent_name].set_position(p)
      
      # Update package position and visibility
      if agent_name in self.packages:
        package = self.packages[agent_name]
        package.set_xy((p[0] - 0.2, p[1] + 0.4))  # Position slightly above and to the left
        
        # Check if agent is carrying a package (status == 2)
        if (self.agent_statuses and 
            current_time < len(self.agent_statuses) and 
            agent_name.replace('agent', '').isdigit()):
          agent_id = int(agent_name.replace('agent', ''))
          if (agent_id < len(self.agent_statuses[current_time]) and 
              self.agent_statuses[current_time][agent_id] == 2):
            package.set_visible(True)
          else:
            package.set_visible(False)
        else:
          package.set_visible(False)
        
        # Update goal position and visibility
        if agent_name in self.goals:
          goal = self.goals[agent_name]
          
          # Check if agent has a goal location
          if (self.agent_goal_locations and 
              current_time < len(self.agent_goal_locations) and 
              agent_name.replace('agent', '').isdigit()):
            agent_id = int(agent_name.replace('agent', ''))
            
            # Find this agent's goal in the current timestep
            agent_goal = None
            for goal_agent_id, goal_location in self.agent_goal_locations[current_time]:
              if goal_agent_id == agent_id:
                agent_goal = goal_location
                break
            
            if agent_goal is not None:
              # Agent has a goal, show green box at goal location
              goal.set_xy((agent_goal[1] - 0.25, agent_goal[0] - 0.25))  # Convert to (x, y) format
              goal.set_visible(True)
              # Position and show goal text
              goal_text = self.goal_texts[agent_name]
              goal_text.set_position((agent_goal[1], agent_goal[0]))  # Center of the goal box
              goal_text.set_visible(True)
            else:
              # Agent has no goal, hide the box
              goal.set_visible(False)
              self.goal_texts[agent_name].set_visible(False)
          else:
            goal.set_visible(False)
            self.goal_texts[agent_name].set_visible(False)

    # reset all colors
    for _,agent in self.agents.items():
      agent.set_facecolor(agent.original_face_color)

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


def visualize(map_dimensions : tuple, obstacles : list, schedule : list, charging_loc : list, delivery_loc : list, agent_id : int, video : str = None, speed : int = 1, agent_statuses : list = None, agent_goal_locations : list = None):
  combined_schedule = {}
   
  for robot_num, sequence in enumerate(schedule):
    robot_path = []
    for i, step in enumerate(sequence):
      robot_path.append({'t':i, 'x':step[0], 'y':step[1]})
    combined_schedule['agent'+str(robot_num)] = robot_path
  
  animation = Animation(map_dimensions, obstacles, combined_schedule, charging_loc, delivery_loc, agent_id, agent_statuses, agent_goal_locations)
  

  if video:
    animation.save(video, speed)
  else:
    animation.show()
