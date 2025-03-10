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
    parser.add_argument('buffer_file', type=str, help='The name of the buffer file')
    parser.add_argument('video_file', type=str, help='The name of the video output file')
    
    args = parser.parse_args()
    
    map_file = args.map_file
    buffer_file = args.buffer_file
    video_file = args.video_file

    with open(buffer_file, 'r') as f:
        buffer_data = json.load(f)

    map_array = load_map(map_file)
    map_array = map_array[::-1]

    print(map_array)
    print(len(map_array))
    print(len(map_array[0]))

    obstacles = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == '@']
    # agent_start_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'r']
    charging_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'c']
    delivery_locs = [(i, j) for i, row in enumerate(map_array) for j, val in enumerate(row) if val.decode('utf-8') == 'd']

    states = buffer_data['states']
    agent_id = buffer_data['agent']
    charging_locs = buffer_data['task start location']
    charging_locs = [(len(map_array) - charging_locs[0] - 1, charging_locs[1])]
    delivery_locs = buffer_data['task goal location']
    delivery_locs = [(len(map_array) - delivery_locs[0] - 1, delivery_locs[1])]

    print(len(states))
    print(len(states[0]))

    states = np.asarray(states)

    paths = []
    for col in range(states.shape[1]):
        agent_path = []
        for row in range(states.shape[0]):
            x = len(map_array) - states[row, col][0] - 1
            y = states[row, col][1]
            agent_path.append((x, y))
        paths.append(agent_path)

    print(paths)
    print(f"path lengths: {len(paths)}")
    visualize(map_array.shape, obstacles, paths, charging_locs, delivery_locs, agent_id, video_file)

if __name__ == '__main__':
    symbotic_main()