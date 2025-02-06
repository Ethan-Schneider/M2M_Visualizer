import numpy as np

def load_map(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Determine the shape of the map
    rows = len(lines)
    cols = len(lines[0].strip())
    
    # Initialize numpy array
    map_array = np.chararray((rows, cols))
    
    # Fill the numpy array with characters from the map file
    for i, line in enumerate(lines):
        for j, c in enumerate(line.strip()):
            map_array[i, j] = c
    
    return map_array


def load_paths(file_path):
    a = [[(7, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10), (8, 10)], 
         [(10, 7), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 10), (10, 9), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (9, 13), (9, 15), (9, 17), (7, 17), (5, 17), (3, 17), (2, 17)], 
         [(10, 12), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (10, 11), (9, 10), (9, 8), (9, 6), (9, 5), (9, 3), (10, 1), (10, 1), (10, 1), (10, 1), (10, 1), (10, 1), (10, 1), (10, 1), (10, 1), (10, 1)], 
         [(13, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (11, 10), (10, 10), (10, 12), (10, 13), (10, 15), (10, 17), (8, 18), (6, 18), (4, 18), (2, 18), (2, 18), (2, 18), (2, 18), (2, 18)]]
    np.save('./paths/scenario2', a)
    b = np.load('./paths/scenario2.npy')
    # print(b)

    paths = []
    for agent_path in b.tolist():
        path = []
        for loc in agent_path:
            path.append((loc[0], loc[1]))
        paths.append(path)
    return b.tolist()

