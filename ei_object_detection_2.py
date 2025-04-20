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

    if l > 94 and abs(a) < 15 and abs(b) < 15:
        return "white"
    elif a > 35 and b > 20:
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

# --- Load color recognition model ---
net_color = None
color_labels = None
try:
    net_color = ml.Model("color_trained.tflite", load_to_fb=uos.stat('color_trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    raise Exception('Failed to load "color_trained.tflite": ' + str(e))

try:
    color_labels = [line.rstrip('\n') for line in open("color_labels.txt")]
except Exception as e:
    raise Exception('Failed to load "color_labels.txt": ' + str(e))

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

faces_done = []
cube_map = {}
square_list = []

while len(faces_done) < 6:
    print("\U0001F4F8 Ready to detect a new face...")
    time.sleep(2)

    img = sensor.snapshot()
    all_centers = []
    all_boxes = []

    for class_idx, detection_list in enumerate(net_square.predict([img], callback=fomo_post_process)):
        if class_idx == 0: continue
        for x, y, w, h, score in detection_list:
            cx = math.floor(x + w / 2)
            cy = math.floor(y + h / 2)
            all_centers.append((cx, cy))
            all_boxes.append((x, y, w, h, class_idx))
            img.draw_circle((cx, cy, 8), color=colors[class_idx % len(colors)])

    if len(all_centers) == 9:
        pos_map = assign_positions(all_centers)
        center_coords = pos_map["center"]
        center_color = None

        print("\U0001F50E LAB → CNN Color classification:")
        face_map = {}
        for label, (cx, cy) in pos_map.items():
            for (x, y, w, h, class_id) in all_boxes:
                if abs((x + w // 2) - cx) < 5 and abs((y + h // 2) - cy) < 5:
                    roi = (x, y, w, h)
                    stats = img.get_statistics(roi=roi)
                    pred_label = classify_color(stats)

                    # TODO: Implement a failsafe so that when a color is not recognized, it recaptures the image and tries again.
                    if pred_label == "?":
                        print("LAB failed, using CNN for LAB:",stats.l_mean(), stats.a_mean(), stats.b_mean())

                    else:
                        print("LAB succeeded, for LAB:",stats.l_mean(), stats.a_mean(), stats.b_mean())
                        confidence = 1.0  # Assume full confidence for LAB

                    if label == "center":
                        if len(faces_done) == 0:
                            center_color = "white"
                        else:
                            center_color = pred_label
                    img.draw_string(cx, cy, "{}:{}".format(label, pred_label), color=(255, 255, 255), scale=1)
                    print("{} @({}, {}) → {} ({:.2f})".format(label, cx, cy, pred_label, confidence))
                    face_map[label] = pred_label
                    break

        if center_color is not None:
            if center_color in faces_done:
                print("⚠️ Face with center color '{}' already captured. Rotate to a new face.".format(center_color))
                continue
            elif center_color == "?":
                print("⚠️ Unrecognized color at center. Please try again.")
                continue
            else:
                faces_done.append(center_color)
                cube_map[center_color] = face_map.copy()
                filename = "side_{}.jpg".format(len(faces_done))
                img.save(filename)
                print("✅ Captured and saved {} with center color '{}'".format(filename, center_color))

print("🎉 Done capturing all 6 sides!")
print("cube_map: ",cube_map)


time.sleep(2)
new_order = ['white', 'red', 'green', 'orange', 'blue', 'yellow']
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
