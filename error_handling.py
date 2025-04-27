import kociemba


def prompt_user_string():
    errors = (input("Please insert cube string: \n"))
    if len(errors) != 54:
        print("Please enter a valid cube string")
        return prompt_user_string()
    return errors

def prompt_user_errors():
    errors = int(input("How many errors were found ? \n"))
    return errors

def prompt_user_cube():
    side_number = int(input("On which side ? \n"))
    if side_number < 1 or side_number > 6:
        print("Please enter a valid side number (1-6)")
        return prompt_user_cube()
    square_number = int(input("which square \n"))   
    if square_number < 1 or square_number > 9:
        print("Please enter a valid square number (1-9)")
        return prompt_user_cube()
    
    return side_number, square_number

def prompt_user_color():
    color_change = (input("Which color should it be ? \n"))
    if color_change == "red":
        color_change = "R"
    elif color_change == "green":
        color_change = "F"
    elif color_change == "blue":
        color_change = "B"
    elif color_change == "yellow":
        color_change = "D"
    elif color_change == "white":
        color_change = "U"
    elif color_change == "orange":
        color_change = "L"
    else:
        print("Please enter a valid color")
        return prompt_user_color()
    return color_change

def string_correction (string_output, number_of_side, number_of_square,change):
    char_to_change = (number_of_side - 1) *9 + number_of_square -1
    string_output[char_to_change] = change
    return string_output

def solving_cube(layout):
    try:
        solution = kociemba.solve(layout)
        print("Solution:", solution)
    except Exception as e:
        print("Error:", e)

def main ():
    # Prompt the user for the cube string (assuming a solved cube for simplicity)
    string_output = prompt_user_string()
    string_output = list(string_output)  # Convert string to list for mutability
    
    # Prompt the user for the number of errors
    errors = prompt_user_errors()
    
    
    # Loop through the number of errors and prompt the user for each one
    for i in range(errors):
        print(f"\nError number {i+1}")
        side_number, square_number = prompt_user_cube()
        color_change = prompt_user_color()
        
        # Correct the string based on user input
        string_output = string_correction(string_output, side_number, square_number, color_change)
    
    # Convert the list back to a string and print it
    corrected_string = ''.join(string_output)
    print("Corrected cube string:", corrected_string)

    solving_cube(corrected_string)
    return corrected_string

if __name__ == "__main__":
    main()