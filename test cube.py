import pycuber as pc
from pycuber.solver import CFOPSolver
import kociemba
import twophase.solver  as sv

# Define the color map based on your definition
color_map = {
    'U': '[w]',  # Yellow (Up)
    'F': '[g]',  # Green (Front)
    'R': '[r]',  # Orange (Right)
    'D': '[y]',  # White (Down)
    'B': '[b]',  # Blue (Back)
    'L': '[o]',  # Red (Left)
}

# Testing purpose
reverse_color_map = {
    'y': 'D',  # Yellow (Up)
    'g': 'F',  # Green (Front)
    'o': 'L',  # Orange (Right)
    'w': 'U',  # White (Down)
    'b': 'B',  # Blue (Back)
    'r': 'R',  # Red (Left)
}


def solving_cube(layout):
    
    try:
        solution = kociemba.solve(layout)
        print("Solution:", solution)
    except Exception as e:
        print("Error:", e)


def cube_stickers(layout_str):
    # Convert the string to a list of colors using the color map
    layout = [color_map[ch] for ch in layout_str]
    layout = ''.join(layout)
    cube_faces = {
    'U': layout[0:3*9],  # Up
    'R': layout[3*9:3*18],  # Right
    'F': layout[3*18:3*27],  # Front
    'L': layout[3*27:3*36],  # Left
    'B': layout[3*36:3*45],  # Back
    'D': layout[3*45:3*54]   # Down
}
    print("Converted layout:", cube_faces)
    return cube_faces

# Print the cube layout in a readable format
def cube_layout(layout_str):
    cube_str=cube_stickers(layout_str)
    print(cube_str['D'])

    str_output = '\n'
    side_size = 9
    num_layers = 3

    for j in range (0, num_layers):
        for i in range(0, side_size):
            str_output += ' '
        for i in range(0, side_size, 9):
            str_output += cube_str['U'][side_size*j:side_size*j+side_size] + '\n'


    for j in range (0, num_layers):
        for i in range(0, side_size, 9*4):
            str_output += cube_str['R'][side_size*j:side_size*j+side_size] + cube_str['F'][side_size*j:side_size*j+side_size] + cube_str['L'][side_size*j:side_size*j+side_size] + cube_str['B'][side_size*j:side_size*j+side_size] + '\n'

    for j in range (0, num_layers):
        for i in range(0, side_size):
            str_output += ' '
        for i in range(0, side_size, 9):
            str_output += cube_str['D'][side_size*j:side_size*j+side_size] + '\n'

    return str_output

# Testing purpose
def reverse_cube_layout(cube_faces):
    # Initialize the layout string
    layout = ''

    # The order of stickers in the cube layout
    layout += cube_faces[:]
    layout = layout.replace('[','').replace(']','').replace(' ','').replace('\n','')
    string2return = layout[0:9]# U
    print('string2return:', string2return)
    for j in range(0,3):
        # for i in range(0, 3):
            
        string2return += layout[j*12+9:j*12+9+3] # R
        print('string2return:', string2return)
    for j in range(3):
            string2return += layout[j*12+9+3:j*12+6+9] # F
    print('string2return:', string2return)
    # string2return += layout[45:54] # D
    for j in range(3):
        string2return += layout[j*12+9+6:j*12+9+9] # L
    for j in range(3):
        string2return += layout[j*12+9+9:j*12+12+9] # B
    string2return += layout[45:54] # D
    print('string2return:', string2return)

    string2return = [reverse_color_map[ch] for ch in string2return]
    string2return = ''.join(string2return)
   
    print("Reversed layout:", string2return)
    return string2return


def main():
    cube = pc.Cube()
    solver = CFOPSolver(cube)

    cube("z")
    cube("z")

    # print(cube)
    # cube("D2 R' D' F2 B D R2 D2 R' F2 D' F2 U' B2 L2 U2 D R2 U")
    cube("U R U2 F2 D2 F D' R2 L D F' R' D' B2 R2 D F2 U2 L2 D")
    # solution = solver.solve()
    # print("Solution:", solution)


    # print(cube)  # Print the cube in its current state
    string = cube.__str__()
    print(string)  # Print the cube as a string representation
    layout_str = reverse_cube_layout(string)

    # Example usage of the functions defined above
    # layout_str = "DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD"
    

    print("Facelet string:", layout_str)
    layout = cube_layout(layout_str)
    print("Scrambled Cube:")
    print(layout)

    # Print the scrambled cube
    try:
        solution = sv.solve("FDLUUURLFLBDFRRDLBBBUBFLDDLFBBUDUBRLURDFLRUFRFLRFBDUDR",19,2)
        print("Solution:", solution)
    except Exception as e:
        print("Error:", e)

    solving_cube(layout_str)

if __name__ == "__main__":
    main()