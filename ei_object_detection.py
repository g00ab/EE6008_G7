import sensor, image, time, ml, math, uos, gc

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_windowing((240, 240))
sensor.skip_frames(time=2000)

net = None
labels = None
min_confidence = 0.5

try:
    net = ml.Model("trained.tflite", load_to_fb=uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024)))
except Exception as e:
    raise Exception('Failed to load "trained.tflite": ' + str(e))

try:
    labels = [line.rstrip('\n') for line in open("labels.txt")]
except Exception as e:
    raise Exception('Failed to load "labels.txt": ' + str(e))

colors = [
    (255, 0, 0),
    (0, 255, 0),
    (255, 255, 0),
    (0, 0, 255),
    (255, 0, 255),
    (0, 255, 255),
    (255, 255, 255),
]

position_names = [
    "top_left_corner", "middle_top", "top_right_corner",
    "middle_left", "center", "middle_right",
    "bottom_left_corner", "middle_bottom", "bottom_right_corner"
]

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
            rect = b.rect()
            x, y, w, h = rect
            score = img.get_statistics(thresholds=threshold_list, roi=rect).l_mean() / 255.0
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

def classify_color(stats):
    l = stats.l_mean()
    a = stats.a_mean()
    b = stats.b_mean()
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

for i in range(6):
    print("📸 Position the cube for side", i+1)
    time.sleep(5)  # wait 5 seconds

    img = sensor.snapshot()
    all_centers = []
    all_boxes = []

    for j, detection_list in enumerate(net.predict([img], callback=fomo_post_process)):
        if j == 0: continue
        for x, y, w, h, score in detection_list:
            cx = math.floor(x + w / 2)
            cy = math.floor(y + h / 2)
            all_centers.append((cx, cy))
            all_boxes.append((x, y, w, h, j))
            img.draw_circle((cx, cy, 8), color=colors[j])

    if len(all_centers) == 9:
        position_map = assign_positions(all_centers)
        for label, (cx, cy) in position_map.items():
            for (x, y, w, h, class_id) in all_boxes:
                if abs((x + w // 2) - cx) < 5 and abs((y + h // 2) - cy) < 5:
                    roi = (x, y, w, h)
                    stats = img.get_statistics(roi=roi)
                    color_label = classify_color(stats)
                    img.draw_string(cx, cy, "{}:{}".format(label, color_label), color=(255, 255, 255), scale=1)
                    print("Side {} - {} = {}".format(i+1, label, color_label))
                    break

    filename = "side_{}.jpg".format(i+1)
    img.save(filename)
    print("✅ Saved", filename)

print("🎉 Done capturing all 6 sides!")
