# Edge Impulse - OpenMV FOMO Object Detection Example
#
# This work is licensed under the MIT license.
# Copyright (c) 2013-2024 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE

import sensor, image, time, ml, math, uos, gc

# Initialize sensor
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)  # 320x240
sensor.skip_frames(time=2000)

# Load FOMO model
try:
    # load the model, alloc the model file on the heap if we have at least 64K free after loading
    net = ml.Model("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    raise Exception('Failed to load "trained.tflite", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')

try:
    labels = [line.rstrip('\n') for line in open("labels.txt")]
except Exception as e:
    raise Exception('Failed to load "labels.txt", did you copy the .tflite and labels.txt file onto the mass-storage device? (' + str(e) + ')')


clock = time.clock()

# Position label order
position_names = [
    "top_left_corner", "middle_top", "top_right_corner",
    "middle_left", "center", "middle_right",
    "bottom_left_corner", "middle_bottom", "bottom_right_corner"
]

# Assign 9 centers to position labels
def assign_positions(points):
    sorted_y = sorted(points, key=lambda p: p[1])
    rows = [sorted(sorted_y[i*3:(i+1)*3], key=lambda p: p[0]) for i in range(3)]
    pos_map = {}
    idx = 0
    for row in rows:
        for pt in row:
            pos_map[position_names[idx]] = pt
            idx += 1
    return pos_map

# Convert average LAB to color label
def classify_color(stats):
    l = stats.l_mean()
    a = stats.a_mean()
    b = stats.b_mean()

    # Thresholds need tuning based on your lighting/environment
    if a < 110 and b < 110:
        return "white"
    elif a > 140 and b < 120:
        return "red"
    elif a < 120 and b > 140:
        return "yellow"
    elif a < 110 and b < 90:
        return "blue"
    elif a > 150 and b > 150:
        return "orange"
    elif a < 100 and b < 80 and l < 70:
        return "green"
    else:
        return "?"

while True:
    clock.tick()
    img = sensor.snapshot()
    objects = net.detect(img, threshold=0.5, nms=0.3)

    boxes = []
    centers = []

    for obj in objects:
        rect = obj.rect()
        x, y, w, h = rect
        cx = x + w // 2
        cy = y + h // 2
        centers.append((cx, cy))
        boxes.append((x, y, w, h))
        img.draw_rectangle(rect, color=(255, 0, 0))
        img.draw_cross(cx, cy, color=(0, 255, 0))

    if len(centers) == 9:
        labels = assign_positions(centers)
        for label, (cx, cy) in labels.items():
            # Find matching bounding box
            for i, (x, y, w, h) in enumerate(boxes):
                if abs((x + w // 2) - cx) < 5 and abs((y + h // 2) - cy) < 5:
                    roi = (x, y, w, h)
                    stats = img.get_statistics(roi=roi)
                    color_label = classify_color(stats)
                    img.draw_string(cx, cy, "{}:{}".format(label, color_label), color=(255, 255, 0), mono_space=False)
                    break

    print("FPS:", clock.fps())
