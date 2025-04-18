import sensor, image, time

# Position labels for 3x3 Rubik's cube face
position_names_9 = [
    "top_left", "top_middle", "top_right",
    "middle_left", "center", "middle_right",
    "bottom_left", "bottom_middle", "bottom_right"
]

# Updated LAB color thresholds (tweak with OpenMV IDE if needed)
color_lims = {
    'R': (20, 60, 40, 80, 20, 60),     # Red
    'O': (50, 80, 10, 40, 40, 80),     # Orange
    'G': (30, 80, -60, -20, 0, 60),    # Green
    'B': (20, 60, 0, 50, -80, -20),    # Blue
    'Y': (50, 90, -20, 20, 60, 90),    # Yellow
    'W': (60, 100, -10, 10, -10, 10),  # White
}

# Camera setup
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
clock = time.clock()

# Draw bounding boxes and color labels
def draw_overlay(img, squares):
    for sq in squares:
        img.draw_rectangle(sq['rect'], color=(255, 0, 0))
        img.draw_string(sq['cx'], sq['cy'], sq['color'], mono_space=False)

# Assign 9 squares to fixed grid positions
def assign_positions_9(squares):
    sorted_by_y = sorted(squares, key=lambda s: s['cy'])
    top = sorted(sorted_by_y[:3], key=lambda s: s['cx'])
    middle = sorted(sorted_by_y[3:6], key=lambda s: s['cx'])
    bottom = sorted(sorted_by_y[6:], key=lambda s: s['cx'])
    ordered = top + middle + bottom
    return {position_names_9[i]: ordered[i]['color'] for i in range(9)}

# Print grid to terminal with position and color
def print_face_3x3(pos_map):
    print("\n🧩 Rubik's Cube Face (Detected Colors):")
    print("┌────────┬────────┬────────┐")
    print("│ {:^6} │ {:^6} │ {:^6} │".format(pos_map["top_left"], pos_map["top_middle"], pos_map["top_right"]))
    print("├────────┼────────┼────────┤")
    print("│ {:^6} │ {:^6} │ {:^6} │".format(pos_map["middle_left"], pos_map["center"], pos_map["middle_right"]))
    print("├────────┼────────┼────────┤")
    print("│ {:^6} │ {:^6} │ {:^6} │".format(pos_map["bottom_left"], pos_map["bottom_middle"], pos_map["bottom_right"]))
    print("└────────┴────────┴────────┘")
    print("🔍 Per Position:")
    for k in position_names_9:
        print(f"{k:>13}: {pos_map[k]}")

while True:
    clock.tick()
    img = sensor.snapshot()
    detected_squares = []

    for color, thresh in color_lims.items():
        blobs = img.find_blobs([thresh], pixels_threshold=100, area_threshold=100, merge=True)
        for b in blobs:
            if abs(b.w() - b.h()) < 20:  # Square-like shape
                detected_squares.append({
                    'color': color,
                    'rect': b.rect(),
                    'cx': b.cx(),
                    'cy': b.cy()
                })

    # Draw bounding boxes in real-time
    draw_overlay(img, detected_squares)
    img.draw_string(5, 5, "Squares: {}".format(len(detected_squares)), color=(0, 255, 0))

    # Print face if exactly 9 squares are detected
    if len(detected_squares) == 9:
        pos_map = assign_positions_9(detected_squares)
        print_face_3x3(pos_map)
        time.sleep(4)  # Pause before next detection
