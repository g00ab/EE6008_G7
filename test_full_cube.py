import sensor, image, time, ml, math, uos, gc
from collections import OrderedDict
import re

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((240, 240))
sensor.skip_frames(time=2000)

# --- LAB Color Classification Function ---
def classify_color(stats):
    l = stats.l_mean()
    a = stats.a_mean()
    b = stats.b_mean()

    if l > 94 : # and abs(a) < 15 and abs(b) < 15:
        return "white"
    elif a > 38 and b > 30:
        return "red"
    elif 0 < a <= 38 and 30 < b <= 70:
        return "orange"
    elif -28 < a < 0 and b > 40:
        return "yellow"
    elif a < -33 and -10 < b < 35:
        return "green"
    elif a < 15 and b < -25:
        return "blue"
    else:
        return "?"

# --- Load square detection model (FOMO) ---
net_square = None
square_labels = None
try:
    net_square = ml.Model("fomo.tflite", load_to_fb=uos.stat('fomo.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    raise Exception('Failed to load "fomo.tflite": ' + str(e))

try:
    square_labels = [line.rstrip('\n') for line in open("fomo_labels.txt")]
except Exception as e:
    raise Exception('Failed to load "fomo_labels.txt": ' + str(e))

min_confidence = 0.5

colors = [
    (255, 0, 0), (0, 255, 0), (255, 255, 0),
    (0, 0, 255), (255, 0, 255), (0, 255, 255),
    (255, 255, 255),
]

position_names = [
    "top_left_corner", "middle_top", "top_right_corner",
    "middle_left", "center", "middle_right",
    "bottom_left_corner", "middle_bottom", "bottom_right_corner"
]

color_map = {
    'yellow': 'D',  # Yellow (Down)
    'green': 'F',  # Green (Front)
    'orange': 'L',  # Orange (Left)
    'white': 'U',  # White (Up)
    'blue': 'B',  # Blue (Back)
    'red': 'R',  # Red (Right)
}
color_map_drawing = {
    'D': '[y]',  # Yellow (Down)
    'F': '[g]',  # Green (Front)
    'L': '[o]',  # Orange (Left)
    'U': '[w]',  # White (Up)
    'B': '[b]',  # Blue (Back)
    'R': '[r]',  # Red (Right)
}


threshold_list = [(math.ceil(min_confidence * 255), 255)]

def fomo_post_process(model, inputs, outputs):
    ob, oh, ow, oc = model.output_shape[0]
    x_scale = inputs[0].roi[2] / ow
    y_scale = inputs[0].roi[3] / oh
    scale = min(x_scale, y_scale)
    x_offset = ((inputs[0].roi[2] - (ow * scale)) / 2) + inputs[0].roi[0]
    y_offset = ((inputs[0].roi[3] - (ow * scale)) / 2) + inputs[0].roi[1]
    l = [[] for i in range(oc)]

    for i in range(oc):
        img = image.Image(outputs[0][0, :, :, i] * 255)
        blobs = img.find_blobs(threshold_list, area_threshold=1, pixels_threshold=1)
        for b in blobs:
            x, y, w, h = b.rect()
            score = img.get_statistics(thresholds=threshold_list, roi=b.rect()).l_mean() / 255.0
            x = int((x * scale) + x_offset)
            y = int((y * scale) + y_offset)
            w = int(w * scale)
            h = int(h * scale)
            l[i].append((x, y, w, h, score))
    return l

def assign_positions(centers):
    sorted_y = sorted(centers, key=lambda p: p[1])
    rows = [sorted(sorted_y[i*3:(i+1)*3], key=lambda p: p[0]) for i in range(3)]
    pos_map = {}
    idx = 0
    for row in rows:
        for pt in row:
            pos_map[position_names[idx]] = pt
            idx += 1
    return pos_map

def print_face_3x3(pos_map):
    print("\n Rubik's Cube Face (Detected Colors):")
    print("┌────────┬────────┬────────┐")
    print("│ {:^6} │ {:^6} │ {:^6} │".format(
        pos_map["top_left_corner"], pos_map["middle_top"], pos_map["top_right_corner"]))
    print("├────────┼────────┼────────┤")
    print("│ {:^6} │ {:^6} │ {:^6} │".format(
        pos_map["middle_left"], pos_map["center"], pos_map["middle_right"]))
    print("├────────┼────────┼────────┤")
    print("│ {:^6} │ {:^6} │ {:^6} │".format(
        pos_map["bottom_left_corner"], pos_map["middle_bottom"], pos_map["bottom_right_corner"]))
    print("└────────┴────────┴────────┘")
    print("🔍 Per Position:")
    for k in position_names:
        print(f"{k:>18}: {pos_map[k]}")

def cube_stickers(layout_str):
    # Convert the string to a list of colors using the color map
    layout = [color_map_drawing[ch] for ch in layout_str]
    layout = ''.join(layout)
    cube_faces = {
    'U': layout[0:3*9],  # Up
    'R': layout[3*9:3*18],  # Right
    'F': layout[3*18:3*27],  # Front
    'D': layout[3*27:3*36],   # Down
    'L': layout[3*36:3*45], # Left
    'B': layout[3*45:3*54]  # Back
}
    print("Converted layout:", cube_faces)
    return cube_faces

def cube_layout(layout_str):
    cube_str=cube_stickers(layout_str)
    # print(cube_str['D'])

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
            str_output += cube_str['L'][side_size*j:side_size*j+side_size] + cube_str['F'][side_size*j:side_size*j+side_size] + cube_str['R'][side_size*j:side_size*j+side_size] + cube_str['B'][side_size*j:side_size*j+side_size] + '\n'

    for j in range (0, num_layers):
        for i in range(0, side_size):
            str_output += ' '
        for i in range(0, side_size, 9):
            str_output += cube_str['D'][side_size*j:side_size*j+side_size] + '\n'

    return str_output

faces_done = []
cube_map = {}

face_map = {}

max_faces = 6
face_idx = 0

while face_idx < max_faces:
    face_map = {}

    print("📸 Present side {} of 6 and hold steady...".format(face_idx + 1))
    time.sleep(2)

    while len(face_map) < 9:
        print("📸 Scanning face {}… Detected {} positions.".format(face_idx + 1, len(face_map)))
        img = sensor.snapshot()
        all_centers = []
        all_boxes = []

        for class_idx, detection_list in enumerate(net_square.predict([img], callback=fomo_post_process)):
            if class_idx == 0: continue
            for x, y, w, h, score in detection_list:
                cx = int(x + w / 2)
                cy = int(y + h / 2)
                all_centers.append((cx, cy))
                all_boxes.append((x, y, w, h, class_idx))
                img.draw_circle((cx, cy, 8), color=colors[class_idx % len(colors)])

        if len(all_centers) < 9:
            continue

        try:
            pos_map = assign_positions(all_centers)
        except:
            print("Could not assign positions. Skipping frame.")
            continue

        for label, (cx, cy) in pos_map.items():
            if label in face_map:
                continue

            for (x, y, w, h, class_id) in all_boxes:
                if abs((x + w // 2) - cx) < 5 and abs((y + h // 2) - cy) < 5:
                    stats = img.get_statistics(roi=(x, y, w, h))
                    pred_label = classify_color(stats)

                    if label == "center":
                        if face_idx == 0:
                            pred_label = "white"
                            center_color = pred_label
                            face_map[label] = pred_label
                        else:
                            center_color = pred_label

                    if pred_label == "?" or pred_label == "":
                        print("LAB Failed, for LAB:",stats.l_mean(), stats.a_mean(), stats.b_mean())
                        print("XXXX Skipping {}, uncertain color.".format(label))
                        continue

                    print("LAB: ",stats.l_mean(), stats.a_mean(), stats.b_mean())
                    face_map[label] = pred_label
                    img.draw_string(cx, cy, "{}:{}".format(label, pred_label), color=(255, 255, 255), scale=1)
                    print("✅ Updated {} as {}".format(label, pred_label))
                    break

    # Save the face based on center
    center_color = face_map["center"]
    if center_color in faces_done:
        print("⚠️ Face with center color '{}' already saved. Try a different one.".format(center_color))
    else:
        faces_done.append(center_color)
        cube_map[center_color] = face_map.copy()
        filename = "side_{}.jpg".format(face_idx + 1)
        img.save(filename)
        print("📸 Saved {} with center color '{}'".format(filename, center_color))
        print_face_3x3(face_map)
        face_idx += 1
        time.sleep(2)

# Final Step: Reorder cube and build string
print("✅ All 6 sides scanned.")
time.sleep(1)

new_order = ['white', 'red', 'green', 'yellow', 'orange', 'blue']
reordered_cube_map = OrderedDict()
for color in new_order:
    reordered_cube_map[color] = cube_map[color]

print("reordered_cube_map: ",reordered_cube_map)

time.sleep(2)
string_cube = ""
for color, face_map in reordered_cube_map.items():
    print(string_cube)
    string_cube += face_map['top_left_corner']
    print(string_cube)
    string_cube += face_map['middle_top']
    print(string_cube)
    string_cube += face_map['top_right_corner']
    print(string_cube)
    string_cube += face_map['middle_left']
    print(string_cube)
    string_cube += color
    print(string_cube)
    string_cube += face_map['middle_right']
    print(string_cube)
    string_cube += face_map['bottom_left_corner']
    print(string_cube)
    string_cube += face_map['middle_bottom']
    print(string_cube)
    string_cube += face_map['bottom_right_corner']

time.sleep(2)
pattern = '|'.join(color_map.keys())
output_string = re.sub(pattern, lambda m: color_map[m.group(0)], string_cube)

print("Cube string:", output_string)

print("Cube layout:")
print(cube_layout(output_string))


