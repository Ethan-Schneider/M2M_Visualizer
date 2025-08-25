import argparse
from src.graph import *
from src.visualizer import *
import json

def main():
    parser = argparse.ArgumentParser(description='Process map and sequence files.')
    parser.add_argument('map_file', type=str, help='The name of the map file')
    parser.add_argument('sequence_file', type=str, help='The name of the sequence file')
    parser.add_argument('video_file', type=str, help='The name of the video output file')
    
    args = parser.parse_args()
    
    map_file = args.map_file
    sequence_file = args.sequence_file
    video_file = args.video_file

    map_array = load_map(map_file)
    map_array = map_array[::-1]

    obstacles = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == '@']
    agent_start_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'r']
    charging_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'c']
    delivery_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'd']
    paths = [[loc] for loc in agent_start_locs]

    print(paths)

    new_paths = load_paths(sequence_file)
    for i, path in enumerate(new_paths):
        paths[i] = paths[i] + path

    print(paths)

    visualize(map_array.shape, obstacles, paths, charging_locs, delivery_locs, video_file)

def symbotic_main():
    parser = argparse.ArgumentParser(description='Process map and sequence files.')
    parser.add_argument('map_file', type=str, help='The name of the map file')
    parser.add_argument('data_file', type=str, help='The name of the JSON data file from the data folder')
    parser.add_argument('video_file', type=str, help='The name of the video output file')
    parser.add_argument('start_timestep', type=int, help='The starting timestep')
    parser.add_argument('final_timestep', type=int, help='The final timestep')
    
    args = parser.parse_args()
    
    map_file = args.map_file
    data_file = args.data_file
    video_file = args.video_file
    start_timestep = args.start_timestep
    final_timestep = args.final_timestep

    # Read JSON data from data folder
    with open(f"data/{data_file}", 'r') as f:
        data = json.load(f)

    map_array = load_map(map_file)
    map_array = map_array[::-1]

    print(map_array)
    print(len(map_array))
    print(len(map_array[0]))

    obstacles = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == '@']
    charging_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'c']
    delivery_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'd']

    # Extract paths from the JSON data
    all_paths = data['paths']
    
    # Extract agent statuses from the JSON data
    agent_statuses = data.get('agent_statuses_per_timestep', [])
    
    # Extract agent goal locations from the JSON data
    agent_goal_locations = data.get('agent_goal_locations_per_timestep', [])
    
    # Extract the specified timestep range for each agent
    paths = []
    for agent_path in all_paths:
        # Extract timesteps from start_timestep to final_timestep (inclusive)
        # Convert from [x, y] format to (x, y) tuple format
        agent_timestep_path = []
        for timestep in range(start_timestep+1, final_timestep+2):
            if timestep < len(agent_path):
                # Convert coordinates: flip x coordinate to match map orientation
                x = len(map_array) - agent_path[timestep][0] - 1
                y = agent_path[timestep][1]
                agent_timestep_path.append((x, y))
        paths.append(agent_timestep_path)

    # Extract the specified timestep range for agent statuses
    agent_statuses_range = []
    for timestep in range(start_timestep, final_timestep + 1):
        if timestep < len(agent_statuses):
            agent_statuses_range.append(agent_statuses[timestep])
        else:
            # If timestep doesn't exist, create a default status list
            agent_statuses_range.append([0] * len(paths))

    # Extract the specified timestep range for agent goal locations
    agent_goal_locations_range = []
    for timestep in range(start_timestep, final_timestep + 1):
        if timestep < len(agent_goal_locations):
            # Convert goal locations to map coordinates
            timestep_goals = []
            for agent_id, goal_location in enumerate(agent_goal_locations[timestep]):
                if goal_location is not None:  # Agent has a goal
                    # Convert coordinates: flip x coordinate to match map orientation
                    x = len(map_array) - goal_location[0] - 1
                    y = goal_location[1]
                    timestep_goals.append((agent_id, (x, y)))
                else:
                    timestep_goals.append((agent_id, None))  # No goal for this agent
            agent_goal_locations_range.append(timestep_goals)
        else:
            # If timestep doesn't exist, create empty goal list
            agent_goal_locations_range.append([])

    print(f"Extracted paths for timesteps {start_timestep} to {final_timestep}")
    print(f"Number of agents: {len(paths)}")
    for i, path in enumerate(paths):
        print(f"Agent {i}: {len(path)} timesteps")
    
    # Use a default agent_id of 0 for visualization (can be modified if needed)
    agent_id = 0
    
    # For charging and delivery locations, we'll use the map-based ones for now
    # These could be extracted from the JSON data if available
    visualize(map_array.shape, obstacles, paths, charging_locs, delivery_locs, agent_id, video_file, agent_statuses=agent_statuses_range, agent_goal_locations=agent_goal_locations_range)

if __name__ == '__main__':
    symbotic_main()