import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import argparse


def load_map(file_path):
    """Load map from file and return as numpy array."""
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


def create_map_image(map_file, output_file=None):
    """
    Create a static image of a map file with the specified color scheme.
    
    Args:
        map_file (str): Path to the map file
        output_file (str, optional): Path to save the output image. If None, displays the image.
    """
    # Load the map
    map_array = load_map(map_file)
    
    # Get map dimensions
    rows, cols = map_array.shape
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(cols * 0.5, rows * 0.5))
    ax.set_xlim(-0.5, cols + 0.5)
    ax.set_ylim(-0.5, rows + 0.5)
    ax.set_aspect('equal')
    
    # Remove axes for cleaner look
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_frame_on(False)
    
    # Create border around the entire map
    border = patches.Rectangle((-0.5, -0.5), cols + 1, rows + 1, 
                              linewidth=2, edgecolor='gray', facecolor='none')
    ax.add_patch(border)
    
    # Process each cell in the map
    for i in range(rows):
        for j in range(cols):
            cell_char = map_array[i, j].decode('utf-8')
            
            # Create rectangle for this cell
            rect = patches.Rectangle((j - 0.5, i - 0.5), 1, 1, 
                                   linewidth=1, edgecolor='black')
            
            # Set color based on character
            if cell_char in ['e', 's']:
                # Light blue for 'e' and 's'
                rect.set_facecolor('lightblue')
            elif cell_char == 'r':
                # Orange for 'r'
                rect.set_facecolor('orange')
            elif cell_char == '@':
                # Gray for obstacles
                rect.set_facecolor('black')
            elif cell_char == '.':
                # White for empty spaces
                rect.set_facecolor('white')
            elif cell_char == 'b':
                rect.set_facecolor('black')
            else:
                # Default to white for unknown characters
                rect.set_facecolor('white')
            
            ax.add_patch(rect)
    
    # Invert y-axis to match typical map orientation (0,0 at top-left)
    ax.invert_yaxis()
    
    # Set title
    # ax.set_title(f'Map Visualization: {map_file}', pad=20)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save or show the image
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Map image saved to: {output_file}")
    else:
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Generate a static image from a map file.')
    parser.add_argument('map_file', type=str, help='Path to the map file')
    parser.add_argument('--output', '-o', type=str, help='Output image file path (optional)')
    
    args = parser.parse_args()
    
    create_map_image(args.map_file, args.output)


if __name__ == '__main__':
    main()
