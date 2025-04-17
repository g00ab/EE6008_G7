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
    (255, 0, 0), (0, 255, 0), (255, 255, 0),
    (0, 0, 255), (255, 0, 255), (0, 255, 255),
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

def classify_color(stats):
    l = stats.l_mean()
    a = stats.a_mean()
    b = stats.b_mean()
    print("LAB values: L={}, A={}, B={}".format(l, a, b))

    if l > 180 and a < 128 and b < 128:
        return "white"
    elif a > 150 and b < 140:
        return "red"
    elif a < 130 and b > 160:
        return "yellow"
    elif a < 120 and b < 100:
        return "blue"
    elif a > 160 and b > 160:
        return "orange"
    elif a < 110 and b < 90 and l < 100:
        return "green"
    else:
        return "?"

prev_center_color = None
side_num = 1

while side_num <= 6:
    print("📸 Ready for side", side_num)
    img = sensor.snapshot()
    all_centers = []
    all_boxes = []

    # Run FOMO detection
    for class_idx, detection_list in enumerate(net.predict([img], callback=fomo_post_process)):
        if class_idx == 0: continue  # background
        for x, y, w, h, score in detection_list:
            cx = math.floor(x + w / 2)
            cy = math.floor(y + h / 2)
            all_centers.append((cx, cy))
            all_boxes.append((x, y, w, h, class_idx))
            img.draw_circle((cx, cy, 8), color=colors[class_idx % len(colors)])

    if len(all_centers) == 9:
        pos_map = assign_positions(all_centers)
        center_pt = pos_map.get("center", None)

        # Find the center square's color
        for (x, y, w, h, class_id) in all_boxes:
            if abs((x + w // 2) - center_pt[0]) < 5 and abs((y + h // 2) - center_pt[1]) < 5:
                stats = img.get_statistics(roi=(x, y, w, h))
                center_color = classify_color(stats)

                if center_color == prev_center_color:
                    print("⚠️ Same center color detected: {}. Waiting for a new face...".format(center_color))
                    break  # Wait for new face
                prev_center_color = center_color

                # Annotate colors and labels
                for label, (cx, cy) in pos_map.items():
                    for (x2, y2, w2, h2, class_id2) in all_boxes:
                        if abs((x2 + w2 // 2) - cx) < 5 and abs((y2 + h2 // 2) - cy) < 5:
                            roi = (x2, y2, w2, h2)
                            stats = img.get_statistics(roi=roi)
                            color_label = classify_color(stats)
                            img.draw_string(cx, cy, "{}:{}".format(label, color_label), color=(255, 255, 255), scale=1)
                            print("Side {} - {} = {}".format(side_num, label, color_label))
                            break

                filename = "side_{}.jpg".format(side_num)
                img.save(filename)
                print("✅ Saved", filename)
                print("🌀 Rotate the cube to the next side...\n")
                side_num += 1
                break
    else:
        print("❌ Detected only", len(all_centers), "squares. Waiting...")
    
    time.sleep_ms(500)  # Slow down polling a bit
