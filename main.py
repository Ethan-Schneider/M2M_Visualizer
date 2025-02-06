import argparse
from src.graph import *
from src.visualizer import *

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

if __name__ == '__main__':
    main()